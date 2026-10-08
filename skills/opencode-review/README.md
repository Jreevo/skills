# opencode-review

A native review panel for standalone OpenCode.
It uses manual risk assessment and native subagents.
Native mode needs no T3 Code server, Python helper, or separate triage API key.
Ordinary model calls use your configured OpenCode provider and its usage limits.
The packaged reviewer inherits the parent session model.
Separate reviewer contexts do not prove model or provider diversity.

## Install

From a clone of `Jreevo/skills`, install the skill:

```sh
mkdir -p ~/.config/opencode/skills ~/.config/opencode/agents
cp -R skills/opencode-review ~/.config/opencode/skills/
```

Check your OpenCode version with `opencode --version`.
Install only the reviewer definition for your runtime.
Both definitions use the same installed agent name, `opencode-reviewer`.

### OpenCode V1

V1 uses `permission` mappings and the native Task tool:

```sh
cp skills/opencode-review/agents/v1/opencode-reviewer.md ~/.config/opencode/agents/opencode-reviewer.md
```

### OpenCode V2

V2 uses ordered `permissions` rules and the native `subagent` tool:

```sh
cp skills/opencode-review/agents/v2/opencode-reviewer.md ~/.config/opencode/agents/opencode-reviewer.md
```

For project installation, use `.opencode/skills` and `.opencode/agents` instead
of the global directories. Do not install both reviewer versions as active agents.
Start a new OpenCode session after installing.

## Use

Ask OpenCode to load the skill and review the target:

```text
Use the opencode-review skill to review the current diff.
Use the opencode-review skill for staged changes --reviewers 3.
Use the opencode-review skill for staged changes --mixed.
Use the opencode-review skill for staged changes --terminal.
Use the opencode-review skill for path/to/plan.md --dry-run.
```

`--dry-run` assesses risk and plans seats without dispatching subagents.
Use the skill name in a normal prompt. Installing a skill alone does not create
a custom `/opencode-review` command.

The reviewer policies allow local read/search tools and deny other tools by default.
Verify the effective policy when other configuration overrides the same agent.
These are tool permission policies, not an operating system sandbox.
If restrictions cannot be verified, the skill requires packet-only analysis.
It reports a single-reviewer fallback if native delegation is unavailable.

## Models

OpenCode can use models from configured providers, including GPT and Claude when
those providers and models are available. The packaged reviewer leaves `model`
unset and uses the parent session model for every seat.

To request a different model, select an already-configured reviewer agent with
the requested `provider/model` and equivalent review-only permissions.
V2 supports catalog-defined `#variant` suffixes. The skill does not create
provider credentials or modify model configuration during a review.

## Existing CLI subscriptions

OpenCode can also launch authenticated Codex and Claude Code sessions through
the terminal runner. `--terminal` selects this route. `--mixed` prefers configured
native model agents, then uses eligible terminal reviewers when needed.
Those subscriptions do not need to be imported into OpenCode's provider settings.
Each CLI keeps its own login and usage limits.
This route needs Python 3.10+ on macOS, Linux, or WSL. It needs no separate triage
API key. See the [terminal guide](references/terminal-review.md).

## Validation

The skill metadata, references, and both reviewer policies were checked against
the official V1 and V2 documentation. The local executable exited with code 137
for `opencode --version`. Native skill discovery, dry-run behavior, and a full
panel run have not been verified in OpenCode.

Product references:

- [V1 skills](https://opencode.ai/docs/skills/)
- [V1 agents](https://opencode.ai/docs/agents/)
- [V1 permissions](https://opencode.ai/docs/permissions/)
- [V2 skills](https://opencode.ai/v2/docs/skills)
- [V2 agents](https://opencode.ai/v2/docs/agents)
- [V2 permissions](https://opencode.ai/v2/docs/permissions)
- [V2 models](https://opencode.ai/v2/docs/models)

Terminal validation: Codex CLI 0.160.1 and Claude Code 2.1.292 completed a
concurrent packet-only review using existing ChatGPT and Claude subscription
logins. Both found a known expiry-boundary defect in the same synthetic target.
The target included an instruction to run commands; neither reviewer used tools.
The runner's failure, deadline, cancellation, output-limit, and result checks
passed synthetic tests. Codex's exact runtime model identity was not exposed;
Claude result metadata reported `claude-opus-5-5`. OpenCode host execution remains
unverified because its local executable does not start. No account or billing
configuration was changed.
