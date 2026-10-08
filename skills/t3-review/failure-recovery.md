# Reviewer failure recovery

Use this policy for known unavailable routes and failures during a review.
A route is a provider instance plus model. Family diversity and author exclusions
remain unchanged across routes. The same Claude model through two providers is
still the same model and family.

## Classify the evidence

Read the terminal task result first. If it contains only a generic error, read
the failed child's durable activity once for a precise error or partial output.
Do not guess a cause from a model name. The catalog proves configuration and
child-task support; it does not prove quota or service health.

- **Account quota or spend limit:** skip that provider/account route. Trying a
  cheaper model on the same exhausted account is not a reliable remedy. Use a
  configured alternative route or another family. Honor a known reset time. If
  no reset is provided, mark it unavailable for this invocation; do not invent
  a reset time or maintain an indefinite global ban.
- **Temporary rate limit:** honor Retry-After when available. Retry only if the
  delay fits the remaining budget; otherwise use a backup. Do not busy-wait.
- **Unavailable model or invalid options:** refresh the catalog once. Correct
  unsupported options or choose another eligible model. Preserve target effort;
  disclose a cap instead of silently reducing effort.
- **Network, provider, or unknown failure:** use the preselected backup. Prefer
  an unused family. An alternative model in the same family is allowed when it
  preserves panel diversity. Do not repeat the same unknown failing route by
  default. Record the cause as unknown unless there is specific evidence.
- **Permission failure:** use complete inline, packet-only analysis when viable.
  Do not loosen runtime permissions. If the target cannot be inspected, report
  incomplete coverage rather than replace safety controls.
- **Timeout:** cancel the live task and report incomplete. A seat whose deadline
  has passed has no remaining budget for a replacement.

Authentication failures require a configured alternative route or an incomplete
seat. Do not repair credentials, sign into another account, buy capacity, raise
spending limits, or enable a more expensive speed tier as review recovery.

## Replace once within the original budget

Each logical seat gets at most **two delegated attempts per round**: the original
and one replacement or transient retry. Four logical seats mean at most eight
delegated attempts in a round. A requested rebuttal round has its own bound.
A transport retry with the exact same clientRequestId recovers the existing task;
it does not authorize another attempt or restart its deadline.

Before replacing, confirm the old task is terminal or its cancellation has been
acknowledged. If task identity or cancellation is unknown, do not launch duplicate
work. Record the unresolved task and continue with other seats.

Keep the seat's original deadline. Use only the time remaining for attempt 2.
Do not reset the clock. Start a replacement as soon as its terminal failure is
known while other seats continue; it need not wait for every seat to finish.
In an environment without yielding calls, keep the shorter disclosed seat budget.

Choose a backup from the refreshed live catalog. It must obey author/chair
exclusions, family rules, permissions, user model constraints, and effort mapping.
If the user fixed an exact model list, do not substitute an unrequested model;
report the failed seat. The normal automatic panel permits substitutions.

Announce the replacement and cause. Call `delegate_task` again with attempt 2's
request ID, the same goal, user decisions, original snapshot, lens, prior task
outcome, and any unresolved objections. For a failed first round, prior findings
may be absent. Do not message the backing child to restart it. A replacement is
one logical seat, not an additional vote. Do not dispatch a third attempt.

## Preserve useful work and report coverage

Partial output from a failed task can provide leads. Verify those leads against
the snapshot. Label them `recovered from failed review`; do not count that task
as a completed reviewer. If a replacement confirms the same issue, it is still
one completed seat, not two votes. Log failed and replacement attempts separately
with the same seat identity and a replacementOfTaskId link.

Record failed routes in the private run state and scoreboard. Use explicit recent
account-limit evidence to avoid that route during its stated limit window. Do not
automatically demote a vendor's finding quality because transport or quota failed.
The quality-ranking helper excludes failed attempts.

If the backup fails or no backup is eligible, return the verified available
results. Report requested seats, completed seats, replacements, failed attempts,
and missing lenses. Critical work with an unfilled high-risk lens gets an
`incomplete review` verdict; do not present it as fully reviewed or ready to ship.
