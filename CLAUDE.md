# CLAUDE.md

Guidance for Claude Code working on `urdf_validator`.

## Source of Truth

The PRD (`urdf_validator_PRD.md`) is the authoritative specification for what to build, in what order, and to what standard. Read it before making any non-trivial decision. Do not infer requirements from the codebase alone.

## How to Work

**Stay in milestone scope.** The PRD defines six monthly milestones (v0.1–v1.0). Only implement what belongs to the current milestone. Do not stub, scaffold, or partially implement future phases — leave them absent entirely. When in doubt about scope, check the milestone table in PRD §6.

**Never crash on bad input.** The no-crash guarantee is the single most important correctness property of this tool. Every failure mode — malformed XML, missing mesh, invalid tensor, corrupt file — must produce a structured entry in `ValidationReport`, not an unhandled exception. Wrap all parsing and computation in try/except. Populate `unknowns` rather than propagating.

**Label confidence explicitly.** Every physics estimate must carry one of: `exact / estimated / guessed / missing`. Never present a derived value as ground truth. The tool's credibility with the ROS community depends on this honesty.

**Keep dependencies minimal and clean.** Core pipeline: `urdf_parser_py`, `numpy`, `shapely`, `ikpy` — that's it. `mujoco` must be a lazy import inside `integrations/`, never a hard requirement. No GPL-licensed packages in the core pipeline. `xacro` is optional; its absence must degrade gracefully.

**Exit codes must be CI-compatible.** Exit non-zero on any CRITICAL or FAIL status. This requires no flags — it is the default behaviour.

## Agentic Workflow
Allow maximum of 3 sub agents for each sessions. Ensure sub agents focuses on catching bugs and logic failures.

## Github specific
No authorship or attribution in git comments

## How to Verify Your Work

The acceptance standard is correct, non-crashing output on all six reference URDFs. If the tool crashes on any one of them, it is not releasable. Run these before considering any milestone complete.

| URDF | Robot Type |
|---|---|
| `fetch_robot` | Wheeled mobile manipulator (arm + wheeled base) |
| `PR2` | Dual-arm wheeled robot, 50+ links |
| `ANYmal` | Legged quadruped |
| `Spot (unofficial)` | Legged quadruped, non-standard naming |
| `TurtleBot3` | Simple differential-drive wheeled robot |
| `Franka Panda` | Fixed-base robot arm, no mobile base |

For physics computations (gravity torque, COM), verify against MuJoCo ground truth where possible. The working tolerance is 10%, to be validated empirically on `fetch_robot` in Month 2.