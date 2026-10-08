# codex-review

A native review panel for standalone Codex.
Reviewers use GPT models available in the current session.
They inherit the configured model and effort by default.
This skill does not call Claude or require T3 Code.

Install both the skill and reviewer definition with the
[repository instructions](../../README.md#codex). Start a new session.

```text
Use $codex-review to review the current diff.
Use $codex-review staged --reviewers 3
Use $codex-review path/to/plan.md --dry-run
```

Manual risk assessment selects one to four seats and their review lenses.
The chair checks findings against the captured target before reporting them.
Without native panel support, it reports a single-reviewer fallback.
The standalone version does not use the T3 scoreboard or triage API.

The reviewer definition requests a read-only filesystem.
Session overrides can affect that policy. Filesystem restrictions do not block
all external tools. The skill requires packet-only analysis if the effective
reviewer policy cannot be verified.
If the host cannot select a custom reviewer type, it can use available native
agents for packet-only review and reports that the packaged configuration was not applied.

Product references:

- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex subagents and custom agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents)

Validation: Codex CLI 0.160.1 loaded the project skill and completed a dry-run
on a synthetic billing-status plan. It selected Heavy risk and three planned
seats, started no reviewers, and ignored an instruction embedded in the target
to start T3 tasks. A full native panel run has not been verified.
