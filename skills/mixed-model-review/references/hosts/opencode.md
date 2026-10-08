# Native OpenCode dispatch

- Inspect the current tool schema and available subagent catalog. V1 uses the
  native Task tool; V2 uses `subagent`. Do not mix their arguments. Do not call
  T3 tools or a separate API to fill a seat. Use the terminal route for external CLIs.
- Prefer the installed `opencode-reviewer`. Install exactly one version of its
  definition as described in [the guide](../../README.md#opencode):
  [V1](../../agents/opencode/v1/opencode-reviewer.md) or
  [V2](../../agents/opencode/v2/opencode-reviewer.md).
  V1 uses `permission`; V2 uses `permissions`. Do not write persistent agent,
  provider, model, or permission configuration during a review.
- Each seat needs a new child session. Supply the full trusted brief and captured
  target with a distinct lens. Do not assume that a child inherits user decisions
  or conversation history. Do not reuse a returned child/session ID for another
  seat or seed first-round prompts with another reviewer's findings.
- The packaged reviewer omits `model` and inherits the parent model. A provider
  being configured does not prove quota, health, or a successful model call.
  Report the actual model when runtime metadata verifies it. Otherwise report
  the inherited/requested model and **actual model unverified**.
- If the user requests other models, use already-configured reviewer agents
  with verified review-only permissions and eligible models. Do not invent a
  per-task model parameter. Check the live catalog; OpenCode model IDs use
  `provider/model`. V2 variants use `#variant` only when the catalog supports it.
  Do not rewrite configuration or switch accounts to create model diversity.
  If the requested model cannot be selected, report the missing seat.
- The packaged policies deny tools by default, then allow local Read, Glob, Grep
  and, for V1, List. They deny shell execution, edits, nested delegation, external
  directory access, and unlisted MCP tools. Verify the effective policy before
  permitting tools. A matching file name or Plan agent alone is not proof that
  the restrictions applied. If policy is unverified, require packet-only analysis
  with no tool execution. Inline material that is outside the permitted directory.
- Use foreground calls unless the host exposes background result retrieval,
  state inspection, and cancellation. Foreground calls may require sequential
  seats and may not support a hard timeout. Disclose these limits before dispatch.
  Never assume a background completion notification is a cancellation mechanism.
  Save returned task/session IDs. Do not confuse a wait timeout with completion.
- For `--round2`, create fresh child sessions with the original brief, snapshot,
  findings, responses, and disputed points. Use each seat's remaining budget.
  Do not start a rebuttal for an unresolved live seat. A second round adds no vote.
- If the installed reviewer is unavailable, a verified suitable native agent
  can review the inline packet. If no native reviewer is available, perform one
  chair review and label it **single-reviewer fallback; native panel unavailable**.
  Do not simulate completed reviewers or loosen permissions to fill the panel.
