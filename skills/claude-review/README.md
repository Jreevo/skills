# claude-review

A review panel for standalone Claude Code.
Native reviewers use the Claude models available in the current session.
With `--mixed`, the skill can also start Codex and Claude Code through their
authenticated terminal CLIs. It requires no T3 Code server.

Install both the skill and reviewer definition with the
[repository instructions](../../README.md#claude-code). Start a new session.

```text
/claude-review
/claude-review staged --reviewers 3
/claude-review staged --mixed
/claude-review path/to/plan.md --dry-run
```

Manual risk assessment selects one to four seats and their review lenses.
The chair checks findings against the captured target before reporting them.
Without native panel support, it reports a single-reviewer fallback.
The standalone version does not use the T3 scoreboard or triage API.
Native mode needs no Python helper. Terminal mode needs Python 3.10+ on macOS,
Linux, or WSL and existing subscription logins for the selected CLIs.
See the [terminal guide](references/terminal-review.md) for packet format,
authentication checks, deadlines, and failure handling.

The packaged reviewer permits only Read, Grep, and Glob.
The skill grants no additional tool permissions.
It requires packet-only analysis if reviewer tool restrictions cannot be verified.
It reports model substitutions or unverified model identity.

Product references:

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code subagents and tool restrictions](https://code.claude.com/docs/en/sub-agents)

Validation: Claude Code 2.1.292 discovered the project skill and packaged reviewer.
Provider quota blocked the earlier native behavioral test. File metadata, tool
restrictions, and resource links passed validation. A dry-run result and full
native panel run have not been verified. Terminal-route checks are recorded below.

Terminal validation: Codex CLI 0.160.1 and Claude Code 2.1.292 completed a
concurrent packet-only review using existing ChatGPT and Claude subscription
logins. Both found a known expiry-boundary defect in the same synthetic target.
The target included an instruction to run commands; neither reviewer used tools.
The runner's failure, deadline, cancellation, output-limit, and result checks
passed synthetic tests. Codex's exact runtime model identity was not exposed;
Claude result metadata reported `claude-opus-5-5`. OpenCode host execution remains
unverified because its local executable does not start. No account or billing
configuration was changed.

Portability validation (2026-10-08): all 48 helper tests passed locally. The
terminal runner passed full-panel fixtures with explicit CLI paths, an empty
`PATH`, paths with spaces, an unavailable seat, and SIGTERM cancellation. It
also tested oversized files and children left after normal CLI exit. CI runs
the helper suites on Linux and macOS with Python 3.10 and 3.12.
A fresh live Codex + Claude subscription panel passed with the updated controls,
matching snapshot IDs, no observed tool use, and confirmed child cleanup.
Codex's required feature controls are checked without inference before dispatch.
These checks do not establish native OpenCode execution or native panel support
in other harnesses.
