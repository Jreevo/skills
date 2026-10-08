# Jerry's skills

Agent skills created by [Jreevo](https://github.com/Jreevo).
Each skill has its own folder in `skills/`. Keep its files together.

## Skills

| Skill | Host | Reviewers |
| --- | --- | --- |
| [mixed-model-review](skills/mixed-model-review/) | Standalone Codex, Claude Code, or OpenCode | Codex + Claude Code CLI reviewers by default, or native host agents with `--native` |
| [t3-review](skills/t3-review/) | T3 Code | Configured providers through T3 delegation |

`mixed-model-review` puts Codex and Claude reviewers on the same work by default,
each in a separate context with a different review lens. If a provider is not
ready, it reports the gap and continues with the remaining provider or the host's
native agents. `--native` uses only the host's native agents, which inherit the
configured model and do not promise model diversity.
It uses manual risk assessment and needs no separate triage API key.
The default terminal route needs Python 3.10+ on macOS, Linux, or WSL to manage
separate CLI sessions and their deadlines. Native review needs no Python helper.
In OpenCode, native reviewers can use models from configured providers.
Use `t3-review` for a panel managed through T3 delegation. It requires T3 Code,
configured model providers, Python 3, and macOS. Catalog availability does not prove spare quota.

## Host compatibility

Install the same skill folder in each host, plus that host's reviewer definition.
Each native agent API has different fields. The skill identifies the host from its
native tools and checks actual capabilities before dispatch. A skill folder alone does
not give a chat application terminal access or native agent tools.

The packaged terminal helper can run from another harness that permits Python,
local CLI processes, result inspection, and cancellation. Use the
[terminal guide](skills/mixed-model-review/references/terminal-review.md) directly.
This route supports macOS, Linux, and WSL. It requires Codex 0.160.1+ and Claude
Code 2.1.292+ with eligible logins in that environment. Native Windows Python
is not supported. Remote hosts need their own accessible CLI installations.

The runner accepts absolute CLI paths when a desktop app has an incomplete
`PATH`. It saves private progress and results so a lost tool response does not
require another panel. Unsupported versions and unavailable seats stay visible.
Other harnesses have not been tested end to end. See the skill's validation notes.

## Use existing subscriptions

Install Codex and Claude Code, then sign in through their normal CLI login flows.
The skill uses those existing local logins for its default mixed-provider review.
A ChatGPT subscription does not authenticate Claude Code, and a Claude subscription
does not authenticate Codex. Each CLI uses its own account and usage limits.

```text
Use $mixed-model-review to review the current diff.
/mixed-model-review staged
/mixed-model-review staged --native
Use the mixed-model-review skill for the current diff --terminal.
```

The terminal runner uses a complete inline packet in fresh sessions. It removes
API-key and parent-session environment overrides, requires subscription auth,
disables reviewer tool access where supported, and runs in a private directory
outside the source repository. It reports quota, login, CLI, and result failures.
It does not install CLIs, copy login tokens, change billing, or fall back to API keys.
See the [terminal guide](skills/mixed-model-review/references/terminal-review.md).

## Install

Clone this repository:

```sh
git clone https://github.com/Jreevo/skills.git jreevo-skills
```

Install `skills/mixed-model-review` and the reviewer definition for your host:

```sh
# Codex
mkdir -p ~/.agents/skills ~/.codex/agents
cp -R jreevo-skills/skills/mixed-model-review ~/.agents/skills/
cp jreevo-skills/skills/mixed-model-review/agents/codex-reviewer.toml ~/.codex/agents/

# Claude Code
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R jreevo-skills/skills/mixed-model-review ~/.claude/skills/
cp jreevo-skills/skills/mixed-model-review/agents/claude-reviewer.md ~/.claude/agents/
```

OpenCode needs the V1 or V2 reviewer file that matches its version.
See the [skill guide](skills/mixed-model-review/README.md#install) for OpenCode
and for removing the older `codex-review`, `claude-review`, and `opencode-review`
installs. Start a new session, then ask:

```text
Use $mixed-model-review to review the current diff.          # Codex
/mixed-model-review                                           # Claude Code
Use the mixed-model-review skill to review the current diff. # OpenCode
```

### T3 Code

Install `skills/t3-review` in `~/.claude/skills` for the Claude provider or
`~/.agents/skills` for the Codex provider. Start a new T3 Code conversation.
Ask: **Use the t3-review skill to review the current diff.**
See the [T3 guide](skills/t3-review/README.md) for requirements and options.

## Add a skill

Create `skills/<skill-name>/SKILL.md` with `name` and `description` in YAML frontmatter.
Put required scripts, reference files, and an installation guide in the same folder.
Add the skill to the table above.

Keep credentials, local paths, review packets, and review history out of the repository.
