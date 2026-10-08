---
name: codex-review
description: Review code, plans, or copy in Codex with native agents or a mixed-provider panel through authenticated Codex and Claude Code terminal sessions. No T3 Code server is required.
---

# Codex review

Act as the review chair. Use native Codex agents for separate review contexts.
Read [the review workflow](references/review-workflow.md) for target capture,
manual risk assessment, reviewer briefs, and verification.

## Arguments

```text
Use $codex-review [target] [--mixed] [--reviewers N] [--round2] [--dry-run] [--timeout-seconds N]
```

Target can be a path, PR, `staged`, branch, or document.
Default to the uncommitted diff, then the last produced work if no diff exists.
`--reviewers` accepts 1 to 4. It changes the seat count, not the risk tier.
`--round2` permits one rebuttal round for disputed findings.
`--dry-run` captures and assesses the work without starting agents or calling an API.
`--timeout-seconds` is the budget per seat, including rebuttal, default 600,
range 1 to 3600. State any limit on enforcing this budget.

## Mixed-provider terminal route

When the user requests mixed-model review or passes `--mixed`, read
[the terminal guide](references/terminal-review.md). Use the packaged runner to
start fresh packet-only Codex and Claude Code sessions with existing local
subscription logins. This is separate from native Codex subagent delegation.
Probe available logins without requesting or copying tokens. Print the panel
before dispatch. Respect explicit model/provider choices and the assessed seat count.
Do not replace a failed subscription seat with an API-key route.
If a mixed-provider panel is unavailable, state the gap before using a native
panel or a single-reviewer fallback. Do not claim model diversity from one model.
Python 3.10+ and a POSIX host are required only for this terminal route.

Probe CLI versions and eligible logins before terminal dispatch. Use absolute
CLI paths if the host has an incomplete `PATH`. Save the run ID and private
artifact path. Recover a lost response from that run's status files before
starting another panel. A missing seat or unconfirmed cleanup is incomplete.
Do not remove safety flags to support an older CLI.

## Native Codex dispatch

- Inspect the native agent tools and installed reviewer types in this session.
  Use the installed `codex-reviewer` when the spawn tool supports custom types.
  Its source is [agents/codex-reviewer.toml](agents/codex-reviewer.toml).
  Do not write persistent agent or model configuration during a review.
- Request a fresh context for every seat. Inline the trusted brief and captured
  work. Do not fork author reasoning, suspected findings, or another seat's output
  into a first-round reviewer. Use the actual spawn schema; field names vary by host.
- Inherit the configured model and effort by default. If the user requests a
  model or effort, use only settings accepted by the current native tool.
  This native route targets GPT models. Do not request Claude through the native
  spawn tool or call T3 tools. Use the terminal route above for an external CLI.
- A model may be the same as the author or chair. Label this as a separate-context
  review using the same model. Do not call it cross-model or cross-vendor review.
  Report unknown model provenance. More lenses do not prove model diversity.
- The packaged reviewer requests `sandbox_mode = "read-only"`. Parent runtime
  overrides can change the effective policy. A read-only filesystem does not block
  every MCP or external action. Keep the review-only instructions in every brief.
  If the effective policy is not verified, require packet-only analysis with no
  tool execution. Do not claim a verified read-only sandbox from a prompt alone.
- Retain each returned agent ID. Use native wait and result tools in bounded
  steps. A wait timeout is not completion or cancellation. At a seat deadline,
  inspect its state once, accept a completed result, or interrupt/close it using
  the supported tool. Report unknown state or unconfirmed cleanup.
- For `--round2`, start a fresh agent with the original packet, findings,
  responses, and disputed points. Use the remaining seat budget. Do not start a
  rebuttal for an unresolved live seat. Rebuttal does not add an independent vote.
- If the spawn tool cannot select a custom reviewer type, use an available native
  agent with the complete inline packet and require no tool execution. Report
  that the packaged reviewer configuration was not applied. Missing custom-type
  support alone is not a reason to discard an available native panel.
- When native agent tools are unavailable, perform one
  chair review and label it **single-reviewer fallback; native panel unavailable**.
  Do not simulate multiple completed reviewers or silently widen permissions.

Print the risk tier, requested seats, lenses, inherited/requested model settings,
permission limits, and wait budget before dispatch. `--dry-run` ends here.
