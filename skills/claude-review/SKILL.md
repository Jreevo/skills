---
name: claude-review
description: Review code, plans, or copy in Claude Code with native agents or a mixed-provider panel through authenticated Claude Code and Codex terminal sessions. No T3 Code server is required.
---

# Claude Code review

Act as the review chair in the main conversation.
Use native Claude Code agents for separate review contexts.
Read [the review workflow](references/review-workflow.md) for target capture,
manual risk assessment, reviewer briefs, and verification.

## Arguments

```text
/claude-review [target] [--mixed] [--reviewers N] [--round2] [--dry-run] [--timeout-seconds N]
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
start fresh packet-only Claude Code and Codex sessions with existing local
subscription logins. This is separate from native Claude subagent delegation.
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

## Native Claude Code dispatch

- Inspect the native Agent tool and available subagent types in this session.
  Prefer the installed `claude-reviewer`. Its definition is
  [agents/claude-reviewer.md](agents/claude-reviewer.md).
  It limits tools to Read, Grep, and Glob and inherits the session model.
  Do not write persistent agent or model configuration during a review.
- Request a fresh context for every seat. Include the complete trusted brief and
  captured work. Do not assume that a subagent inherits the user's decisions or
  chat history. Do not send another seat's findings in a first-round prompt.
- Specify the available `subagent_type` explicitly. Use only fields supported by
  the current Agent schema. Inherit the configured model by default.
  If the user requests a model, use only supported Claude aliases or IDs allowed
  in the session. Do not request GPT through the native Agent tool or call T3
  tools. Use the terminal route above for an external CLI. Do not change global
  model or effort settings.
- Runtime model substitution is possible. Record the actual model if task
  metadata exposes it. Otherwise report requested/inherited model and **actual
  model unverified**. If all seats use one model, label the panel accordingly.
  Separate contexts and lenses do not prove model or vendor diversity.
- Verify the selected agent's tool restrictions when possible. A skill's
  `allowed-tools` field grants permission; it is not a restrictive tool allowlist.
  Do not treat plan mode as proof of a strict read-only sandbox. If the selected
  agent's restrictions are not verified, require packet-only analysis with no
  tool execution. Keep the review-only instructions in every brief.
- Use background tasks only when the session exposes task IDs, result retrieval,
  and cancellation. Save each ID. Use bounded result waits and the supported stop
  tool at a seat deadline. A wait timeout does not cancel a running agent.
  If only foreground calls are available, run seats sequentially and disclose
  that the host cannot enforce the requested deadline. Do not invent cancellation.
- For `--round2`, start a fresh Agent task with the original packet, findings,
  responses, and disputed points. Use the remaining seat budget. Do not start a
  rebuttal for an unresolved live seat. Rebuttal does not add an independent vote.
- If the custom reviewer is missing, an available built-in Explore agent can
  provide read-only code exploration. Check its actual restrictions and model;
  do not assume its default model. Use the complete inline packet for plans/copy.
  If no suitable native agent is available, perform one chair review and label
  it **single-reviewer fallback; native panel unavailable**. Do not simulate a panel.

Print the risk tier, requested seats, lenses, inherited/requested model settings,
permission limits, and wait budget before dispatch. `--dry-run` ends here.
