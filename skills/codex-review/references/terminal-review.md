# Terminal subscription reviewers

Use this route for a requested mixed-provider review when native agent tools
cannot reach the other provider. OpenCode can prefer configured native model
agents; `--terminal` selects this CLI route instead.

## Requirements

- Python 3.10+ on macOS, Linux, or WSL. The runner uses POSIX process groups.
- Installed Codex and Claude Code CLIs with existing subscription logins.
- Codex 0.160.1+ and Claude Code 2.1.292+. These are the minimum tested
  versions. The runner rejects older or unverified version formats before
  checking auth or starting inference. Newer versions can still change flags.
  Report an unsupported CLI failure; do not remove safety flags to work around it.
- Permission for the chair to execute the packaged Python helper.

If sign-in is missing, tell the user which CLI needs `codex login` or
`claude auth login`. Do not start login, change accounts, buy capacity, request
API keys, or copy authentication files during a review.
The runner requires Codex's ChatGPT login and Claude Code's `claude.ai`
first-party login. It rejects API-key, key-helper, and third-party auth routes.

## Probe without reviewer inference

Resolve `REVIEW_SKILL` to the directory containing this SKILL.md.

```sh
python3 -I "$REVIEW_SKILL/scripts/terminal_review.py" probe --reviewer codex --reviewer claude
```

This checks CLI versions and calls their auth-status commands. For Codex, it
also checks that the requested feature controls report disabled without inference.
A missing, removed, or ineffective required control blocks that seat. It does not
request model inference. Auth status is not a model entitlement or quota check.
Use the returned readiness information and recent failure evidence.
The output excludes raw auth status, account email, org IDs, and credential values.
Exit code 1 means a selected CLI is unavailable or the probe was cancelled.
Inspect each probe reason; do not treat an empty result list as a successful panel.

Desktop apps can use a different `PATH` from the user's terminal. If a selected
CLI is installed but not found, use `--codex-bin` or `--claude-bin` with its
absolute executable path. Quote paths that contain spaces. Use a file path,
not an alias, a shell command, or arguments. The runner does not search the
source repository or install software to fill a missing seat.

```sh
python3 -I "$REVIEW_SKILL/scripts/terminal_review.py" probe --reviewer codex --reviewer claude --codex-bin "$CODEX_BIN" --claude-bin "$CLAUDE_BIN"
```

Resolve these paths in the current host. A remote container, SSH session, or WSL
instance needs its own accessible CLIs and eligible local login state. A login
on another machine or in a browser does not prove readiness here. Do not copy
credentials into a container or redirect a local review to a remote service.
Native Windows Python is not supported by this runner. Run the helper and both
CLIs inside the same WSL environment instead.

## Prepare the packet

Capture the complete target and assess risk with the normal review workflow.
Write a private JSON file with exactly these fields:

```json
{
  "goal": "Review this change against the stated requirements.",
  "decisions": ["Review only. Keep the existing product behavior."],
  "author_models": ["unknown"],
  "work": "The complete diff or document, with locations and required context."
}
```

Use actual captured work, not a path-only placeholder. Keep secrets, `.env`
contents, credentials, and unrelated data out. Record author model provenance
without guessing. Use a private directory and mode 0600 for the packet.
The runner hashes the complete packet and never truncates it. Its limit is
200000 characters, including trusted context. Raw packet and rebuttal files
are also limited to 2000000 bytes before parsing. UTF-8 files may include a BOM.
Split an oversized target; do not truncate it.

Print risk, requested seats, lenses, models, subscription routes, and timeout
before dispatch. Prefer different eligible providers for mixed review. Disclose
seats that use the author or chair model and unknown model provenance.
Do not assume four seats imply four models or four vendors.

## Run the panel

```sh
python3 -I "$REVIEW_SKILL/scripts/terminal_review.py" run --packet "$PACKET" --reviewer codex --reviewer claude --lens correctness --lens "security and data safety" --timeout-seconds 600
```

The default CLI model is used unless an explicit, available model is requested.
That default is not inherited from the chair's session. Model syntax for the
runner is `codex:<model-id>` or `claude:<model-id-or-alias>`. Use models the user
can access; do not guess availability. Explicit models do not change global defaults.
The runner permits one to four seats. Match the user's requested count and the
assessed risk. Repeat an eligible provider with another lens when needed, but
label shared-model reviews honestly. Do not silently replace an unavailable seat.

Add `--dry-run` to probe auth and print the plan without reviewer inference.
Normal chair inference still uses the chair's provider.
There is no separate decision API call or API key requirement in this route.

The runner launches the selected CLIs concurrently in new sessions. It sends the
packet through stdin and uses argument arrays, not shell interpolation.
Claude Code runs with built-in tools disabled, safe mode, and no configured MCP
servers. Codex runs read-only with shell, native delegation, apps, plugins,
hooks, memory, skill search, local image reads, browser, and computer-use
features disabled for that call.
It ignores user configuration for the Codex run and uses a private work directory.
It does not grant the reviewer access to the source repository.
These controls do not replace host security policies or a verified OS sandbox.
Managed CLI policy can still apply. Report effective-control limits; do not
promise that a prompt alone enforces packet-only review.

The child environment keeps local auth locations but drops API-key, provider
routing, OAuth-token, and parent-session overrides. It does not modify the parent
shell. CLI login state stays with the owning CLI. Subscription usage limits still
apply; eligible login is not a guarantee of a successful review or zero usage.

## Completion, failure, and cancellation

The helper prints its run ID, process ID, and private artifact path to stderr
before the probes. It prints one final JSON manifest to stdout. `manifest.json`
is created at startup and replaced atomically as probes and seats finish.
The manifest records its format version, snapshot, round, planned seats, and
finished results. Every seat gets a result file, including unavailable seats.
Each launched seat also gets private stdout, stderr, prompt, and process-ID files.
Its result file first records a running state, start time, and deadline.
Only a final seat state is a completed outcome.
Save the artifact path. Inspect progress there if the host loses its tool result.
Do not start a duplicate panel while the first run's state is unresolved.
Do not paste raw CLI logs or publish packets. SIGINT, SIGTERM, or SIGHUP asks the runner to cancel its
children. The runner terminates each timed-out child's own process group and
reports whether cleanup was confirmed. Cleanup can take a few additional seconds.
The runner also checks for remaining children when a CLI exits normally.
A forced kill of the runner itself can prevent cleanup; do not claim otherwise.
A saved `runner_pid` is evidence for that run, not permission to signal a later
process that reused the ID. Cancel through the host's active process handle,
or send SIGINT/SIGTERM only after verifying that the process still owns this run.
If cleanup is unconfirmed, report it and resolve the live process before starting
a retry or rebuttal. Do not kill unrelated CLI sessions.

Use a yielding tool runner and give progress updates while the process runs.
Do not leave a background CLI panel unresolved at the end of the chair's turn.
Use the manifest for progress. Accept its final state only after the runner exits.
A nonzero exit can still contain completed seats plus failed, unavailable, or
timed-out seats.
Do not retry a quota or authentication failure or switch to API-key billing.
The CLI's error flag matters even when its exit code is zero.

The runner validates the review's JSON shape, snapshot ID, and inspection evidence.
It rejects malformed output, observed tool use, and denied tool attempts.
It limits combined CLI output, including Codex's final JSON file, to 8000000 bytes.
A result that exceeds the limit is incomplete. Valid output does not prove that
the findings are correct or that every file was covered. Verify against the snapshot,
merge by root cause, and report coverage and failed seats with the normal workflow.
Codex model identity is unverified if its output exposes no model metadata.
Claude model usage names are reported only when present in CLI result metadata.
Reported costs remain unknown; subscription usage is not treated as an API bill.

For one requested rebuttal, use the same packet and add `--rebuttal` with a private
text file containing prior findings, responses, and unresolved objections.
Set `--timeout-seconds` to the seat's remaining budget. Use separate calls when
seats have different remaining budgets. Fresh sessions preserve the snapshot hash;
rebuttal output does not add an independent first-round vote.

Product references:

- [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
- [Codex authentication](https://learn.chatgpt.com/docs/auth)
- [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [Claude Code authentication](https://code.claude.com/docs/en/authentication)

Codex disables both shell implementations through `features.shell_tool=false`.
`unified_exec` selects the backend and is not used as an enforcement switch.
See the [Codex shell tool registration](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/spec_plan.rs).
