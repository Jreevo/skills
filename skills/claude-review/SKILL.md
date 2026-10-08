---
name: claude-review
description: Review code, plans, or copy in standalone Claude Code with native Claude reviewer agents. Use for a requested review panel without T3 Code or GPT delegation.
---

# Claude Code review

Act as the review chair in the main conversation.
Use native Claude Code agents for separate review contexts.
Read [the review workflow](references/review-workflow.md) for target capture,
manual risk assessment, reviewer briefs, and verification.

## Arguments

```text
/claude-review [target] [--reviewers N] [--round2] [--dry-run] [--timeout-seconds N]
```

Target can be a path, PR, `staged`, branch, or document.
Default to the uncommitted diff, then the last produced work if no diff exists.
`--reviewers` accepts 1 to 4. It changes the seat count, not the risk tier.
`--round2` permits one rebuttal round for disputed findings.
`--dry-run` captures and assesses the work without starting agents or calling an API.
`--timeout-seconds` is the budget per seat, including rebuttal, default 600,
range 1 to 3600. State any limit on enforcing this budget.

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
  in the session. Do not request GPT models, call T3 tools, or start another CLI
  or API as a substitute. Do not change global model or effort settings.
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
