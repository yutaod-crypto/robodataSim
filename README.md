# robodataSim

Reusable robosuite / MuJoCo task-building skill. Start with [SKILL.md](SKILL.md).

Includes object/mechanism design standards, task contracts, randomized reset layouts,
controller validation and demonstration replay guidance. Simulation datasets are not included.

The skill's internal identifier remains `robosuite-task-builder`.
To synchronize from its source checkout, run `python3 scripts/sync_github.py`;
add `--watch` to publish after saved edits remain unchanged for 10 seconds.
The watcher must stay running and have GitHub authentication/network access.
