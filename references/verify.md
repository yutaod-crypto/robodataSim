# Validate the requested deliverable

Apply the levels affected by the change. A complete benchmark needs dependency and
robot evidence; a standalone asset does not require a whole robot dataset.

## 1. Predicate and observations

Use controlled states for complete, incomplete, missing-object and wrong-state cases.
These test scoring, not physical enforcement or robot reachability. Check every
required object: door-only scoring previously accepted dishes never moved from spawn.
Audit policy inputs for hidden information. Test histories for ordering/resources.
See [benchmark-contracts.md](benchmark-contracts.md).

## 2. Dependency experiment

Run positive, violating and repaired cases under comparable limits/actions. Inspect
contacts and achieved states, not only reward. Vary sizes/poses that might defeat the
mechanism. If both cases succeed, a physical dependency remains unproven even when a
zone predicate rejects one; if both fail, investigate the positive case/execution.
Do not loosen criteria to make the solver pass.

## 3. Compile, render, reset

Compile the integrated model, inspect rendering with normal robosuite visual groups,
and run multiple seeded resets across geometry ranges. Check unintended contacts in
used door/rack configurations and namespace collisions for multiple instances.
For collection/replay, explicitly exercise the wrapper's reset_from_xml_string path;
plain env.reset calls do not prove that separate reconstruction path works.
Use the local venv. Headless checks disable camera rendering. This checkout's viewer
imports pynput: PYNPUT_BACKEND=dummy is appropriate for headless validation only, not
interactive keyboard teleoperation.

## 4. Manipulation

Drive the real controller. Verify sustained lift/carry after settling, large rotation
and travel, then stable release; a momentary bump is not a grasp. For fixtures measure
joint displacement and sustained contact rather than demanding a vertical lift.
Check approach/operation/retreat and whole-arm contacts, including upper links,
pedestal and held object. Nominal reach does not prove collision-free convergence.
A standalone servo cycle does not prove robot graspability.

## 5. Reliability

Use saved seeds/conditions and a stated attempt budget (e.g. 12 diagnostic episodes,
not a statistical guarantee). Report successes/all attempts with per-phase and
per-condition failures; cover every intended branch. Isolate repeatable failures
before another batch. Re-run affected checks after fixes and broaden only when shared
geometry/controller changes justify it. Separate isolated-phase successes from full
runs: a 0/N full-run result is still 0/N.

Separate tuning seeds from a frozen evaluation batch and retain both reports. Save
the source/model hashes, versions, seeds, randomized dimensions, failure phase and
contact evidence. If a deterministic prerequisite blocks all seeds before randomized
objects are touched, say so: those failures measure the shared motion bottleneck,
not sensitivity to the object distribution or downstream gesture reliability.

## 6. Dataset replay and behavior

Save through the actual collection pipeline. Reconstruct the recorded model/environment,
restore the correctly aligned initial state, replay actions in a fresh instance and
compare corresponding states throughout. State replay alone does not test determinism.
Restore/recompute evaluator history too. Report maximum divergence and its tolerance;
bitwise identity across versions is not guaranteed. Inspect a rendered replay or all
relevant object trajectories/achieved states separately: wrong behavior can replay
perfectly. Test the first episode before scaling; report how many retained episodes
were checked. Preserve model/config/seed provenance and existing recordings.

## Report

State the category/dependency, levels passed, positive/negative/repair outcomes,
attempted/successful episodes, causes and unverified scope. Keep integration, benchmark
validity, oracle demonstration and learned-policy performance distinct.

For success-target HDF5 collection, first validate one actual wrapper-collected trial
through fresh-environment action replay. Retain only final settled successes that pass
replay, while recording every failed attempt and replay rejection separately. A target
of ten retained successes is not a ten-attempt success-rate experiment. Store the
terminal state as well as the standard equal-length pre-action states and actions so
the last action can also be checked. Keep model XML, configuration, seeds, source
hashes and per-episode replay errors alongside the dataset. Preserve prior datasets.

Do not equate tiny position jitter with meaningful layout randomization. When the user
expects different starting arrangements, test each object's coverage across the allowed
areas and measure XY spans. Inspect retained successful demonstrations too: rejection
and execution failures can leave a success-only dataset with much less diversity than
the reset sampler. Show starting-layout comparisons and report the actual retained
coverage. Preserve earlier limited-layout recordings as a distinct dataset version.
