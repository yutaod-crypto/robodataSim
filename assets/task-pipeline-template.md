# Task pipeline contract

Use this as a compact task README/design section. Fill the relevant fields and omit
sections outside the requested deliverable; examples do not prescribe task difficulty.

## Task and reset

- Task key / task folder:
- Tested dependency and complete success predicate:
- Object identities, dimensions, grasp affordances and symmetry:
- Fixed fixtures and robot initialization:
- Randomized area assignments, XY distribution and orientation axes/ranges:
- Excluded areas and reason (collision, table bounds, reachability, task constraint):
- Seed handling, hard/soft reset behavior and actual pose capture point:

## Reset evidence

- Sample count, seeds and source/model version:
- Common world XY bounds and stable color legend for layout graphs:
- Polygon extraction from actual saved geometry; extra height views if needed:
- Reset-only gallery and raw pose report:
- Per-object XY/yaw spans, area occupancy, distinct assignments and invalid resets:
- Reproducibility and boundary/overlap checks; remaining uncertainty:

## Execution and dataset, if requested

- Policy/gesture selection and how choices depend on measured state:
- Tuning budget and failure evidence; separate frozen protocol:
- Requested retained successes / maximum attempts:
- HDF5 location, model/config/source provenance and terminal-state alignment:
- Fresh-environment action replay tolerance, measured error and final success:
- Attempts, retained successes, failure reasons and tested branches:
- Retained-layout coverage versus reset-only coverage:
- Browser gallery, simulator replay command and explicit limitations:

## Organization

- Use envs/, assets/, scripts/, demonstrations/<unique_run>/ and evaluations/ as needed.
- Place browser artifacts in the dataset's web/ folder and preserve previous versions.
- Link raw reports and replay checks; distinguish recorded evidence from intended behavior.
