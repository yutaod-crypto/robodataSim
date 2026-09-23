# Object and mechanism building standard

Use this standard when creating, adapting or integrating simulation assets. Reuse
suitable existing assets, but check their geometry, articulation and robot access
against the new task. A shape suggestion is not a design specification. The output
must explain what the object does, how its parts move, how the robot interacts with
it, and what evidence establishes that it works.

Apply the sections relevant to the asset: a rigid prop does not need a joint tree;
a fixed appliance does not need a whole-appliance grasp test. User requirements
control simplifications and task difficulty. Record unknowns rather than presenting
photo-derived dimensions or hidden mechanisms as measured facts.

## 1. Define the build specification before geometry

Keep a compact specification beside the task assets, in the existing task document
or an asset design file. Resolve these fields to concrete dimensions and choices:

| Field | Required design information |
| --- | --- |
| Purpose | Object identity, task role, intended operations, and physical dependencies to preserve |
| Reference | Images/existing assets, observed features, estimated dimensions, unknown internals, approved simplifications |
| Coordinates | Metres and radians; root origin, local axes, upright/long axis, support plane, quaternion convention |
| Dimensions | Outer envelope, usable interior, wall/support thicknesses, grasp cross-sections, openings and motion ranges |
| Structure | Rigid parts and their parents; fixed versus moving parts; joints and constraints if applicable |
| Interaction | Grasp regions or push surfaces, approach and closing axes, operation direction, release and retreat space |
| Physics | Collision representation, mass/inertia method, material/contact choices, joint resistance and any assistance |
| Variation | Allowed initial poses and dimension ranges, support conditions, reach envelope and reserved motion corridors |
| Acceptance | Legal/illegal configurations, applicable checks, numerical thresholds with rationale, evidence paths |

Separate cosmetic, contact-critical and task-critical features. Cosmetic detail may
be omitted first. A handle, rim, neck, rack support or hinge location is not cosmetic
when it controls grasping, containment, support, access or ordering.

## 2. Decompose the assembly and define its motion

For articulated assets, draw a body/joint tree before writing MJCF. Each part that
moves relative to another needs an explicit relative transform and degree of
freedom. Rigidly attached subparts may share a body; decorative seams do not need
joints. Mount children on the body whose motion they actually follow.

For each joint, specify parent/child bodies, type, pivot, axis in the stated local
frame, limits, initial position, damping/friction, and the physical operation it
represents. Verify the sign of motion in the assembled model. A single photo does
not establish hidden linkages: use the simplest mechanism consistent with visible
motion and the task, and document the assumption.

Dishwasher example, to adapt rather than copy blindly:

```text
cabinet root (fixed)
├── door (hinge at the lower front edge)
│   └── handle (rigid attachment)
├── lower rack (slide along its actual guide direction)
│   ├── supports / tines (rigid attachments)
│   └── rack pull surface (rigid attachment)
└── upper rack or shelf (slide or fixed, according to the reference/task)
```

A rack riding on cabinet rails is not automatically a child of the hinged door.
Document whether rails, stops and support transfer are represented by the ideal
joint, contact geometry, or both. Do not add cosmetic wheels as free joints unless
their dynamics matter. Do not invent an interlock merely to force the solver order;
verify a required physical dependency through contact or model it explicitly as an
approved abstraction.

Check the complete travel at empty and representative loaded states: intermediate
poses, stops, clearances, support, and whether the mechanism stays usable under load.
A door that opens is not evidence that the rack can extend far enough for loading.

## 3. Choose geometry by the behavior it must preserve

Prefer the simplest representation that preserves silhouette, contact, support and
functional dimensions. Use primitives, compound convex parts or meshes as needed;
do not force every asset into boxes or cylinders.

| Asset feature | Representation decision and required check |
| --- | --- |
| Solid rigid prop | Match task-critical extents and grasp surfaces; remove small cosmetic detail first |
| Hollow cup, bin or cabinet | Build collision walls, base and rim separately so the usable cavity remains open |
| Round or tapered container | Retain body proportions, base, taper, shoulder/neck and lid where they affect identity or interaction |
| Handle, hook or utensil | Preserve finger entry space, closing thickness, support and useful contact surfaces |
| Rack or shelf | Represent actual load-bearing supports; verify small items cannot fall through unintended gaps or perch on tines |
| Door, flap or drawer | Preserve hinge/guide placement, panel thickness, stops, opening and complete swept volume |

Do not use one convex collision hull for an entire concave container: it can fill
its opening. Inspect the compiled collision representation separately from the
visual mesh. Do not leave a hidden cylindrical collider under an anti-roll faceted
visual mesh, or assign collision to a visual-only copy that doubles contact/mass.
Check the installed loader's duplication and inertia behavior.

### Round, cylindrical and faceted objects

Choose the contact cross-section deliberately. A circular object is not inherently
unsuitable, and an octagon is not a universal replacement. State whether rolling,
axial symmetry or orientation alignment is part of the task.

- If rolling is intended, preserve curved contact and provide the intended support
  and control strategy. Do not suppress the task with a hidden constraint.
- If rolling is incidental, consider an upright reset, an observed flat base/side,
  a supported staging location, or an approved faceted approximation. Keep the
  recognizable circular-like form and useful grasp surfaces.
- For faceting, specify side count, circumradius, inradius, face orientation, and
  axial dimensions. For a regular n-gon, inradius = circumradius × cos(pi/n).
  Grasp width depends on rotation; check actual projected width over allowed yaw,
  not only a nominal diameter. More sides approach round contact and may roll more
  easily; fewer sides change packing and orientation behavior.
- Test gravity settling and a small stated perturbation in every allowed support
  mode. Record drift, tipping/rolling, contact stability and grasp retention.
  Friction alone is not proof that a horizontal bottle will stay in place.
- Do not randomize an unsupported pose just to claim orientation diversity. Specify
  allowed resting faces and placement heights using actual rotated collision bounds.

## 4. Make robot interaction part of the asset design

Specify contact regions and candidate approach/closing directions in the object's
local frame. Transform them from the live pose at execution time. Sites document
interaction targets; they do not create a physical handle or contact surface.

Check gripper aperture against the cross-section along the actual closing axis,
including finger thickness and approach clearance. A long object can be graspable
across a thin section. `horizontal_radius` is a spawn bound, not a graspability test.
Choose top, side, oblique, push or staged regrasp actions according to geometry and
the required final orientation. Top-down reachability does not require every grasp
to be top-down. A fixed fixture may be operated by pushing or pulling rather than
lifting. A lid without a pinchable edge needs a reachable push surface or an
explicitly approved handle/tab modification.

Reserve space for approach, closure, loaded travel, reorientation, release and
retreat. Check the held object and whole robot, including forearm and pedestal.
Isolated reach to a point does not prove a loaded pose or path is feasible. Verify
separation under randomized layouts; initial non-overlap alone does not leave a
side-entry grasp corridor. Replan from measured poses after a failed action.

For enclosed appliances, expose the placement region by the intended opening/rack
motion. Do not load through the ceiling. Evaluate targets in the moving support's
live frame. Keep reset objects out of door/rack swept volumes and account for the
robot mount when reserving pull distance. In this checkout, table length changes
also affect pedestal placement: recheck reach as well as travel clearance.

## 5. Budget dimensions and tolerances separately

Record actual values per relevant axis; avoid a universal clearance or global scale
factor. Use projected geometry at the allowed orientations, including placement
error and settling tilt. For each critical fit, document:

- Nominal object extent and available interior/opening dimension.
- Clearance for valid insertion, release and retreat, including robot fingers.
- Dimension variation and pose-error allowance used for validation.
- Remaining interference in the intended invalid configuration, if blocking matters.
- Contact-solver tolerance and evaluator tolerance, separately from usable clearance.

Increasing an insertion allowance must not erase a capacity, headroom or orientation
dependency. Long objects can wedge after small tilt even with positive nominal
clearance. Test offsets and load contact, not only a centered CAD fit. Do not fail
valid resting wall contact solely because of an arbitrary inward scoring buffer.
Conversely, an evaluator tolerance must not accept visibly protruding objects.

If adapting layout, prefer a targeted change with a reason: table area for full
rack travel, fixture pose for reach, or a particular prop dimension for insertion.
Uniform scaling changes grip widths, capacity and physical behavior and requires
revalidation. Record the resulting dimensions, not just the scale factor.

## 6. Define physics and integration explicitly

Assign positive mass and physically consistent inertia to moving bodies from stated
material/density estimates or explicit values. Verify the compiled totals and
centres of mass after composing or duplicating geoms. Reconsider them after adding
handles/tabs or changing dimensions; visual edits can change operating forces.
Use contact properties appropriate to the intended surfaces and verify their effect
in drop, slide, grasp and loaded mechanism tests. Do not use extreme friction,
inertia, damping or hidden constraints merely to conceal a failed mechanism.

Inspect the installed robosuite loader and a working local asset. In this checkout,
`MujocoXMLObject` expects the `worldbody/body/body` object structure, placement marker
sites and explicit visual/collision groups. Verify names, prefixed joints/sites and
multiple instances. Confirm angular units and joint defaults after model assembly.

A fixed fixture has no free root joint; its internal hinges/sliders still exist.
Set the root pose before assembly and reset internal joints by name. Never assume
`joints[0]` is a free-joint pose. Remove standalone position servos for passive robot
operation: zero control can still command a position target. Document counterbalance,
gravity compensation, actuators or other assistance when intentionally used.

## 7. Validate through separate acceptance gates

For each applicable gate, record configuration, threshold/rationale, observed result
and artifact path. Mark untested capabilities as unverified. Do not silently replace
failed physical evidence with a scoring label or a hand-set pose.

| Gate | Required evidence |
| --- | --- |
| Geometry and appearance | Inspect isolated and assembled renders, plus collision geometry; check proportions, cavities, supports and interaction surfaces |
| Compilation and reset | Compile through the actual loader and repeated wrapper/XML reconstruction; exercise allowed parameter extremes, namespaces and valid geometry dimensions |
| Mechanism | Sweep complete joint ranges empty and loaded; inspect intermediate contacts, stops, support and unintended penetration |
| Free-prop behavior | Release under gravity in allowed orientations; measure support, rolling/tipping and any specified perturbation response |
| Robot interaction | Real-controller approach, sustained grasp/push/pull, loaded movement or full fixture travel, release and retreat; inspect whole-arm contacts |
| Task dependency, when applicable | Legal, violating and repaired cases with the same operation budget; distinguish physical blocking, self-correction and score-only rejection |

A bounded diagnostic torque can establish that a hinge works; it is not evidence
that the robot can operate it. A lift test applies to a movable prop, not a cabinet.
Assigned poses are useful predicate tests, not manipulation demonstrations. For
robot datasets, continue with [verify.md](verify.md) for action replay and outcome
validation, and [reset-layout-pipeline.md](reset-layout-pipeline.md) for diversity.

Success metrics belong to the task contract, not to a generic asset standard.
Choose persistence, containment, release and motion diagnostics according to what
completion means. Do not impose the delivery-box or dishwasher speed thresholds on
unrelated tasks. Version user-requested criterion changes, preserve original labels,
and explicitly re-evaluate historical recordings when using the new criteria.

## 8. Deliver a reproducible asset package

Keep the build specification, parameterized source or generator, MJCF and required
meshes/materials in the task folder. Include named joint and interaction-frame
mappings, reset assumptions, evidence reports/renders and known limitations in the
task documentation. Freeze model/source hashes with evaluations and demonstrations.
Do not overwrite incompatible recordings or mix their geometry/metric versions.

After revision, rerun the gates affected by the change: geometry affects collision,
fits and grasping; joint/fixture placement affects sweeps and robot reach; changed
mass affects operation; reset ranges affect support and access. Expand testing when
those results expose a shared problem, rather than replaying unchanged full trials
without diagnosing the failure.
