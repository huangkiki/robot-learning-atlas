# G1 专题：随机化与课程分别在何时生效

[观测与动作](02-observations-actions.md) · [PPO 数据路径](../learning/ppo-data-path.md)

**先修：** G1 的 step/reset、观测与动作。

**目标：** 区分 startup、reset、interval 和 curriculum；沿着触发点解释它们改了什么状态，而不是只罗列随机范围。

**快照与证据：** 同一 mjlab 固定提交，G1 flat 训练配置。没有运行随机化实验，也没有验证训练鲁棒性。

## 1. 三种 event 不是同一个时钟

| 原生事件 | mode | 当前配置 | 影响与持久性 |
|---|---|---|---|
| `foot_friction` | startup | 绝对值 [0.3,1.2]，脚部 geom shared random | 环境启动时分配物理参数；不因每次 episode reset 自动重新采样 |
| `encoder_bias` | startup | [-0.015,0.015] rad | 影响 actor 的 biased joint_pos 与 action 的目标偏置校正 |
| `base_com` | startup | x/y ±0.025 m，z ±0.03 m，加法 | G1 对应 `torso_link`，改变物理模型参数 |
| `reset_base` | reset | xy ±0.5 m，z [0.01,0.05] m，yaw ±3.14 rad | 在指定重置行上改变初始 root 状态 |
| `reset_robot_joints` | reset | position/velocity offset 都为 [0,0] | 恢复默认关节状态；本项不是非零关节随机化 |
| `push_robot` | interval | 每 1–3 s，设置速度扰动 | 改变当前运动状态，不是施加一个“持续 1–3 s 的恒定力” |

来源：[reset events](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L203-L225)、[interval/startup events](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L226-L271)、[G1 目标实体覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L96-L97)。`shared_random` 的脚部一致性不应推断成所有环境副本共享同一个抽样结果。

环境加载 managers 后调用 startup；每次 step 的 interval 分支传入 `step_dt`；`_reset_idx` 只对需要重置的行应用 reset。[startup 触发](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L354-L356)、[interval 触发](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L464-L465)、[reset 生命周期](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L580-L618)。非全局 interval 的剩余时间还会在 reset 时重新采样，因此 episode 边界也参与这个事件时钟。[event reset](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/managers/event_manager.py#L217-L238)

## 2. Flat 还保留命令课程

基础配置包含 `terrain_levels` 和 `command_vel`。G1 flat 移除了地形 generator 与 `terrain_levels`，但训练模式仍保留 `command_vel`：

| `common_step_counter` 阈值 | vx 范围（m/s） | wz 范围（rad/s） |
|---|---|---|
| 0 | [-1.0,1.0] | [-0.5,0.5] |
| 5000 × 24 = 120,000 | [-1.5,2.0] | [-0.7,0.7] |
| 10000 × 24 = 240,000 | [-2.0,3.0] | 未覆盖，保留上一阶段 |

来源：[课程配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L396-L412)、[flat 删除地形课程](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L197-L212)。

阈值单位是向量环境的公共策略步数，**不是环境总转移条数，也不是 wall time**。在每迭代固定 24 步且计数从零开始的设定下，它们对应约 5000/10000 轮采样；改变 rollout 长度不会自动改写这里硬编码的乘积。

实际执行在 `_reset_idx` 的开头。`commands_vel` 检查公共计数，并对所有已达到的 stage 顺序覆盖 command 的范围。因此阈值跨过后要等下一次相应 reset 执行；它修改的是采样范围，不保证所有存量 command 当场同时改变。[课程触发位置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L580-L589)、[commands_vel 实现](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/mdp/curriculums.py#L106-L131)

Rough 的 terrain curriculum 则根据实际位移、命令要求位移与剩余时间决定升降级，并保护初始 reset 不产生虚假的升级。本 flat 案例没有运行这项课程。[terrain_levels_vel](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/mdp/curriculums.py#L25-L81)

## 3. Play 配置不是冻结评估协议

G1 play 会关闭 actor corruption、移除 push、清空 curriculum、把 episode 上限设为很大的值；flat play 又覆盖部分速度范围。因此它是方便交互查看的配置，不能把其平均 reward 直接与训练配置比较。[rough play 覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L163-L183)、[flat play 覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L214-L218)

后续独立评估至少需要固定配置、seed 集合、episode 数或时长、动作/观测处理、成功判据以及 startup 随机参数的分布；并保存失败样本。当前 E5/E6 的运行验收留到后续，不能以“有这些配置”代替 sim-to-real 鲁棒性结果。

## 4. 练习与答案

1. 把摩擦事件从 startup 改成 reset 是否只是改一个字符串？

   **答案：** 行为上改变了每个 episode 的参数分布和后端模型更新频率，还需检查该随机化操作是否支持该模式及正确刷新模型。
2. 4096 环境跑一步，command curriculum 计数增加 4096 吗？

   **答案：** 不会；公共策略步计数增加 1，而 rollout 中转移条数增加 4096。
3. 第三个 stage 未写 wz，是否意味着将角速度范围清零？

   **答案：** 否。函数只覆盖显式给出的键，保留第二阶段的 [-0.7,0.7]。
4. 为什么 play 没摔倒不能证明策略通过扰动验收？

   **答案：** play 已移除 push 并关闭噪声，实验分布不同；需要冻结并执行独立协议。
