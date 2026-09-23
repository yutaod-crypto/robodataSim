# Specify the task

Use the requested scenario, catalog row and latest implementation to resolve known
choices. A short structured plan is enough; no new configuration framework is needed.

## Contract fields

- Purpose/source: category, task row, capability tested, accepted simplifications.
- Entities: movable objects, fixtures, articulated parts, tools/targets, dimensions,
  joints, reset distributions and reference frames.
- State/evidence: prerequisites, completion predicates, policy-visible evidence at
  each stage, and evaluator-only state kept out of policy inputs.
- Transitions: actions with preconditions/effects, state-dependent decisions, legal
  concurrency and ordering. Use a partial order when multiple orders are valid.
- Mechanism: contact/geometry, occlusion, capacity or temporal constraint enforcing
  the dependency; explicitly identify abstract software rules where intended.
- Scoring: final state, required history, violation/recovery outcomes and settling
  thresholds derived from geometry rather than solver convenience.
- Validation: correct, violating and repaired cases, plus relevant nuisance variation.

Read [benchmark-contracts.md](benchmark-contracts.md) for category-specific criteria.

## Three independent distinctions

1. Parameter variation: sizes, poses, friction or other sampled quantities.
2. State-dependent decisions: observed conditions change the appropriate action.
3. Ordering freedom: independent actions may occur in either order or concurrently.

These can coexist in any category. Randomized battery yaw remains a conditional task;
two interchangeable loading orders do not alone create a branching benchmark.
For decisions, specify condition -> valid response -> completion evidence. For order,
specify prerequisite edges and accept all intended legal orders, not one demonstration.

## Dishwasher example

Open door, extend rack to expose loading surfaces, load movable dishes, retract and
close. Goals follow the rack's live frame; loading order can remain unconstrained
where access allows. Identify a feasible misplaced dish that physically obstructs
retraction/closure, compare a correct placement, and show correction restores success.
Arbitrary labeled zones do not demonstrate this dependency. Check actual size ranges:
a supposedly tall item may fit everywhere. Score loaded/stable dishes and required
rack/door states independently; closing an empty appliance fails. Fixed display dishes
are unsuitable for a loading benchmark.

## Memory example

Define cue exposure, occlusion, intervening task and later query. Different earlier
cues should require different choices in an otherwise indistinguishable current policy
observation. Record hidden history for evaluation/replay without leaking it as input.
