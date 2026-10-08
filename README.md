# Jerry's skills

Agent skills created by [Jreevo](https://github.com/Jreevo).
Each skill has its own folder in `skills/`. Keep its files together.

## Skills

| Skill | Host | Reviewers |
| --- | --- | --- |
| [codex-review](skills/codex-review/) | Standalone Codex | Native Codex agents using available GPT models |
| [claude-review](skills/claude-review/) | Standalone Claude Code | Native Claude agents using available Claude models |
| [t3-review](skills/t3-review/) | T3 Code | Configured providers through T3 delegation |

The standalone versions use separate reviewer contexts and different review lenses.
Reviewers inherit the configured model by default. They do not promise model diversity.
They use manual risk assessment and need no separate triage API key or Python helper.
Use `t3-review` for a panel that can span providers. It requires T3 Code, configured
model providers, Python 3, and macOS. Catalog availability does not prove spare quota.

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
