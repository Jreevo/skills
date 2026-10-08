# codex-review

A review panel for standalone Codex.
Native reviewers use the GPT models available in the current session.
With `--mixed`, the skill can also start Claude Code and Codex through their
authenticated terminal CLIs. It requires no T3 Code server.

Install both the skill and reviewer definition with the
[repository instructions](../../README.md#codex). Start a new session.

```text
Use $codex-review to review the current diff.
Use $codex-review staged --reviewers 3
Use $codex-review staged --mixed
Use $codex-review path/to/plan.md --dry-run
```

Manual risk assessment selects one to four seats and their review lenses.
The chair checks findings against the captured target before reporting them.
Without native panel support, it reports a single-reviewer fallback.
The standalone version does not use the T3 scoreboard or triage API.
Native mode needs no Python helper. Terminal mode needs Python 3.10+ on macOS,
Linux, or WSL and existing subscription logins for the selected CLIs.
See the [terminal guide](references/terminal-review.md) for packet format,
authentication checks, deadlines, and failure handling.

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

Terminal validation: Codex CLI 0.160.1 and Claude Code 2.1.292 completed a
concurrent packet-only review using existing ChatGPT and Claude subscription
logins. Both found a known expiry-boundary defect in the same synthetic target.
The target included an instruction to run commands; neither reviewer used tools.
The runner's failure, deadline, cancellation, output-limit, and result checks
passed synthetic tests. Codex's exact runtime model identity was not exposed;
Claude result metadata reported `claude-opus-5-5`. OpenCode host execution remains
unverified because its local executable does not start. No account or billing
configuration was changed.
