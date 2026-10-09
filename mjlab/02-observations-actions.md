# G1 专题：逐字段检查观测与动作

[首课](01-g1-task.md) · [随机化与课程](03-randomization-curriculum.md) · [PPO 数据路径](../learning/ppo-data-path.md)

**先修：** G1 首课、张量拼接、关节位置与速度单位。

**目标：** 能在固定的 G1 平地任务中定位每个观测字段、解释 actor/critic 差别，并把策略动作追到位置目标。

**范围：** mjlab `033ae22a2c7a30a25a6fa77b16c113ed88dd1b55`，`Mjlab-Velocity-Flat-Unitree-G1` 训练配置，未执行原生环境。下表是源码预期维度，E5 仍需读回实际 manager 的 shape、关节名与传感器匹配结果。

## 1. 先处理继承与覆盖

基础 velocity 配置定义 actor、critic；G1 rough 配置指定机器人与两足传感器；flat 再删除两组中的 `height_scan`，但保留 critic 的 `foot_height` 及足部接触信息。模型 XML 含 29 个具名普通关节，free joint 不计入这 29 个 action 维度。[观测定义](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L76-L151)、[flat 覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L188-L212)、[29 关节模型](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/asset_zoo/robots/unitree_g1/xmls/g1.xml)

## 2. Actor：99 维源码预期

索引使用 Python 半开区间，表内单位指归一化前的输入。N 表示环境数。

| 区间 | 原生 term | 维数 | 语义与单位 | 训练噪声 |
|---|---|---|---|---|
| `[0:3]` | `base_lin_vel` | 3 | `robot/imu_lin_vel`，m/s | uniform ±0.5 |
| `[3:6]` | `base_ang_vel` | 3 | `robot/imu_ang_vel`，rad/s | uniform ±0.2 |
| `[6:9]` | `projected_gravity` | 3 | 身体系重力方向，非 m/s² 加速度读数 | uniform ±0.05 |
| `[9:38]` | `joint_pos` | 29 | 带 encoder bias 的相对默认关节角，rad | uniform ±0.01 |
| `[38:67]` | `joint_vel` | 29 | 相对默认关节角速度，rad/s | uniform ±1.5 |
| `[67:96]` | `actions` | 29 | 原始策略 action，无量纲 | 未声明额外噪声 |
| `[96:99]` | `command` | 3 | twist 的 vx、vy、wz，m/s、m/s、rad/s | 未声明额外噪声 |

本 G1 actor **包含线速度**，不能套用“actor 一律看不到 base linear velocity”的泛化说法。关节字段内部顺序要以运行时解析的 joint names 为准，XML 的顺序只能用于源码核对，不能代替 actuator/关节映射的读回。

`joint_pos_rel(biased=True)` 读取 biased joint position 后减 default position；`last_action` 返回 action manager 的原始 action，不是乘尺度后的目标角。对一步返回的观测来说，它通常是刚刚执行的那个 action，成为下次决策的历史输入。[关节观测](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/observations.py#L51-L72)、[动作观测](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/observations.py#L80-L94)

## 3. Critic：111 维源码预期

Critic 前 99 维沿用相同 term 顺序，但 joint_pos 改成无偏真实相对关节角，整组关闭 corruption。再追加：

| 区间 | 原生 term | 维数 | 语义 |
|---|---|---|---|
| `[99:101]` | `foot_height` | 2 | 每只足相对地形的高度，m；不是每条扫描射线一维 |
| `[101:103]` | `foot_air_time` | 2 | 每足当前离地时间，s |
| `[103:105]` | `foot_contact` | 2 | 每足接触是否存在，0/1 |
| `[105:111]` | `foot_contact_forces` | 6 | 两足各 3 分量，先 flatten，再 `sign(f)*log1p(abs(f))` |

最后六维是原始力数值的非线性变换，不应在画图时直接标为未经变换的 N。两足配置使用 subtree 匹配、`reduce="netforce"` 和一个 slot；因此这里推导 2 × 3 分量。[G1 足部传感器](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L42-L81)、[foot observation 函数](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/mdp/observations.py#L14-L47)

部署通常只需要 actor；critic 的接触、离地时间或真值关节信息不能悄悄增加为 actor 的必需输入。模型导出时还要携带 actor 的归一化统计。

## 4. 观测处理顺序会改变含义

本快照 manager 的顺序为 term 计算 → noise → clip → scale → delay → history。无历史配置时不能凭经验乘上历史长度；启用 history 后，拼接宽度也要跟着变化。`compute(update_history=False)` 有缓存分支，重复读取不应重复推进历史。[观测处理](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/managers/observation_manager.py#L307-L382)

G1 actor/critic 都配置了算法侧 observation normalization。这和环境侧噪声、物理单位、编码器偏置是不同层，不能认为关闭 corruption 就关闭了 normalization。[G1 网络配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/rl_cfg.py#L12-L27)

## 5. Action 到位置目标

基础动作 scale 0.5 会被 G1 配置替换为 `G1_ACTION_SCALE`，它按 actuator 类型计算 `0.25 * effort_limit / stiffness`。因此每一维不一定用同一尺度；不能把它写成统一 0.5 rad。[G1 覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L86-L88)、[尺度生成](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/asset_zoo/robots/unitree_g1/g1_constants.py#L280-L288)

```text
processed = raw_action * per_joint_scale + default_joint_pos
target    = processed - encoder_bias
          → set_joint_position_target
          → 原生 position actuator → 实际受限的关节力矩
```

可选 action clip 在 processed 阶段执行；上图省略未启用的 clip。偏置的减法发生在 `JointPositionAction.apply_actions`，默认姿态来自本机器人配置选用的 `KNEES_BENT_KEYFRAME`，不能误用另一个 HOME 常量。[scale/offset/clip](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/actions/actions.py#L154-L163)、[位置目标](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/actions/actions.py#L212-L224)、[机器人初始配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/asset_zoo/robots/unitree_g1/g1_constants.py#L266-L277)

## 6. 练习与答案

1. 为什么把 `base_lin_vel` 删除后仍沿用旧 checkpoint 会出问题？

   **答案：** 观测从 99 变为 96 维，且后续列偏移；即使补零维持宽度，输入语义和归一化统计仍不同。
2. 为何 `foot_height` 在 flat 上还有意义？

   **答案：** flat 删除的是 terrain ray scan；每足对平面的高度仍是状态信息，critic 的对应 term 未被删除。
3. action=0 是否意味着无力矩或保持当前姿态？

   **答案：** 都不保证。它指向默认姿态减 encoder bias，position actuator 根据状态误差产生控制。
4. 为何 111 维 critic 输入不能直接当作 99 维 actor 的传感器需求？

   **答案：** 两组承担不同训练角色，额外真值/接触信息可以只供 critic 使用。需要单独设计 actor 的可部署输入契约。

**验证边界：** 已静态核对 XML 关节数量、配置字段与形状推导，实际张量排列和尺寸仍待原生环境读回。
