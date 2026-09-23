# Reusable reset-layout and demonstration pipeline

Use this reference when building randomized tasks or reviewing dataset diversity.
The dishwasher is a worked example, not a fixed recipe for object count, spawn sides,
nearest-first ordering, grasp style, or number of retained demonstrations.

## Define what varies

Separate geometry changes from initial pose changes. Specify allowed spatial areas,
identity-to-area assignments, continuous position distributions, orientation axes,
object symmetries, fixed fixtures and robot initialization. State what stays fixed.
Tiny XY jitter around fixed slots is not a varied scene layout. Wide sampling across
unreachable or obstructed regions is not a useful substitute. Preserve the task's
reasoning dependency while checking bounds, overlaps and the complete motion corridor.

Copy [the task contract template](../assets/task-pipeline-template.md) into a task's documentation when a written
contract will help; adapt it instead of imposing irrelevant fields on simple assets.
Use the project's task-local folder and path helpers.

## Record actual resets, then visualize them

Capture each object's actual world pose after the final reset/wrapper reconstruction,
before the first action. Use stable object identities and explicit quaternion order,
metres and coordinate frame. Never substitute intended sampler targets or a final
placement for the recorded initial pose. Measure geometry from the saved model when
rendering historical datasets; live object definitions can change.

Show an overview grid of top-down starting layouts with:
- Identical world bounds and metric scale across episodes, fixed fixtures, and a legend.
- Consistent object colors/names; orientation-aware projected footprints, not only dots.
- Episode ID and seed; optional links or videos for full playback.
- An explicit population label: reset samples, all attempts, or retained successes.

Keep a reset-only gallery separate from success-only data. A reset sampler may cover
many areas while the controller succeeds in only a narrow subset. Report per-object XY
spans, area occupancy counts, yaw coverage (respecting symmetry), distinct assignments,
and observed overlap/bounds failures. Compare requested, sampled and retained coverage;
choose task-appropriate criteria rather than borrowing the dishwasher's centimetres.

The bundled [layout-gallery generator](../scripts/build_layout_gallery.py) generates an offline HTML grid using
only Python's standard library. It accepts polygons so box, round, irregular and
projected tilted objects can share the same renderer. Compute those polygons in a
task adapter; use a convex hull or suitable outline for full 3D projected geometry.
The tool displays geometry and does not certify collision freedom, reachability,
sampling fairness, success or replay correctness.

Manifest schema:

```json
{
  "title": "Task reset comparison",
  "population": "all reset samples before filtering",
  "bounds_xy": [-0.6, 0.6, -0.6, 0.6],
  "object_colors": {"object_a": "#4d80b3"},
  "fixtures": [
    {"name": "fixture", "polygon_xy": [[0,0],[0.2,0],[0.2,0.2],[0,0.2]]}
  ],
  "episodes": [
    {"id": "reset_1", "seed": 7, "objects": [
      {"name": "object_a", "polygon_xy": [[-0.3,0.3],[-0.2,0.3],[-0.2,0.4],[-0.3,0.4]]}
    ], "video": "demo_1.webm"}
  ]
}
```

`video` is optional and relative to the generated HTML. All polygons are world XY
metres; retain the full poses/model provenance in the source report too. Fixture
polygons should represent the recorded reset state. For stacked or multi-level tasks,
add height labels or additional views: overlapping XY projections alone do not prove
physical overlap. Do not hide unsupported reset samples to make a gallery look better.

## Validate execution and save the requested deliverable

Use the [verification guidance](verify.md) for physical, wrapper, predicate and replay checks. Before
scaling collection, replay one wrapper-collected HDF5 episode in a fresh environment.
Keep pre-action states/actions aligned, preserve model XML and terminal state, and
record maximum state divergence and final success. Maintain evaluator history for
ordering/memory tasks. A browser video is a separate saved-state visualization.

For a requested success-target dataset, retain final successes passing replay and log
all failures. Use a bounded attempt budget, diagnose repeated failures, and version
source/model changes rather than pooling incompatible trials. Do not automatically
collect ten episodes just because the worked example did. Recompute layout coverage
on the retained subset and show it beside the reset-sampling coverage.

## Worked implementation in this repository

- `custom_tasks/dishwasher/envs/capacity.py`: four-area reset assignment, XY/yaw sampling.
- `custom_tasks/dishwasher/assets/check_box_resets.py`: hard/soft resets, actual bounds,
  separation, area coverage, seeded reproducibility and footprint scoring.
- `custom_tasks/dishwasher/scripts/collect.py`: wrapper collection, initial poses,
  source snapshots, final-success retention and fresh-env action replay.
- `custom_tasks/dishwasher/scripts/render.py`: HDF5 videos and clickable layout thumbnails.
- `custom_tasks/dishwasher/demonstrations/distributed_first_10/`: worked dataset/report.

Its retained ten episodes cover nine area assignments and both sides per object.
The earlier `archive/nearest_first_10` shows why small jitter was visually insufficient.
Reuse the separation of reset audit, execution, retained-data audit and browser review;
adapt physics and policy choices to the next task.
