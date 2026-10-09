# 同一个 step/reset 问题，三个不同契约

[首页](../README.md) · [共同基础](../foundations/README.md) · [完整版本](../docs/sources.json)

**先修：** mjlab 首课。

**目标：** 迁移任务之前，把时间、返回数据和回合边界对齐。

**范围：** 下表比较本课程固定提交的 manager 路径，不推广到同框架所有版本和 Direct/多智能体路径。

| 问题 | mjlab | Isaac Lab | UniLab |
|---|---|---|---|
| 本表对象 | `ManagerBasedRlEnv` | `ManagerBasedRLEnv` | `ManagerBasedRlEnv(TorchEnv)` |
| 环境时长 | `sim.mujoco.timestep × decimation` | `sim.dt × decimation` | `ctrl_dt`；子步由 `ctrl_dt/sim_dt` 计算 |
| 物理推进位置 | 环境显式循环 `decimation` 次 | 环境或后端持有 decimation | 父类调用 `backend.step_tensor(ctrl, sim_substeps)` |
| 环境返回 | 五元组 | 五元组 | `TorchEnvState` |
| 默认自动重置后的 obs | 结束行是重置后观测 | 结束行是重置后观测 | 结束行是重置后观测 |
| 终止观测入口 | 本课路径不另行返回；手动 reset 模式需专用调用循环 | 启用 `compute_final_obs` 时写 `extras["final_obs"]` | `state.final_observation`；按结束 mask 取有效行 |
| 本表证据 | 固定源码 | 固定源码 | 固定源码 |

源码入口：[mjlab step](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L386-L510)；[Isaac Lab step](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L177-L286)；[UniLab step](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L256-L349) 和 [UniLab reset](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L482-L529)。

## 相同名称不保证相同执行阶段

mjlab 在 reward/termination 后、自动重置前执行 step/interval 事件；Isaac Lab 这条 manager 路径先自动重置，随后更新 command/interval event，最后计算观测。UniLab 将任务状态更新与父类自动重置拆开，必须一起阅读。

如果事件修改速度，先问奖励读取的是扰动前还是扰动后状态、返回观测是否看到扰动、重置是否覆盖扰动。仅复制配置名称无法回答这些问题。

## 三步判断一个迁移是否保留了任务

1. **接口对应：** action/obs 的形状、顺序、单位、device、归一化、裁剪和历史长度一致吗？
2. **时间对应：** 物理步、控制步、传感器采样、奖励缩放、命令更新、终止和 reset 的先后关系一致吗？
3. **物理与评估对应：** 机器人参数、执行器、接触模型、命令分布、随机化和独立评估协议一致吗？

本课程目前帮助完成源码层面的前两步检查；没有跨框架数值等价或训练效果的实测结论。

## 练习与答案

- 将 `obs, reward, terminated, truncated, info = env.step(action)` 原样移到 UniLab 可行吗？

  **答案：** 本表版本返回状态对象，先查看 adapter；即使解包问题解决，也仍需核对回合语义。
- 自动重置后，能否对所有返回 obs 直接计算上一回合终止值？

  **答案：** 不可以。选择正确的终止观测通道和有效行，再检查算法如何处理截断。
- 两个框架都声明 50 Hz，是否说明它们观察到完全相同的状态？

  **答案：** 不说明。物理求解、传感器和派生量刷新时刻都可能不同。
