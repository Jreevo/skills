# t3-review

Review code, plans, or copy with a panel of different models in T3 Code.
The chair selects reviewers from the live model catalog.
It checks their findings against a captured review packet and merges confirmed issues.
The skill applies fixes only when the user asks.

## Requirements

- T3 Code with delegated task support.
- Configured model providers that can run child tasks.
- Python 3. The helpers use the standard library.
- macOS for the current Keychain integration. The state helper uses Unix file locking.

See the [repository installation steps](../../README.md#install).
Keep the full `t3-review` folder together. Resolve helper paths relative to `SKILL.md`.

## Use

Ask: **Use the t3-review skill to review the current diff.**

Where skill commands are supported:

```text
/t3-review
/t3-review path/to/file --reviewers 3
/t3-review staged --round2
/t3-review path/to/plan.md --dry-run
```

`--dry-run` prints the planned panel without starting reviewers.
It can still call the triage API.
Read [SKILL.md](SKILL.md) for all arguments and the review process.
Model names in [roster.md](roster.md) are preferences.
The live T3 catalog determines availability.

## Optional API triage

`triage.py` attempts OpenAI API triage with `gpt-6-luna` at `/v1/decisions`.
It reads the recipient's credential from macOS Keychain service `t3-review-openai`.
This repository includes no credential.
API triage sends the captured review packet to OpenAI.
Reviewer tasks send that packet to the selected providers.

Without a configured credential or available API route, the skill uses manual triage.
Manual triage applies the same policy without a network or Keychain call.
The live API route and reviewer providers are not validated by the helper tests.

## Local data

The state helper creates private review packets in temporary directories.
It writes a local `scoreboard.jsonl` when reviews are logged.
The repository excludes review history, packets, and Python cache files.
Each installation starts with its own review history.

## Test the helpers

From the repository root:

```sh
python3 -I -m unittest discover -s skills/t3-review/tests -p 'test_*.py' -v
```

Tests use synthetic data. They do not call model APIs or read credentials.
