# Jerry's skills

Agent skills created by [Jreevo](https://github.com/Jreevo).
Each skill has its own folder in `skills/`. Keep its files together.

## Skills

| Skill | Host | Reviewers |
| --- | --- | --- |
| [codex-review](skills/codex-review/) | Standalone Codex | Native GPT agents, or Codex + Claude Code CLI reviewers with `--mixed` |
| [claude-review](skills/claude-review/) | Standalone Claude Code | Native Claude agents, or Claude Code + Codex CLI reviewers with `--mixed` |
| [opencode-review](skills/opencode-review/) | Standalone OpenCode | Configured native models, or Codex + Claude Code CLI reviewers |
| [t3-review](skills/t3-review/) | T3 Code | Configured providers through T3 delegation |

The standalone versions use separate reviewer contexts and different review lenses.
Reviewers inherit the configured model by default. They do not promise model diversity.
They use manual risk assessment and need no separate triage API key.
Native review needs no Python helper. The optional terminal route needs Python
3.10+ on macOS, Linux, or WSL to manage separate CLI sessions and their deadlines.
OpenCode can use models from its configured providers. This skill inherits the
parent model by default. Use `t3-review` for a panel managed through T3 delegation.
It requires T3 Code, configured
model providers, Python 3, and macOS. Catalog availability does not prove spare quota.

## Host compatibility

Use the version for your active host. Each native agent API has different fields.
The skill checks actual capabilities before dispatch. A skill folder alone does
not give a chat application terminal access or native agent tools.

The packaged terminal helper can run from another harness that permits Python,
local CLI processes, result inspection, and cancellation. Use the
[terminal guide](skills/codex-review/references/terminal-review.md) directly.
This route supports macOS, Linux, and WSL. It requires Codex 0.160.1+ and Claude
Code 2.1.292+ with eligible logins in that environment. Native Windows Python
is not supported. Remote hosts need their own accessible CLI installations.

The runner accepts absolute CLI paths when a desktop app has an incomplete
`PATH`. It saves private progress and results so a lost tool response does not
require another panel. Unsupported versions and unavailable seats stay visible.
Other harnesses have not been tested end to end. See each skill's validation notes.

## Use existing subscriptions

Install Codex and Claude Code, then sign in through their normal CLI login flows.
The skills can use those existing local logins for a mixed-provider review.
A ChatGPT subscription does not authenticate Claude Code, and a Claude subscription
does not authenticate Codex. Each CLI uses its own account and usage limits.

```text
Use $codex-review to review the current diff --mixed.
/claude-review staged --mixed
Use the opencode-review skill for the current diff --terminal.
```

The terminal runner uses a complete inline packet in fresh sessions. It removes
API-key and parent-session environment overrides, requires subscription auth,
disables reviewer tool access where supported, and runs in a private directory
outside the source repository. It reports quota, login, CLI, and result failures.
It does not install CLIs, copy login tokens, change billing, or fall back to API keys.
See the [terminal guide](skills/codex-review/references/terminal-review.md).

## Install

Clone this repository:

```sh
git clone https://github.com/Jreevo/skills.git jreevo-skills
```

### Codex

Install both the skill and reviewer definition:

```sh
mkdir -p ~/.agents/skills ~/.codex/agents
cp -R jreevo-skills/skills/codex-review ~/.agents/skills/
cp jreevo-skills/skills/codex-review/agents/codex-reviewer.toml ~/.codex/agents/
```

Start a new Codex session. Ask:

```text
Use $codex-review to review the current diff.
```

See the [Codex guide](skills/codex-review/README.md).

### Claude Code

Install both the skill and reviewer definition:

```sh
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R jreevo-skills/skills/claude-review ~/.claude/skills/
cp jreevo-skills/skills/claude-review/agents/claude-reviewer.md ~/.claude/agents/
```

Start a new Claude Code session. Run:

```text
/claude-review
```

See the [Claude Code guide](skills/claude-review/README.md).

### OpenCode

Install the skill:

```sh
mkdir -p ~/.config/opencode/skills
cp -R jreevo-skills/skills/opencode-review ~/.config/opencode/skills/
```

Install the matching V1 or V2 reviewer file with the
[OpenCode guide](skills/opencode-review/README.md#install).
Start a new OpenCode session. Ask:

```text
Use the opencode-review skill to review the current diff.
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
