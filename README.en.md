# Robot Learning Atlas

Learn how robot learning frameworks turn simulation into tasks, observations, actions, rewards, policy training, and evaluation.

[中文](README.md) · [Curriculum](docs/curriculum.md) · [Foundations](foundations/README.md) · [Progress](docs/roadmap.md) · [GitHub Project](https://github.com/users/huangkiki/projects/3)

The suggested sequence is **mjlab → Isaac Lab → UniLab**. Follow one concrete task from its CLI and configuration into the environment, runner, and policy playback; then compare the other frameworks using their own APIs. The detailed lessons are currently written in Chinese. This English entry mirrors their actual coverage.

| Framework / topic | Delivered content |
|---|---|
| [Foundations](foundations/README.md) | Layer boundaries, time and batching, termination and reset |
| [mjlab](mjlab/README.md) | G1 task, field-by-field observations/actions, randomization and curriculum |
| [Isaac Lab](isaaclab/README.md) | Cartpole registration, configuration, step/reset, training API and manager/direct comparison |
| [UniLab](unilab/README.md) | Go2 configuration overrides, backend construction, Torch state and PPO adapter |
| [PPO](learning/ppo-data-path.md) | Pinned RSL-RL 5.5.1 storage, timeout handling, GAE and losses |
| [Comparison](comparisons/lifecycle.md) | Time, return types, autoreset and terminal observations |

Start with the [mjlab lesson](mjlab/01-g1-task.md). Its [source inspection example](mjlab/examples/inspect_g1.py) reads pinned Git blobs using Python's AST, without importing mjlab or starting a GPU. It derives 50 Hz control, 1000 steps per configured episode and rollout sample counts.

Two routes organize the planned curriculum: **A**, author and operate tasks; **B**, understand configuration, lifecycle, managers, data movement and the learner interface. E0–E4 cover foundations, native task walkthroughs for all three frameworks, and mjlab observation/action, randomization/curriculum and PPO internals. E5 native execution and short training are deferred by agreement. E6 migration, independent evaluation and final course review remain pending.

[Sim Atlas](https://github.com/huangkiki/sim-atlas) teaches physics engines and native simulation APIs. This companion repository teaches the task and learning layers above them. All three frameworks initially share this repository.

The source snapshot was reviewed on 2026-10-09; commits and file digests are in [sources.json](docs/sources.json). [Validation](docs/validation.md) records source review and execution of the course's static inspection and scalar GAE examples. Native simulation, training, evaluation, performance and robot deployment have not been validated here.

Checks: `python3 scripts/check_docs.py`, `python3 learning/examples/rollout_math.py`, `python3 -m compileall -q scripts mjlab/examples learning/examples`, and `git diff --check`.

This independent community course is not affiliated with the upstream projects. Original text and scripts use [Apache-2.0](LICENSE); see [attribution](THIRD_PARTY.md) and [contributing](CONTRIBUTING.md).
