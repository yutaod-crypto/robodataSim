# Phase 3 — Generate the script

For a requested complete scripted task, write the environment and solver.
For narrower changes, edit only the needed components. Use the nearest existing task as a concrete template — don't write either from a blank
page, since the house conventions (how objects are exposed as attributes,
how observables are wired, how success checks read local-frame poses) are
easier to copy correctly than to reinvent.

**Register the new env where every other script will find it, not just the
one you're testing with.** robosuite's `EnvMeta` metaclass auto-registers a
task env the moment its module is *imported* — but only for whatever script
actually imported it. If the project's package `__init__.py` imports each
task module (check for this pattern first), add the new task there too, and
update any other script's task registry/import list that enumerates tasks
by name (a teleop collector's `TASK_REGISTRY` dict, for instance). Missing
this doesn't fail while generating/verifying the new task itself (whatever
script you're using to build and test it presumably already imports the new
module directly) — it fails later, opaquely, in a *different* script (a
generic replay tool, a teleop collector) with "Environment <Name> not
found", the first time someone tries to use the new task through it.

## The task environment file

A subclass of the project's task base class (e.g. `CustomTaskEnv`),
typically implementing:
- Object construction (instantiate each object from the phase-1 spec,
  exposing each as a `self.<name>` attribute other methods can reach).
- A placement initializer (one sampler per object, with position/rotation
  ranges from the spec's initial-pose distributions). **Compute real
  separation margins between objects' `horizontal_radius` values rather
  than guessing at placement ranges** — an elongated or asymmetric object's
  `horizontal_radius` is often larger than its footprint alone (a circular
  bound around an asymmetric shape), and placement samplers reject any
  configuration that violates minimum separation, so ranges that are too
  tight for the real radii cause hard-to-diagnose "cannot place all
  objects" errors at reset time. The opposite mistake also happens: don't
  set `horizontal_radius` to a moving part's *full swept footprint* (e.g. a
  hinged door's entire open-swing extent) just because it's part of the
  object -- that property is what the placement sampler uses to keep spawn
  *centers* apart, not a claim about volume swept during the task, and
  padding it with swept volume that nothing else will ever spawn inside of
  just forces every other object's placement range needlessly far out,
  often past the arm's comfortable reach for no actual benefit. Size it to
  the object's resting/closed footprint plus an ordinary margin.
- A success-check method implementing the phase-1 predicate: usually
  per-object local-frame position/orientation checks against another
  object's live pose (not fixed world coordinates), following the pattern
  of whatever the project's existing tasks already do (e.g. dot products
  between rotation-matrix columns for orientation alignment, relative
  position within a margin for containment).
- Observables exposing only the contracted policy inputs. Keep evaluator-only
  state separate, especially hidden cues, branch labels and occluded object poses.

## The solver script

Built on `MotionController` from `motion.py`. For a **parametric** task
(see `decompose.md`), the pattern is a straight-line sequence:

```python
def solve_episode(env, verbose=False):
    mc = MotionController(env, verbose=verbose)
    env.reset()
    mc.hold(-1.0, 20)  # let objects finish settling before reading poses

    handle = mc.grasp(env.<object>_body_id)
    if handle is None:
        return False  # grasp failed -- don't burn the rest of the episode

    target_rotmat = ...  # usually another object's live rotmat
    target_pos = jittered_pose(env.rng, base_pos, base_rotmat, local_xyz,
                                xy_jitter=..., z_jitter=...)
    ok, handle = mc.place(handle, target_rotmat, target_pos,
                           rotate_in_place=<True if orientation must change>,
                           remeasure_after_rotate=<True if rotate_in_place>)
    if not ok:
        return False

    # ... repeat grasp/place per step in the spec's sequence ...

    return env._check_success()
```

A few things worth calling out explicitly, since they're easy to get wrong
by not thinking about them:
- `rotate_in_place=True` only when the object's orientation actually needs
  to change to reach its goal (e.g. fixing polarity/orientation). If the
  object's spawn orientation already matches its goal orientation (common
  for objects with a fixed spawn yaw, like a lid that always lands the same
  way up), skip reorientation entirely — it's extra motion that can only
  introduce grasp slip for no benefit.
- `remeasure_after_rotate=True` whenever `rotate_in_place=True` — a big
  in-place rotation measurably lets a rigid-pinch grasp slip, so the
  pre-rotation grasp-relative transform goes stale. Skipping the re-measure
  makes later position/orientation targets silently wrong rather than
  erroring, which is a much worse failure mode than the extra
  `still_grasped` check costs.
- Always check the return of `grasp()`/`place()` before continuing. A
  script that keeps issuing motion commands for an object it's no longer
  holding won't error — the end-effector just drives to nonsense targets
  for the rest of the episode, sometimes to physically unreachable poses,
  burning the full step budget for no benefit.
- Use `jittered_pose` for placement targets rather than the exact computed
  center: releasing exactly at a target's resting-contact height means the
  position controller has to fight real contact resistance the whole way
  down, which converges unreliably. Releasing from a small random offset
  just *above* resting height, then letting gravity finish settling, is
  both more reliable and produces useful placement variety in the resulting
  demonstrations instead of pixel-identical repeats.

### Branching solver pattern

If phase 1 classified the task as **branching**, the solver needs a
classification step right after settling, before doing anything else:

```python
def classify_branch(env):
    """Reads live post-reset state and returns which branch applies."""
    if <condition observed in live state>:
        return "already_placed"
    return "pick_and_place"

def solve_episode(env, verbose=False):
    mc = MotionController(env, verbose=verbose)
    env.reset()
    mc.hold(-1.0, 20)

    branch = classify_branch(env)
    if branch == "already_placed":
        ...  # this branch's step sequence
    elif branch == "pick_and_place":
        ...  # that branch's step sequence

    return env._check_success()
```

For evaluated decisions, classify from the contracted policy observations.
Simulator object poses can also be privileged (for example behind a closed door).
If a demonstration oracle reads them, label that use and do not report its decision
accuracy as evidence of perception or memory. See benchmark-contracts.md.

## Path planning ("won't hit anything")

`MotionController.move_via_clearance` already gives you the practical
default: transit at a safe height above the target XY rather than moving
diagonally through the scene, avoiding sweeping a held object into whatever
else is on the table. That's sufficient for open tabletop scenes with only
flat, low obstacles. If a task's fixture includes something *tall* (an open
cabinet door, a raised divider), a plain diagonal `move_to`/`move_via_clearance`
between two far-apart points can genuinely collide with it — confirmed via
direct contact inspection (`env.sim.data.contact`) in exactly this
situation, not a hypothetical. The fix that worked: rise straight up to a
fixed safe altitude *above the known obstacle's max height* first, move
laterally at that altitude, then descend — i.e. absolute-altitude transit
rather than clearance-relative-to-target transit. This is a distinct
pattern from `move_via_clearance` (which is relative to the *target's*
height, not a fixed known ceiling) worth reaching for specifically when a
task has a tall fixture in the way. If a task needs to route *around*
rather than *over* an obstacle (a wall, a frame with no clear overhead
path), that's a real extension needing an actual collision check between
waypoints — implement when the actual fixture requires it. A path over a closed shell
does not provide access through the roof; use the opening and moving rack.

## Hinged parts: grasp+swing vs. push

For a hinged mechanism (a door, a flap, a lid on a real hinge — as opposed
to a free-floating lid like Task 1's, which is just placed on top),
`MotionController` has two approaches, choose the approach from handle access and required contact forces:

- `grasp()` (or `grasp_fixed_part()` if the part won't lift off a surface)
  + `swing()`: grip a handle and sweep it through the arc. Needs the handle
  to actually be reachable/graspable by whatever approach direction
  `grasp()` uses (top-down by default — a handle mounted on a vertical face
  needs `approach_dir`/`grasp_rotmat` overrides, or redesigning where the
  handle sits, e.g. sticking up from a top edge instead of out from a
  face), and needs the grasp-relative transform to stay valid through the
  whole arc (same slippage risk as any large in-place reorientation, see
  design-objects.md's grasp-margin notes).
- `push_arc()`: no grasp at all — just move a contact point through the
  arc. Simpler (no grasp-relative transform, nothing to lose grip of, no
  approach-angle problem since you're not trying to *enclose* the handle)
  and was more reliable in practice. For a thin handle passing between open fingers, close the
  gripper to create a pushing surface; verify contact rather than assuming it. An open parallel-jaw gripper pushing a
  thin handle doesn't actually make contact — the handle just passes
  between the open fingers (confirmed empirically: a full push sequence
  with the gripper open moved the eef through the intended arc while the
  hinge angle didn't change at all; closing the gripper first as a blunt
  paddle fixed it completely). Push in short segments, re-reading the
  part's actual live position each time and re-deriving the remaining
  angle, rather than one long open-loop sweep — a push's true progress
  under resistance can lag the ideal arc, and segmenting keeps it
  self-correcting.


## Articulated parts and task history

Task-specific gestures may extend the motion library: approach, pinch, segmented
pull/push, carry, insertion, release and hinge following need different contact
conditions. Keep numerical poses and gains in the task script; put reusable evidence
and selection rules in this skill. For each gesture record prerequisites, termination
criteria, step budget and failure evidence. An implemented gesture is not a validated
one when every episode stops before reaching it.

When contact anywhere on a rigid mechanism is allowed, do not constrain every
operation to its named handle. Pulling may need a grasp; retraction can use the palm
or closed fingers as a top-down paddle against a front wall, lip or platform. Check
the part's joint progress in bounded segments instead of requiring the wrist to
converge to a deliberately penetrating push target. Stop on measured lack of progress,
verify the final joint threshold and check that loaded objects stayed seated.
Inspect the entire approach, push and withdrawal path: lowering a push near an
opening can clear an upper seal even when the initial push height works farther out.

A hybrid gesture can avoid maintaining a fragile grasp through a large rotation.
For the dishwasher door, a side grasp angled above the table lifts the edge far
enough to expose the outer face; subsequent live-pose pushes finish closure. A flat
side grasp hit the table and a full grasped arc lost contact. Treat these as examples
for selecting contact modes, not universal poses or a requirement to grasp every door.

For a long handle, distinguish permitted motion along the rod from transverse grasp
error, then verify contact and actual joint travel. Do not infer engagement merely
from the gripper closing. Check the full travel, including the robot's own mount:
the capacity dishwasher's horizontal grasp maintained contact during a partial pull
but hit the Panda pedestal before full extension. Increasing position gain exposed
that collision; it did not fix the path. Angled approaches also contacted the rim or
lost the handle. Diagnose geometry/kinematics before further gain tuning.

Use the appropriate frame and joint for each operation. Re-read rack and handle poses
after movement. A grasp orientation suitable for a horizontal handle may be unsuitable
for a later top-down object grasp; set the desired orientation explicitly rather than
inheriting the last command. Check move/grasp return values and measured joint motion
before declaring a phase complete. Validate approach, loaded motion and retreat with
whole-arm contacts, not just fingertip waypoints.

For ordering/resource/memory evaluation, reset and maintain the required history in
the environment/evaluator, not just the solver. Derive completion events from achieved
state with settling criteria. Record or reconstruct this history during replay and
keep hidden evaluator fields out of observations. The phase sequence of an oracle
solver is not proof that other policies are scored correctly.

## Table-supported box alignment

When insertion needs an upright, axis-aligned box, align it while supported by the
table before lifting if requested or mechanically preferable. Approach the measured
post yaw, close without an automatic lift, and rotate toward the nearest valid
symmetry-equivalent orientation. Verify actual table contact, bottom height and
upright/yaw error before lifting. Recheck after lift, then preserve achieved rotation
through the carry; fail rather than silently making the correction in the air.
This validates yaw alignment of standing boxes, not recovery of a box lying on its
side. Keep that distinction explicit in the reset contract and results.

Pose randomization means initial positions/orientations, not merely size variation.
Use reachable, collision-free regions with sufficient clearance for rotated bounds;
resample on both hard and soft resets and test seeded reproducibility. When identities
can swap regions, choose manipulation order from measured poses, not object names.
For box scoring use the actual oriented footprint, accounting for square symmetry;
a center-only or cylinder-radius check can accept corners protruding outside a bay.

When the user requests closest-first picking, define the reference point and metric
explicitly. Recompute distances from the live gripper to the remaining grasp points
after each placement, log candidates and the selected minimum, and keep destination
assignment separate from object identity or selection order. Do not silently reserve
small objects for last. Validate changed order through complete execution: loading
one item can alter later approach clearance even when the capacity condition allows it.
