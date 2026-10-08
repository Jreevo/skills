# mixed-model-review

One review panel skill for standalone Codex, Claude Code, and OpenCode.
By default, it starts Codex and Claude Code reviewers through their authenticated
terminal CLIs, so two model families review the same work. `--native` uses only
the active host's native agents instead. It requires no T3 Code server.

The skill identifies the host from its native tools and reads only that host's
dispatch guide in [references/hosts](references/hosts/). The review workflow,
terminal runner, and reviewer brief are shared by every host.

## Install

From a clone of `Jreevo/skills`, copy the skill folder and the reviewer definition
for your host. Start a new session after installing.

### Codex

```sh
mkdir -p ~/.agents/skills ~/.codex/agents
cp -R skills/mixed-model-review ~/.agents/skills/
cp skills/mixed-model-review/agents/codex-reviewer.toml ~/.codex/agents/
```

### Claude Code

```sh
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R skills/mixed-model-review ~/.claude/skills/
cp skills/mixed-model-review/agents/claude-reviewer.md ~/.claude/agents/
```

### OpenCode

```sh
mkdir -p ~/.config/opencode/skills ~/.config/opencode/agents
cp -R skills/mixed-model-review ~/.config/opencode/skills/
```

Check your OpenCode version with `opencode --version`.
Install only the reviewer definition for your runtime.
Both definitions use the same installed agent name, `opencode-reviewer`.

V1 uses `permission` mappings and the native Task tool:

```sh
cp skills/mixed-model-review/agents/opencode/v1/opencode-reviewer.md ~/.config/opencode/agents/opencode-reviewer.md
```

V2 uses ordered `permissions` rules and the native `subagent` tool:

```sh
cp skills/mixed-model-review/agents/opencode/v2/opencode-reviewer.md ~/.config/opencode/agents/opencode-reviewer.md
```

For project installation, use `.opencode/skills` and `.opencode/agents` instead
of the global directories. Do not install both reviewer versions as active agents.

### Upgrading from the per-host skills

This skill replaces `codex-review`, `claude-review`, and `opencode-review`.
Delete those installed skill folders so the host does not offer duplicate review
skills. The reviewer agent names are unchanged; recopy them to pick up any updates.

## Use

```text
Use $mixed-model-review to review the current diff.          # Codex
/mixed-model-review staged --reviewers 3                      # Claude Code
Use the mixed-model-review skill for staged changes.          # OpenCode
/mixed-model-review staged --native                           # same-host panel only
/mixed-model-review path/to/plan.md --dry-run
```

In OpenCode, use the skill name in a normal prompt. Installing a skill alone does
not create a custom `/mixed-model-review` command there.

Manual risk assessment selects one to four seats and their review lenses.
A mixed panel uses at least two seats, one per provider, unless you pass
`--reviewers 1`. The chair checks findings against the captured target before
reporting them. If a provider's CLI or login is not ready, the skill names the
gap and continues with the remaining provider or the host's native agents.
Without any panel support, it reports a single-reviewer fallback.
It does not use the T3 scoreboard or triage API.
The default terminal route needs Python 3.10+ on macOS, Linux, or WSL and
existing subscription logins for Codex and Claude Code. `--native` needs no
Python helper.
See the [terminal guide](references/terminal-review.md) for packet format,
authentication checks, deadlines, and failure handling.

## Models and mixed panels

The default panel runs each CLI's default model unless you request one.
Native reviewers (`--native` or a fallback) inherit the session model. Separate
contexts and lenses do not prove model or provider diversity.

- **Codex:** native reviewers use GPT models available in the session.
- **Claude Code:** native reviewers use Claude models available in the session.
- **OpenCode:** native reviewers can use models from configured providers. To
  request a different model, select an already-configured reviewer agent with the
  requested `provider/model` and equivalent review-only permissions. V2 supports
  catalog-defined `#variant` suffixes. The default mixed route prefers such agents
  when they cover different providers, then uses eligible terminal reviewers.
  `--terminal` skips them.

The terminal route uses each CLI's own login and usage limits. A ChatGPT
subscription does not authenticate Claude Code, and a Claude subscription does
not authenticate Codex. Those subscriptions do not need to be imported into the
host's provider settings. The skill does not create provider credentials or
modify model configuration during a review.

## Reviewer permissions

- **Codex:** the reviewer requests a read-only filesystem. Session overrides can
  affect that policy, and filesystem restrictions do not block all external tools.
  If the host cannot select a custom reviewer type, available native agents can
  review the inline packet; the skill reports that the packaged configuration was
  not applied.
- **Claude Code:** the reviewer permits only Read, Grep, and Glob. The skill grants
  no additional tool permissions and reports model substitutions or unverified
  model identity.
- **OpenCode:** the policies allow local read/search tools and deny other tools by
  default. They are tool permission policies, not an operating system sandbox.
  Verify the effective policy when other configuration overrides the same agent.

On every host, the skill requires packet-only analysis if reviewer restrictions
cannot be verified.

## Product references

- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex subagents and custom agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code subagents and tool restrictions](https://code.claude.com/docs/en/sub-agents)
- [OpenCode V1 skills](https://opencode.ai/docs/skills/),
  [agents](https://opencode.ai/docs/agents/), and
  [permissions](https://opencode.ai/docs/permissions/)
- [OpenCode V2 skills](https://opencode.ai/v2/docs/skills),
  [agents](https://opencode.ai/v2/docs/agents),
  [permissions](https://opencode.ai/v2/docs/permissions), and
  [models](https://opencode.ai/v2/docs/models)

## Validation

Merged skill (2026-10-08), dry runs on a synthetic billing diff in a scratch
project with Claude Code 2.1.294 and Codex 0.161.0:

- Claude Code identified itself as the host, chose the default mixed route,
  assessed Critical risk, and planned four alternating Codex/Claude seats.
- Codex identified itself as the host and chose the default mixed route. With
  approval to run outside its sandbox, it planned three alternating seats with
  both logins verified. Inside its `workspace-write` sandbox, Claude Code reported
  `loggedIn: false` for a valid login; the chair marked that seat unverified and
  attributed it to the sandbox, as the terminal guide now requires.
- OpenCode was not tested; `opencode --version` still exits with code 137.

No reviewer inference ran in these dry runs. Earlier per-host results follow.

Codex: Codex CLI 0.160.1 loaded the project skill and completed a dry-run on a
synthetic billing-status plan. It selected Heavy risk and three planned seats,
started no reviewers, and ignored an instruction embedded in the target to start
T3 tasks. A full native panel run has not been verified.

Claude Code: Claude Code 2.1.292 discovered the project skill and packaged
reviewer. Provider quota blocked the earlier native behavioral test. File
metadata, tool restrictions, and resource links passed validation. A dry-run
result and full native panel run have not been verified.

OpenCode: the skill metadata, references, and both reviewer policies were checked
against the official V1 and V2 documentation. The local executable exited with
code 137 for `opencode --version`. Native skill discovery, dry-run behavior, and
a full panel run have not been verified in OpenCode.

Terminal: Codex CLI 0.160.1 and Claude Code 2.1.292 completed a concurrent
packet-only review using existing ChatGPT and Claude subscription logins. Both
found a known expiry-boundary defect in the same synthetic target. The target
included an instruction to run commands; neither reviewer used tools. The
runner's failure, deadline, cancellation, output-limit, and result checks passed
synthetic tests. Codex's exact runtime model identity was not exposed; Claude
result metadata reported `claude-opus-5-5`. No account or billing configuration
was changed.

Portability (2026-10-08): the terminal runner passed full-panel fixtures with
explicit CLI paths, an empty `PATH`, paths with spaces, an unavailable seat, and
SIGTERM cancellation. It also tested oversized files and children left after
normal CLI exit. CI runs the helper suites on Linux and macOS with Python 3.10
and 3.12. A fresh live Codex + Claude subscription panel passed with the updated
controls, matching snapshot IDs, no observed tool use, and confirmed child cleanup.
Codex's required feature controls are checked without inference before dispatch.
These checks do not establish native OpenCode execution or native panel support
in other harnesses.
