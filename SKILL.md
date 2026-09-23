---
name: robosuite-task-builder
description: Build or debug robosuite/MuJoCo benchmark tasks, articulated assets, and controller-driven demonstration solvers in a custom_tasks pipeline. Preserve conditional, memory, branching, resource, and ordering dependencies; verify mechanics, scoring, robot execution, and replay separately. Use for task implementation and asset integration, not merely summarizing benchmark literature.
---

# Robosuite task builder

Build the requested task or asset while preserving what the benchmark measures.
A compiling model, a correct predicate, a mechanical cycle and a complete robot
demonstration are separate results.

## Establish the current contract

Read the relevant task row/category, benchmark rationale, and latest applicable
project log entries. In this repository:
- `custom_tasks/Tasks_Design(Draft).md`
- `custom_tasks/benchmark调研.pdf`
- `PROGRESS.md` (chronological; newer entries supersede old checkpoints)

Inspect current code too: files and logs can disagree or change during concurrent
user work. Locate moved assets before recreating them. Treat literature claims in
the research draft as project rationale, not independently verified facts.
Infer settled choices from the user's instructions and these sources. Ask only when
an unresolved choice materially changes the task; no routine confirmation of an
already specified category or variation mode.

Scope validation to the deliverable: assets need compatibility/mechanics checks;
benchmark tasks additionally need dependency checks; requested solvers/datasets need
execution/replay checks. Do not silently expand one into all three. Preserve approved
simplifications, but flag any that erase the tested dependency.

## Workflow

1. Specify prerequisites, observable evidence, valid alternatives, scoring and
   positive/negative/repaired cases. Read [decompose.md](references/decompose.md)
   and [benchmark-contracts.md](references/benchmark-contracts.md) for benchmark work.
2. Build or adapt assets using the [object and mechanism building standard](references/design-objects.md).
   Specify dimensions, body/joint structure, collision geometry, interaction regions,
   tolerances and physics before implementation. Validate the applicable appearance,
   reset, mechanism and robot-interaction gates; scale the process to the asset.
3. Implement the requested environment/solver using existing infrastructure where
   suitable. Read [generate-script.md](references/generate-script.md). Adapt fixed
   fixture handling rather than assuming every object has a free root joint.
4. Run the applicable checks in [verify.md](references/verify.md). Fix the mechanism
   or implementation, not the criterion, when the intended contrast fails.

For randomized resets or dataset diversity, read
[reset-layout-pipeline.md](references/reset-layout-pipeline.md). It includes the
dishwasher worked example, an adaptable task contract and an offline layout-gallery
generator. In this project, include starting-layout comparisons when reviewing
randomness, and distinguish reset-sample coverage from retained-success coverage.

Use `base_env.py` and `motion.py` where appropriate; scaffold missing infrastructure
only if the requested work needs it. The project default is one folder per task:
`custom_tasks/<task_folder>/{envs,assets,scripts,demonstrations,evaluations}/`.
Read `custom_tasks/README.md` for this convention and use `custom_tasks/task_paths.py`
to resolve task aliases and generate unique run paths. Save HDF5 datasets under
`demonstrations/<run>/`, browser artifacts beside the dataset under `web/`, and
reports under `evaluations/`. Keep common infrastructure shared; don't duplicate it
inside every task. Explicit user locations still take precedence. Preserve existing recordings and identify
incompatible geometry versions instead of deleting them or mixing them silently.

## Debugging and reporting

Measure contacts, live poses and phase outcomes before tuning dimensions or gains.
Use bounded diagnostic runs; isolate repeated failures rather than repeatedly retrying
an unchanged full sequence. Distinguish weak dependency difficulty from excessive
manipulation difficulty: enlarging everything can break grasping without improving
reasoning. See the prop audit in the design reference.

Report what passed and what remains unverified, attempted/successful episode counts,
and decision versus execution versus model/scoring failures. A replay can faithfully
reproduce wrong behavior. Selected successful retries do not establish overall success
rate. Update the project log with concrete new task-development findings and limits.


## Design review preference for this project

The user requests an interactive simulation view whenever an asset design is
finished. After relevant validation, launch the completed design in the local
MuJoCo/robosuite viewer with a useful free camera, and provide a reproducible launch
command. Static inspection and recorded diagnostic playback must be labeled;
neither is a full robot demonstration. Retain the browser preview alongside it.
If desktop access is unavailable, report the launch failure and provide the command
and browser fallback rather than claiming the window opened. This preference applies
to this user's project; do not assume other installations want GUI windows launched.

## Maintaining this project's GitHub mirror

The user requested a skill-only repository named `robodataSim` and synchronization
of future local skill edits. For this authorized project mirror, after editing and
validating the skill, run `python3 .claude/skills/robosuite-task-builder/scripts/sync_github.py`
from the robosuite root. It uses an isolated `.skill-publish/robodataSim` checkout,
creates a private repository on first authenticated publication, and never force
pushes. Report authentication/network/conflict failures rather than claiming sync.
Do not transfer this publishing authorization to an unrelated user's installation.

For edits outside an agent session, the same command with `--watch` synchronizes
after ten quiet seconds; it must remain running with credentials and network access.
`--prepare` only prepares local files. The script reads credentials from GitHub CLI,
the normal Git credential flow, or GH_TOKEN/GITHUB_TOKEN; never put tokens in skill
files or chat. No simulation recordings are included in the mirror.
