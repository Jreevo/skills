# Jerry's skills

Agent skills created by [Jreevo](https://github.com/Jreevo).
Each skill has its own folder in `skills/`. Keep all files in a skill folder together.

## Skills

| Skill | Purpose | Requirements |
| --- | --- | --- |
| [t3-review](skills/t3-review/) | Review code, plans, or copy with a panel of different models. Verify and merge their findings. | T3 Code, configured model providers, Python 3, and macOS. |

## Install

Clone this repository:

```sh
git clone https://github.com/Jreevo/skills.git jreevo-skills
```

For the Claude provider:

```sh
mkdir -p ~/.claude/skills
cp -R jreevo-skills/skills/t3-review ~/.claude/skills/
```

For Codex:

```sh
mkdir -p ~/.codex/skills
cp -R jreevo-skills/skills/t3-review ~/.codex/skills/
```

Start a new T3 Code conversation so the agent can load the skill.
Ask: **Use the t3-review skill to review the current diff.**
Use `/t3-review` where the provider supports skill commands.
Read the [t3-review guide](skills/t3-review/README.md) for options and requirements.

## Add a skill

Create `skills/<skill-name>/SKILL.md` with `name` and `description` in YAML frontmatter.
Put required scripts, reference files, and an installation guide in the same folder.
Add the skill to the table above.

Keep credentials, local paths, review packets, and review history out of the repository.
