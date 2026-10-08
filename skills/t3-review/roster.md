# t3-review roster

These are candidate preferences. Validate provider and model IDs against the live
`orchestrator_capabilities` catalog for every invocation. If a candidate is absent,
use another eligible model in that family. If a provider cannot run child tasks,
skip it. Newly configured families can join the panel after catalog validation.

## Family order

Fill different families before repeating a family. Exclude author models and the
chair model across aliases. Prefer other families, then use a different model in
an author/chair family only when needed to fill the panel. Unknown author identity
must be disclosed. Apply these rules before the preferences below.

1. OpenAI, provider `codex`: `gpt-6.1-sol`, then `gpt-6-sol`, then `gpt-5.6-sol`.
2. Google, provider `cursor`: choose the strongest available Gemini suitable for
   the lens. Candidate IDs: `gemini-3.1-pro`, `gemini-3.8-flash`.
3. xAI, provider `cursor`: `grok-4.7`, then `grok-4.6`.
4. Anthropic: prefer provider `claudeAgent` when it is available. An existing
   configured `cursor` route can be an alternative. Candidates on either route:
   `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5`. Check each route's
   own catalog and effort options. Both routes are one vendor family.
5. Moonshot, provider `cursor`: `kimi-k3`.
6. Zhipu, provider `cursor`: `glm-5p3`.

For copy, prefer Anthropic and OpenAI among eligible families. Other families can
fill missing seats. Do not use mini, nano, flash-lite, or haiku tiers by default.
An ordinary Flash candidate is not excluded by that rule. Fixed effort is not a
measure of model strength. Favor a model's fit for the highest-risk lens over the
family order; disclose capped effort.

Availability comes before preference. Skip a route with a known active account
limit. A model in the catalog is not proof of spare quota. Read
[failure-recovery.md](failure-recovery.md) for bounded replacements. Do not change
accounts, credentials, subscriptions, spending limits, or paid speed modes.

## Learning from history

Use `review_state.py rank <work-type>`. Do not compute rankings from raw JSONL.
The helper skips malformed records with line-number diagnostics. It excludes
failed and incomplete seats. It counts an invocation once per provider/model,
so rebuttal rounds do not inflate the sample size.

With at least 5 successful reviews for the work type, use confirmed findings per
review as a secondary signal within the diversity rule. If rejected findings
outnumber confirmed findings, move that model later and say so. Findings counts
are affected by lens and difficulty; they are not a quality benchmark by themselves.
