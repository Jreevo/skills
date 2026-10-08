---
name: mixed-model-review
description: Review code, plans, or copy in Codex, Claude Code, or OpenCode with a mixed-provider panel of authenticated Codex and Claude Code reviewers by default, or a same-host native panel with --native. No T3 Code server is required.
---

# Mixed-model review

Act as the review chair in the main session. By default, assemble a mixed-provider
panel so Codex and Claude models review the same work. Use the active host's
native agents for a same-host panel only with `--native` or as a disclosed fallback.
Read [the review workflow](references/review-workflow.md) for target capture,
manual risk assessment, reviewer briefs, and verification.

## Arguments

```text
mixed-model-review [target] [--native] [--terminal] [--reviewers N] [--round2] [--dry-run] [--timeout-seconds N]
```

Invoke it as `$mixed-model-review` in Codex, `/mixed-model-review` in Claude Code,
or "Use the mixed-model-review skill" in OpenCode.
Target can be a path, PR, `staged`, branch, or document.
Default to the uncommitted diff, then the last produced work if no diff exists.
`--reviewers` accepts 1 to 4. It changes the seat count, not the risk tier.
A mixed-provider panel is the default; `--mixed` is accepted and changes nothing.
`--native` opts out and uses only the active host's native agents.
`--terminal` forces the CLI route, including in OpenCode.
`--round2` permits one rebuttal round for disputed findings.
`--dry-run` captures and assesses the work without starting reviewers or calling
a separate triage API. Ordinary chair inference still uses the selected provider.
`--timeout-seconds` is the budget per seat, including rebuttal, default 600,
range 1 to 3600. State any limit on enforcing this budget.

## Identify the host

Identify the host from the native tools in this session, not from its name.
Then read only the matching dispatch guide. It covers native seats, which the
default mixed route can use in OpenCode and which `--native` and fallbacks use:

| Native tool surface | Host | Guide |
| --- | --- | --- |
| Codex agent spawn, wait, and close tools | Codex | [hosts/codex.md](references/hosts/codex.md) |
| Claude Code `Agent` tool with `subagent_type` | Claude Code | [hosts/claude-code.md](references/hosts/claude-code.md) |
| OpenCode `Task` (V1) or `subagent` (V2) tool | OpenCode | [hosts/opencode.md](references/hosts/opencode.md) |

Do not translate one host's agent fields into another's by guess.
If no native agent tool is recognized, the terminal route still works when the
host can start, inspect, and cancel local processes. Otherwise perform one chair
review and label it **single-reviewer fallback; mixed and native panels unavailable**.

## Default mixed-provider panel

Use this route unless the user passes `--native`. In OpenCode, first prefer
already-configured native reviewer agents with distinct eligible models from
different providers and verified review-only permissions; `--terminal` skips them.
Otherwise read [the terminal guide](references/terminal-review.md). Use the packaged runner
to start fresh packet-only Codex and Claude Code sessions with existing local
subscription logins. This is separate from native subagent delegation, and those
accounts do not need to be connected to the host's provider settings.
Probe available logins without requesting or copying tokens. Print the selected
route and panel before dispatch. Respect explicit model/provider choices and the
assessed seat count. Do not replace a failed subscription seat with an API-key route.
A mixed panel needs at least two seats, one per provider. Raise a one-seat
assessment to two seats unless the user explicitly passed `--reviewers 1`; label
that single seat as not mixed. Above two seats, alternate providers by lens order.
If one provider is unavailable, state the gap and continue with the remaining seats labeled
**same-provider panel; mixed panel unavailable**. If neither CLI is ready, state
the reason and fall back to the native panel for the host. Do not claim model
diversity from one model. Python 3.10+ and a POSIX host are required only for
this terminal route.

Probe CLI versions and eligible logins before terminal dispatch. If the chair's
commands run in a sandbox, a failed login check is unverified; request approval
to run the runner outside the sandbox as the terminal guide describes. Use absolute
CLI paths if the host has an incomplete `PATH`. Save the run ID and private
artifact path. Recover a lost response from that run's status files before
starting another panel. A missing seat or unconfirmed cleanup is incomplete.
Do not remove safety flags to support an older CLI.

## Before dispatch

Print the host, risk tier, planned seats and lenses, selected agents or CLIs,
inherited/requested model settings, permission limits, and wait budget.
`--dry-run` ends here.
