# Category contracts and evidence

Start from physically plausible catalog scenarios. Identify the primary scored
capability and incidental constraints; do not silently substitute a different task.

| Category | Required distinction | Validation/scoring |
| --- | --- | --- |
| Conditional | A specific earlier result enables a later operation. | Compare correct/incorrect/ repaired placement, orientation or installation under comparable downstream actions; score prerequisites and completion. |
| Memory | Required earlier information is hidden after intervening work. | Match current observations while varying history; score recall and completion; audit camera, state, ID and instruction leakage. |
| Branching | Different observed states require different responses. | Exercise every state, including no-repair cases; score decision separately from execution; test universal recovery shortcuts. |
| Resource contention | Multiple goals use a capacity-limited resource. | Record acquire/use/release intervals or inventory; check conflicts, release, completion and deadlock. |
| Ordering | Valid histories respect precedence, alternation, nesting or synchronization. | Test alternative legal sequences and targeted violations; score achieved events against the intended partial order. |

## Physical conditional evidence

Initialize nonpenetrating cases, then use contact-respecting dynamics. Do not keep
writing qpos/qvel or weld a free obstruction to manufacture blocking. Initial pose
assignment is useful for mechanism tests but does not establish robot reachability.
Use comparable force/torque limits, budgets and targets; document the operating range.
Inspect contact pairs and resulting clearance. Test size extremes and small placement
errors that could erase the contrast. Rigid objects may move under excessive force;
report blocking within realistic operating conditions, not absolute impossibility.
If closing pushes the obstruction aside and succeeds, record that outcome honestly.
A scoring zone can reject a wrong placement without proving physical dependence.

For capacity-based placement, check occupied volume rather than target labels or
summed footprint area alone. Test alternative arrangements, stacking, nesting and
unused regions; a small object inside a hollow large bowl can erase the constraint.
Give valid packing measurable clearance and test placement offsets. Large bodies
may need narrow grasp features instead of a tighter gripper requirement. Separate
these mechanics checks from robot access through the actual moving fixture.

## Observation and history

Enumerate policy observation keys/cameras separately from evaluator state. Body poses
behind an opaque container are privileged, even if available in simulation. An oracle
solver may use privileged state when labeled, but does not demonstrate policy memory
or perceptual classification. Keep hidden cues and branch IDs out of policy inputs.
Derive ordering/resource events from achieved state/contact with settling/debounce,
not commanded actions or script phase counters. Reset history every episode and
record/reconstruct it for replay; qpos/qvel do not store Python-side task history.
Decide from the contract whether violations invalidate the task or permit recovery.

## Failure attribution

Log seed/condition, phase, expected and chosen response, prerequisite values, achieved
state, diagnostic contacts and terminal reason. Use evidence-based labels:
- Decision: wrong branch, unmet prerequisite ignored, invalid order/allocation.
- Execution: valid intended action but failed grasp, slip, collision or timeout.
- Model/scoring: impossible positive case, ineffective block, leakage or false result.
- Unknown: insufficient evidence; retain the trace instead of guessing.

Report per-case counts and all attempts. Distinguish detection, recovery choice and
recovery completion; measure latency/false alarms when those events are defined.
