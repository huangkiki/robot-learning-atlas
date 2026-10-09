# Isaac Lab：任务工作流与仿真平台怎样配合

[首页](../README.md) · [源码地图](source-map.md) · [生命周期对照](../comparisons/lifecycle.md)

**先修：** 共同基础，建议先读 mjlab 首课。

**目标：** 区分 Manager-based 与 Direct；理解任务层和物理/渲染后端的分界。

**快照：** `develop@07daf4426dfa8dcb6d0753768890b4f60dc54f9e`。该提交 README 标记 3.0.0，目标 Isaac Sim 6.1，并提示开发中可能有破坏性变化；本课不把开发分支当作稳定安装推荐。[版本说明](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/README.md#L5-L28)

## 两条原生任务路径

| 路径 | 组织方式 | 阅读问题 |
|---|---|---|
| `ManagerBasedRLEnv` | actions、observations、rewards、terminations 等由 managers 组合 | term 如何注册和执行，状态依赖如何表达？ |
| `DirectRLEnv` | 子类实现动作处理、观测、奖励和结束等方法 | 任务逻辑集中在何处，哪些生命周期仍由基类负责？ |

Direct 并不意味着任意跳过 reset 或仿真同步。Manager-based 也不保证所有任务都应拆成相同的 terms。先根据已有任务代码理解设计，再做选择。源码：[ManagerBasedRLEnv](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L25-L38)、[DirectRLEnv](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/direct_rl_env.py#L37-L51)。

注意大小写：这里是 `ManagerBasedRLEnv`；mjlab 中是 `ManagerBasedRlEnv`。保留原名有助于准确搜索代码。

## 当前 step 有一个后端分支

在该快照，`steps_per_call` 由 `_physics_handles_decimation` 决定：

- 环境持有 decimation 时，每次 Python 循环推进一个物理步。
- 后端持有 decimation 时，一次物理调用承担多个子步，循环次数相应减少。
- scene 更新使用的 dt 也乘以 `steps_per_call`。

因此不能通过 Python 中 `sim.step` 的调用次数直接推断策略频率。先读 `step_dt` 的配置语义，再读后端接口。来源：[后端接管 decimation](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L216-L232)。本期没有验证各后端的运行能力或性能。

## reset 与终止观测

这条 manager 路径计算 termination/reward，再重置结束行，之后更新 command/interval event，最终计算观测。若启用 `compute_final_obs`，在自动重置前保存 `extras["final_obs"]`。读取者仍须使用结束 mask 解释相应行。来源：[结束与 final_obs](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L233-L284)。

与 mjlab 对照时，应指出事件的前后顺序、刷新与传感器时刻；不能只因类名相似就移植全部假设。

## 安装与学习边界

先选兼容的发布版本或明确的开发快照，核对物理/渲染后端、Python、宿主与依赖。当前源码中的后端抽象不表示每种后端、渲染器与任务组合都已可用。安装应遵循所选版本的官方指南，本期只提供源码阅读，不给一条混合版本的安装命令。

## 练习与答案

1. Direct 是否意味着算法直接操作物理引擎、没有环境基类？

   **答案：** 否。`DirectRLEnv` 仍管理交互生命周期，具体任务实现相应钩子。
2. 看到 `decimation=4`，Python 循环是否一定迭代四次？

   **答案：** 当前实现不一定；后端接管时循环次数不同。
3. 有 `final_obs` 配置项，是否能假设所有任务都默认返回它？

   **答案：** 不能。要核对配置、工作流和实际消费者。

**本期状态：** 导读和源码地图完成；完整原生任务、安装验证与训练评估留待 E2/E5。
