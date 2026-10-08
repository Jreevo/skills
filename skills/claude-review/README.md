# claude-review

A native review panel for standalone Claude Code.
Reviewers use Claude models available in the current session.
They inherit the configured model by default.
This skill does not call GPT or require T3 Code.

Install both the skill and reviewer definition with the
[repository instructions](../../README.md#claude-code). Start a new session.

```text
/claude-review
/claude-review staged --reviewers 3
/claude-review path/to/plan.md --dry-run
```

Manual risk assessment selects one to four seats and their review lenses.
The chair checks findings against the captured target before reporting them.
Without native panel support, it reports a single-reviewer fallback.
The standalone version does not use the T3 scoreboard or triage API.

The packaged reviewer permits only Read, Grep, and Glob.
The skill grants no additional tool permissions.
It requires packet-only analysis if reviewer tool restrictions cannot be verified.
It reports model substitutions or unverified model identity.

Product references:

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code subagents and tool restrictions](https://code.claude.com/docs/en/sub-agents)

Validation: Claude Code 2.1.292 discovered the project skill and packaged reviewer.
Provider quota blocked the behavioral test. File metadata, tool restrictions, and
resource links passed validation. A dry-run result and full native panel run have
not been verified.
