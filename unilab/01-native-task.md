# UniLab 首课：Go2 的配置如何变成一条学习转移

[导读](README.md) · [源码地图](source-map.md) · [生命周期对照](../comparisons/lifecycle.md)

**先修：** mjlab 首课、Isaac Lab 的 manager 调用链、字典与张量的批量维度。

**目标：** 选定 `Go2JoystickFlat + mujoco + PPO`，从 Hydra owner 配置读到注册工厂、后端调用、`TorchEnvState` 和 learner adapter。

**快照：** `cbafb5071fb0ea2d7322e1b0b648f8819b2a7499`。本课没有启动原生任务，所有数值是配置推导，不是实测速度、训练成功率或后端兼容性结论。

## 1. 配置不是一个 YAML 文件

```text
conf/ppo/config.yaml
  → task: go2_joystick_flat/mujoco
      → /task/go2_joystick_flat/base
      → mujoco owner 的覆盖值
  → 命令行 overrides
  → BackendAdapter：reward + env → env_cfg_override
  → registry.make → typed env config → validate → env factory
```

基础 PPO 文件先包含 `_self_` 再包含 task；MuJoCo owner 则先包含 task base 再 `_self_`。因此最终值不能只读最外层文件：

| 字段 | PPO 基础值 | MuJoCo owner 覆盖后 |
|---|---|---|
| `algo.num_envs` | 4096 | 1024 |
| `algo.max_iterations` | 101 | 151 |
| `algo.num_steps_per_env` | 24 | 保留 24 |
| actor 输入组 | `policy` | `actor` |
| critic 输入组 | 由配置/算法解析 | 显式 `critic` |
| actor/critic normalization | false | true |
| `training.collector_tensor_device` | cpu | 此 owner 未覆盖 |

来源：[PPO 基础配置](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/conf/ppo/config.yaml#L1-L79)、[MuJoCo owner](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/conf/ppo/task/go2_joystick_flat/mujoco.yaml#L1-L29)。

`BackendAdapter.build_task_env_cfg_override()` 将根 `reward` 路由到任务声明的奖励字段，再并入 `env`。若根 reward 与对应 env 字段重复声明，它会报错，不能理解成“后写的奖励随意覆盖前者”。[配置适配边界](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/config_adapter.py#L33-L48)

注册表把 `Go2JoystickFlat` 关联到 `ManagerBasedRlEnvCfg` 和 `make_manager_based_rl_env`。`registry.make` 实例化配置、应用 overrides、验证，再选 backend 对应工厂，且要求返回 `TorchEnv`。注册成功只说明这条构造路径被声明。[任务注册](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/tasks/locomotion/go2/__init__.py#L1-L10)、[registry.make](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/registry.py#L266-L317)

## 2. 明确任务、控制与时间

[Go2 共同任务声明](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/conf/ppo/task/go2_joystick_flat/base.yaml#L4-L115) 定义平地模型、home keyframe、12 个关节、12 个 actuator，以及：

| 配置 | 值 | 推导/含义 |
|---|---|---|
| `sim_dt` | 0.01 s | 名义 100 Hz 物理步 |
| `ctrl_dt` | 0.02 s | 名义 50 Hz 策略步 |
| `sim_substeps` | 由时间比确定 | 每策略步 2 个物理子步 |
| `max_episode_seconds` | 20 s | 上限 1000 策略步，提前终止除外 |
| position action | scale 0.25，default offset 开启 | 原生关节位置 action 配置；不是直接力矩输入 |
| twist command | vx [-0.6,1.0]，vy [-0.4,0.4]，wz [-0.8,0.8] | 线速度 m/s，角速度 rad/s |
| command 重采样区间 | [20,20] s | 不等同于每步产生新随机命令 |
| PPO batch | 1024 × 24 | 24,576 条转移/迭代，单环境覆盖 0.48 s |

配置验证要求 `ctrl_dt/sim_dt` 是整数倍，不能随便把两个时间参数独立修改。[时间比验证](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L195-L214)。上限计算也可在 [learner adapter](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/rl/vec_env.py#L53-L70) 中复核。

任务声明的关节顺序为 FL、FR、RL、RR，actuator 列表却按 FR、FL、RR、RL 排列。迁移 action 或观测时必须沿名字和原生解析结果建立映射，不能按“每腿三个数”直接复制列；正则 `actuator_names=[".*"]` 也不能代替解析后的名字记录。

## 3. 后端在哪里接入

环境工厂将 scene、环境数、`sim_dt` 和相关能力参数传给 UniLab 的 `create_backend`；后者准备资产，最终调用外部 `unisim.create_backend(...)`，再将对象交给 `ManagerBasedRlEnv`。本课证据到这一正式接口为止，没有阅读或验证此快照所安装的 UniSim 物理求解内部实现。[环境工厂](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L1780-L1806)、[后端边界](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/backend_factory.py#L284-L350)

因此，“learner 在 CUDA 上”“状态返回 torch.Tensor”都不能证明 MuJoCo 物理在 GPU 上执行。PPO 默认配置明确保留 `collector_tensor_device: cpu`；adapter 会在环境与 learner 设备间转换张量。实际数据搬运次数与开销需要运行测量。

## 4. 一次 step 怎样组装状态

公共返回值是 `TorchEnvState`，并非 Gym 五元组：

| 字段 | 本课应怎样理解 |
|---|---|
| `obs` | 观测组字典，包含批量张量 |
| `reward` | 本策略步奖励 |
| `terminated` / `truncated` | 失败/任务结束与时间截断分开保留 |
| `info` | 日志、计数、时序等附加信息 |
| `final_observation` | 自动重置前的终止观测，按 done mask 解释有效行 |

来源：[状态类型](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L45-L61)。

调用顺序是：验证动作 → `apply_action` → `backend.step_tensor(ctrl, sim_substeps)` → `update_state` → 更新步数/截断 → 若启用 autoreset 则重置结束行。[TorchEnv.step](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L256-L315)

Manager 的动作阶段处理 action 并写出后端控制；物理推进后主动使旧的状态读取缓存失效，建立新的读取作用域。任务阶段先算 termination/reward，再处理 step/interval events、command 和 observation。发生状态写入后还要刷新读取边界，不能让 reward 或 observation 引用上一物理步的缓存。[动作和状态刷新](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L1185-L1213)、[任务更新](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L1225-L1327)

这与 Isaac Lab 的 reset 前后顺序不能仅靠同名 manager 推断一致。也不要拿 `step_core_ms` 单个字段当完整物理性能：GPU 排队、同步、reset 和数据转换可能出现在其他阶段，源代码本身已经区分了部分计时归属。

### 自动 reset 后保留了什么

`_reset_done_envs` 先把结束行当前观测写入 `final_observation`，然后 reset，并把 reset 后的观测写回公开 `obs`。因此，同一步返回的 reward/done 描述刚结束的转移，而结束行的 `obs` 已属于新回合。final buffer 使用复用的 scratch 存储；要长期保存转移，应按所需行复制数据，不能把可变状态对象引用直接塞进自己的历史列表。[终止观测与重置](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L482-L563)

## 5. 从 manager 组名到 learner 组名

这条链上有三个命名层：

```text
任务配置中的 policy / critic
  → TorchEnvState.obs 中的 obs / critic
  → TensorDict 中的 actor、policy / critic
  → algo.obs_groups 为 actor 选 actor，为 critic 选 critic
```

`_validate_observation_mapping` 把 `policy_observation_group` 指向的组映射为 `obs`；learner adapter 再把 `obs["obs"]` 放进 `actor`，并构造 `policy`。本任务 actor 使用角速度、重力投影、关节相对位置/速度、上一动作、twist command、四足 gait phase；critic 额外包含局部线速度。训练期 critic 的额外输入不能泄漏成部署时 actor 的必需传感器。[任务观测声明](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/conf/ppo/task/go2_joystick_flat/base.yaml#L40-L92)、[环境组映射](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L1075-L1097)、[adapter 组映射](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/rl/vec_env.py#L94-L116)

`RslRlVecEnvAdapter.step` 将 action 转到环境设备上的连续 float32 张量，再把结果转到 learner 设备；合并 done，并在存在结束行时转发 `time_outs`。这段 adapter 没有把 `state.final_observation` 送入返回的 infos，所以“环境保存了 final observation”与“当前 PPO 消费了它”是两件需分别核对的事实。[adapter.step](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/rl/vec_env.py#L118-L142)

本课选的是 `train_rsl_rl.py` 的单进程 PPO 路径：`create_env` → `RslRlVecEnvAdapter` → `OnPolicyRunner`。其他 uni_rl collector 使用可序列化的 `registry_env_factory` 注入环境；它负责在 spawn 子进程重新初始化 registry，不能把那条多进程路径无条件套到本课的 PPO 入口。[PPO runner 创建](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/scripts/train_rsl_rl.py#L553-L597)、[collector 环境工厂](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/env_factory.py#L26-L86)

## 6. 后续原生验收的候选命令

包声明的 CLI 名称为 `train`，三个选择参数分别是算法、任务 owner 名和仿真后端：

```bash
train --algo ppo --task go2_joystick_flat --sim mujoco \
  algo.num_envs=64 algo.max_iterations=2 training.no_play=true
```

此命令只按源码核对，未执行。选择 `training.no_play=true` 避免短训练后自动接上回放；后续回放应显式选择本次实际产出的 checkpoint，并冻结评估配置。实际安装须同时记录 UniLab、UniSim、MuJoCo、RSL-RL、Torch 和资产版本，不能只记录本课的 UniLab Git SHA。[包入口](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/pyproject.toml#L33-L69)、[CLI 参数](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/cli.py#L525-L578)、[回放开关消费](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/scripts/train_rsl_rl.py#L675-L686)

## 7. 练习与答案

1. 只读 PPO 基础配置，为什么会把默认每轮转移数算成 98,304？

   **答案：** 忽略了 MuJoCo owner 将环境数覆盖成 1024。所选组合为 1024 × 24 = 24,576。
2. 一个已结束的环境行返回 `obs`，它一定是终止状态吗？

   **答案：** autoreset 开启时不是；结束前的观测在 `final_observation` 的对应行，且必须核对 adapter 是否消费。
3. 为什么不能把配置中的 `policy` 字符串直接当成 actor 最终接收的 TensorDict key？

   **答案：** manager → TorchEnvState → learner adapter 有显式映射。本 owner 最后为 actor 指定的是 `actor`。
4. 把 learner 的 device 改成 CUDA，是否就完成了 GPU 物理迁移？

   **答案：** 没有。要分别检查物理后端、环境张量设备、collector 和 learner；本课不报告运行或加速结果。

**交付边界：** 完成配置覆盖、构造、step/reset 和 learner 边界的源码课程。原生运行、数值等价、长期训练与跨后端迁移效果仍未验证。
