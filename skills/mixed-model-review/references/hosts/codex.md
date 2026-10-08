# Native Codex dispatch

- Inspect the native agent tools and installed reviewer types in this session.
  Use the installed `codex-reviewer` when the spawn tool supports custom types.
  Its source is [agents/codex-reviewer.toml](../../agents/codex-reviewer.toml).
  Do not write persistent agent or model configuration during a review.
- Request a fresh context for every seat. Inline the trusted brief and captured
  work. Do not fork author reasoning, suspected findings, or another seat's output
  into a first-round reviewer. Use the actual spawn schema; field names vary by host.
- Inherit the configured model and effort by default. If the user requests a
  model or effort, use only settings accepted by the current native tool.
  This native route targets GPT models. Do not request Claude through the native
  spawn tool or call T3 tools. Use the terminal route for an external CLI.
- A model may be the same as the author or chair. Label this as a separate-context
  review using the same model. Do not call it cross-model or cross-vendor review.
  Report unknown model provenance. More lenses do not prove model diversity.
- The packaged reviewer requests `sandbox_mode = "read-only"`. Parent runtime
  overrides can change the effective policy. A read-only filesystem does not block
  every MCP or external action. Keep the review-only instructions in every brief.
  If the effective policy is not verified, require packet-only analysis with no
  tool execution. Do not claim a verified read-only sandbox from a prompt alone.
- For the default terminal route, Codex's command sandbox can hide Claude Code's
  login and block network calls. Request escalated permissions for the runner's
  probe and run commands as the terminal guide describes; do not report Claude as
  logged out from a sandboxed probe alone.
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
