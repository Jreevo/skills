#!/usr/bin/env python3
"""t3-review triage: ask OpenAI's Decisions API (gpt-6-luna) to size the review panel.

Usage: python3 -I triage.py <packet.md>
Prints one JSON object. Exits non-zero on any failure so the caller falls back to manual triage.
API key is read from macOS Keychain (service "t3-review-openai"), never from env or args.
"""
import json
import math
import argparse
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

MODEL = "gpt-6-luna"
MAX_INPUT_CHARS = 200_000  # ~50k tokens, ~$0.005 per call
FLAG_THRESHOLD = 0.35  # escalate when unsure: a 35% chance of touching money counts as touching money

PREDICATES = {
    "irreversible": "Would mistakes in this work be hard or impossible to undo once shipped, e.g. it deletes or rewrites production data, sends messages to real users, charges or refunds money, or publishes something permanently?",
    "money": "Does this work handle payments, billing, subscriptions, refunds or pricing logic?",
    "money_movement": "Does this work initiate or change the execution of real charges, refunds, payouts or transfers of money, rather than only display prices or subscription status?",
    "security_boundary": "Does this work handle secrets, API keys, encryption, untrusted user input reaching a database or shell, or any security-critical boundary?",
    "legal": "Does this work carry legal, compliance or privacy weight, e.g. personal data (PII), terms, consent, contracts, or regulated claims?",
    "auth": "Does this work touch authentication, sessions, roles, permissions or access control?",
    "data_migration": "Does this work include database schema migrations, data backfills, or bulk changes to stored records?",
    "concurrency": "Does this work involve background jobs, queues, webhooks, retries, caching invalidation, or race-condition-prone concurrent logic?",
    "public_contract": "Does this work change a public API, SDK, webhook payload, or any contract other systems or customers depend on?",
}
CRITICAL = {"irreversible", "money_movement", "security_boundary", "legal"}
HEAVY = {"money", "auth", "data_migration", "concurrency", "public_contract"}
TIERS = {"Light": 1, "Standard": 2, "Heavy": 3, "Critical": 4}
# Abstract effort ladder; SKILL.md maps each step to the nearest option a reviewer model actually offers.
EFFORT_LEVELS = [
    ("medium", "straightforward; problems would be visible on a careful read"),
    ("high", "some non-obvious logic or interactions between parts"),
    ("xhigh", "subtle logic, ordering, state or security reasoning"),
    ("max", "very subtle: novel algorithms, crypto, distributed correctness"),
]
# Risky tiers never get a shallower review than this, whatever the effort score says.
EFFORT_FLOOR = {"Light": 0, "Standard": 0, "Heavy": 1, "Critical": 2}
WORK_TYPES = {"code", "plan", "copy", "mixed"}


class TriageError(ValueError):
    """Invalid evidence must not produce a successful low-risk result."""


def validate_input(text):
    if not isinstance(text, str) or not text.strip():
        raise TriageError("The packet is empty.")
    if len(text) > MAX_INPUT_CHARS:
        raise TriageError(f"Packet has {len(text)} characters; limit is {MAX_INPUT_CHARS}. Split the work or use complete manual evidence.")


def number(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise TriageError(f"Invalid {name}; expected a finite number from {low} to {high}.")
    return value


def classify(resp):
    if not isinstance(resp, dict) or not isinstance(resp.get("answers"), list):
        raise TriageError("Missing answers list.")
    expected = {**{n: "predicate" for n in PREDICATES}, "size": "score", "effort": "score", "work_type": "choice"}
    answers = {}
    for answer in resp["answers"]:
        if not isinstance(answer, dict) or not isinstance(answer.get("name"), str):
            raise TriageError("Malformed answer.")
        name = answer["name"]
        if name not in expected:
            raise TriageError("Unknown answer name.")
        if name in answers:
            raise TriageError(f"Duplicate answer: {name}.")
        if answer.get("type") != expected[name]:
            raise TriageError(f"Missing, refused or invalid answer: {name}.")
        answers[name] = answer
    if set(answers) != set(expected):
        raise TriageError("Missing required answers: " + ", ".join(sorted(set(expected) - set(answers))))
    probs = {n: number(answers[n].get("probability"), 0, 1, n) for n in PREDICATES}
    size = number(answers["size"].get("score"), 0, 4, "size score")
    effort_score = number(answers["effort"].get("score"), 0, 3, "effort score")
    work_type = answers["work_type"].get("choice")
    if not isinstance(work_type, str) or work_type not in WORK_TYPES:
        raise TriageError("Invalid work_type choice.")
    flags = sorted(n for n, p in probs.items() if p >= FLAG_THRESHOLD)
    if set(flags) & CRITICAL:
        tier = "Critical"
    elif set(flags) & HEAVY or size >= 2.75:
        tier = "Heavy"
    elif not flags and size < 1.0 and work_type in {"code", "copy"}:
        tier = "Light"
    else:
        tier = "Standard"
    effort_idx = max(min(int(effort_score + 0.65), len(EFFORT_LEVELS) - 1), EFFORT_FLOOR[tier])
    return {"tier": tier, "reviewers": TIERS[tier], "effort": EFFORT_LEVELS[effort_idx][0],
            "effort_score": effort_score, "work_type": work_type, "size_score": size,
            "flags": flags, "probabilities": probs, "refused": []}


def api_key():
    key = subprocess.run(
        ["security", "find-generic-password", "-s", "t3-review-openai", "-w"],
        capture_output=True, text=True, check=True, timeout=10,
    ).stdout.strip()
    if not key or any(c.isspace() for c in key):
        raise TriageError("Keychain credential is empty or contains whitespace.")
    return key


def decide(text):
    validate_input(text)
    questions = [{"type": "predicate", "name": n, "instructions": i} for n, i in PREDICATES.items()]
    questions.append({
        "type": "choice", "name": "work_type",
        "instructions": "What kind of work is under review?",
        "choices": [
            {"value": "code", "description": "source code, diff, PR, config"},
            {"value": "plan", "description": "design doc, architecture, PRD, strategy"},
            {"value": "copy", "description": "marketing, UX or email text"},
            {"value": "mixed", "description": "substantial amounts of more than one of the above"},
        ],
    })
    questions.append({
        "type": "score", "name": "size",
        "instructions": "How large is the work under review?",
        "levels": [
            {"label": "tiny", "description": "under ~50 changed lines or a short paragraph"},
            {"label": "small", "description": "~50-200 lines or a one-page doc"},
            {"label": "medium", "description": "~200-800 lines or a multi-page doc"},
            {"label": "large", "description": "~800-2000 lines or a long spec"},
            {"label": "huge", "description": "over ~2000 lines"},
        ],
    })
    questions.append({
        "type": "score", "name": "effort",
        "instructions": "How much careful reasoning does a reviewer need to find the real problems in this work? Judge subtlety, not size: a short change can be subtle.",
        "levels": [{"label": l, "description": d} for l, d in EFFORT_LEVELS],
    })
    req = urllib.request.Request(
        "https://api.openai.com/v1/decisions",
        data=json.dumps({"model": MODEL, "input": text, "questions": questions}).encode(),
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", nargs="?")
    parser.add_argument("--manual", metavar="ANSWERS_JSON", help="Apply the same policy to manually assessed answers; no network or Keychain access.")
    parser.add_argument("--policy", action="store_true", help="Print the questions and policy; no network or Keychain access.")
    args = parser.parse_args()
    if args.policy:
        print(json.dumps({"predicates": PREDICATES, "threshold": FLAG_THRESHOLD,
            "critical": sorted(CRITICAL), "heavy": sorted(HEAVY), "size_heavy": 2.75,
            "light": "No risk flags, size < 1.0, and work_type code or copy. Plans and mixed work are at least Standard.",
            "effort_levels": EFFORT_LEVELS, "effort_floor": EFFORT_FLOOR,
            "answer_format": {"answers": [{"name": n, "type": "predicate", "probability": 0} for n in PREDICATES] +
                [{"name": "size", "type": "score", "score": 0}, {"name": "effort", "type": "score", "score": 0}, {"name": "work_type", "type": "choice", "choice": "code"}]}}, indent=2))
        return
    if not args.packet:
        parser.error("packet is required")
    text = Path(args.packet).read_text(encoding="utf-8")
    started = time.time()
    if args.manual:
        if not text.strip():
            raise TriageError("The packet is empty.")
        resp = json.loads(Path(args.manual).read_text(encoding="utf-8"))
    else:
        validate_input(text)
        resp = decide(text)
    result = classify(resp)
    usage = resp.get("usage")
    tokens = usage.get("input_tokens") if isinstance(usage, dict) else None
    tokens = tokens if type(tokens) is int and tokens >= 0 else None
    result.update({"source": "manual" if args.manual else "decision_model", "input_chars": len(text),
        "truncated": False, "input_tokens": tokens,
        "cost_usd": round(tokens * 0.10 / 1_000_000, 6) if tokens is not None else None,
        "cost_is_estimate": True, "latency_s": round(time.time() - started, 2)})
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        # Do not echo remote response bodies, packet text or credential values.
        detail = str(exc) if isinstance(exc, TriageError) else type(exc).__name__
        print("Triage unavailable: " + detail + " Use complete manual triage evidence.", file=sys.stderr)
        sys.exit(1)
