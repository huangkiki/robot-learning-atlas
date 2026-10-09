# 第 1 课：沿 G1 平地速度任务读通 mjlab

[导读](README.md) · [源码地图](source-map.md) · [共同基础](../foundations/README.md) · [下一步对照](../comparisons/lifecycle.md)

**先修：** Python dataclass/dict、张量的 batch 维、[共同基础](../foundations/README.md)。

**目标：** 从一个任务 ID 找到最终配置；解释一次环境 step 的顺序；识别训练、回放与评估的边界。

**固定版本：** `033ae22a2c7a30a25a6fa77b16c113ed88dd1b55`。文中的数值与顺序只描述这个快照。

**证据：** 源码阅读与静态配置脚本已执行；本页原生安装、播放和训练命令尚未执行。

## 1. 从一条命令进入

上游的任务名是 `Mjlab-Velocity-Flat-Unitree-G1`。其含义是让 G1 跟踪速度命令，而不是复现动作捕捉轨迹。训练入口示意：

```bash
uv run train Mjlab-Velocity-Flat-Unitree-G1 --env.scene.num-envs 4096
```

命令需要在正确安装的固定源码仓中执行，不在本课程仓执行。它会开始真实训练；阅读课程无需运行它。CLI 默认日志方式涉及 W&B，运行前应按下面的本地日志示例明确配置。

[pyproject 脚本入口](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/pyproject.toml#L60-L67) 把 `train` 指向 `mjlab.scripts.train:main`。[main](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/scripts/train.py#L230-L258) 先导入任务包，再解析任务 ID，再以该任务的配置为默认值解析其余覆盖项。

`--env.scene.num-envs 4096` 覆盖场景环境数，不会直接改写 `num_steps_per_env`、物理步长或 episode 时长。

## 2. 注册的是四件东西

[G1 flat 注册](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/__init__.py#L19-L24) 绑定：

| 字段 | 本任务的值/来源 | 作用 |
|---|---|---|
| `env_cfg` | `unitree_g1_flat_env_cfg()` | 训练用任务配置 |
| `play_env_cfg` | `unitree_g1_flat_env_cfg(play=True)` | 交互回放用配置 |
| `rl_cfg` | `unitree_g1_ppo_runner_cfg()` | actor、critic、PPO 和 runner 参数 |
| `runner_cls` | `VelocityOnPolicyRunner` | 训练运行器和任务专用保存逻辑 |

注册表返回配置的深拷贝，避免一次 CLI 覆盖污染后续读取。来源：[load_env_cfg / load_rl_cfg](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/registry.py#L48-L65)。

不要把任务注册误读成 Gym 的所有行为都已自动具备；沿本框架自己的创建入口继续读。

## 3. 最终配置是逐层修改的结果

`make_velocity_env_cfg() → unitree_g1_rough_env_cfg() → unitree_g1_flat_env_cfg()`。

基础配置声明观测、动作、速度命令、事件、奖励、终止和课程。G1 rough 配置放入机器人、接触传感器和动作尺度等机器人特有内容。flat 配置再把地形改为平面、移除 terrain scan 观测和地形边界终止、移除地形等级课程。它仍保留其他观测、奖励与命令课程。

| 参数 | 来源与值 | 推导 |
|---|---|---|
| `sim.mujoco.timestep` | 基础配置 `0.005` s | 200 Hz 物理步进 |
| `decimation` | 基础配置 `4` | 一次策略动作推进四次物理步 |
| `step_dt` | 环境属性，二者相乘 | `0.02` s，50 Hz |
| `episode_length_s` | 训练配置 `20.0` s | `ceil(20/0.02)=1000` 步 |
| `scene.num_envs` | 基础默认 `1`；示例 CLI 覆盖为 `4096` | 并行批量 |
| `num_steps_per_env` | G1 runner 配置 `24` | 每轮每环境 24 条转移 |
| `max_iterations` | G1 runner 配置 `30_000` | 配置上限；不代表实际跑过或足以收敛 |

来源：[基础配置尾部](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L418-L456)、[flat 覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L188-L220)、[runner 配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/rl_cfg.py#L42-L46)、[环境时间属性](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L263-L289)。

对于示例的 4096 个环境，每轮采样数是 `4096×24=98,304`；每个环境推进 `24×0.02=0.48` 秒。并行计算的墙钟耗时需要独立测量。

## 4. 用纯 Python 复核这些数值

准备固定源码快照，课程仓与 mjlab 目录并列：

```bash
git clone https://github.com/mujocolab/mjlab.git ../mjlab
git -C ../mjlab checkout --detach 033ae22a2c7a30a25a6fa77b16c113ed88dd1b55
python3 mjlab/examples/inspect_g1.py --source ../mjlab --num-envs 4096
```

若已有阅读仓，可直接传其路径；脚本要求 HEAD 与固定提交一致，读取提交中的 Git blob。它使用 AST 读取选定构造调用中的字面量，不执行配置工厂，不解析任意用户覆盖，也不证明框架可以安装。它还核对相关源文件摘要，防止用不同版本套用本课结论。

预期关键输出：

```text
physics_dt_s: 0.005
decimation: 4
policy_dt_s: 0.02
policy_hz: 50.0
episode_steps: 1000
rollout_steps_per_env: 24
transitions_per_rollout: 98304
simulated_seconds_per_env_per_rollout: 0.48
```

完整结果带 `evidence: static-source-analysis`。本课实跑结果见 [记录](../docs/evidence/mjlab-g1-static.json)。

## 5. action 先变成目标，才进入物理

基础任务选用 `JointPositionActionCfg`，并开启 `use_default_offset`；G1 配置把 scale 改成 `G1_ACTION_SCALE`。因此不能把基础配置里的 0.5 当作 G1 最终动作尺度。

动作处理依次包括 scale/offset、可选裁剪；应用关节位置动作时再扣除 encoder bias，调用 `set_joint_position_target`。其输出是控制目标，实际执行器力还由执行器实现与状态决定。来源：[G1 动作尺度覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L86-L88)、[动作处理](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/actions/actions.py#L154-L164)、[位置目标应用](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/actions/actions.py#L212-L224)。

对观察到的“零 action 仍有运动”，先检查初始状态、默认目标、执行器和重力；不能直接判断策略或接口有 bug。

## 6. 一次 step 的真实顺序

以默认 `auto_reset=True` 为主线，按 [ManagerBasedRlEnv.step](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L386-L510) 阅读：

1. 检查手动重置约束，清理本步日志，处理 action。
2. 循环 `decimation` 次：应用动作 → 写入仿真 → `sim.step()` → 更新 scene → 子步指标。
3. 增加回合和全局环境步计数。
4. 计算 termination，再计算 reward 和指标。
5. 对当前步状态执行 step/interval 事件。
6. 选出结束的环境行，执行 `_reset_idx` 并写入重置状态。
7. 对全部环境做一次 `sim.forward()`，更新派生物理量。
8. 更新命令；刚重置行传 `dt=0`，其他行传 `step_dt`。
9. `sim.sense()`，计算并更新观测历史，记录输出。
10. 返回 `obs, reward, terminated, truncated, extras`。

这份实现有一个重要时序选择：reward/termination 位于额外 `forward()` 之前。源码说明某些派生量可能比积分后的 `qpos/qvel` 落后一个物理子步。课程据此标记采样时刻；这里没有实验支持“影响一定可忽略”。读每个 reward 时还要区分它读取的是原始状态还是派生量。

`forward()` 与 `step()` 职责不同；这一处刷新不应被算成又推进了一个物理步。事件和重置写入的状态也在这次刷新之后进入观测。

## 7. 奖励和日志数值可能不同

[RewardManager.compute](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/managers/reward_manager.py#L116-L135) 把 term 返回值乘权重，再按 `scale_rewards_by_dt` 决定是否乘 `step_dt`。它同时维护训练返回的 reward、回合累计量以及用于显示的 term 值，后者并不一定含同样的 dt 因子。

该函数还使用 `nan_to_num` 清理每项 reward 的 NaN/Inf。因此“奖励有限”本身不足以证明物理状态健康。需要结合状态、NaN guard 与具体运行证据判断。

不要只复制一个奖励权重就声称跨框架等价；至少对齐 term 输入、坐标、单位、时间缩放、命令更新和终止时刻。

## 8. 结束回合的那一行观测属于谁

默认自动重置时，reward 和结束标记描述上一回合最后一次转移，而结束行的返回 observation 已经是新回合状态。此版 mjlab 的这条返回路径没有另行输出 `final_observation` 字段；不能套用其他框架的键名。

`auto_reset=False` 时跳过自动重置，调用者可读取该步观测，但必须在下一次 `step` 前为结束行调用 `reset(env_ids=...)`。官方自带训练路径使用的 runner 不负责这套手动重置流程，所以不能只改一个开关就继续沿用原训练循环。来源：[auto_reset 契约](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L144-L157)。

`RslRlVecEnvWrapper` 将 `terminated | truncated` 合成整数 `dones`，并在非有限时域配置下把 `truncated` 放入 `extras["time_outs"]`。这是信息传递接口；bootstrap 的具体计算由算法消费者决定。[wrapper 转换](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/rl/vecenv_wrapper.py#L77-L90)

## 9. 从环境接到训练，再回到播放

[训练装配](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/scripts/train.py#L110-L186) 创建环境，经可选录像包装后接到 `RslRlVecEnvWrapper`，保存 env/agent 配置，再实例化任务 runner 并调用 `runner.learn(...)`。

本任务的继承关系为：

```text
VelocityOnPolicyRunner → MjlabOnPolicyRunner → rsl_rl.runners.OnPolicyRunner
```

配置项来自本仓；PPO 训练循环属于外部依赖。固定 pyproject 将 `rsl-rl-lib` 设为 `5.5.1`，课程尚未逐行审计该依赖的更新循环。[算法库依赖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/pyproject.toml#L50)、[基础 runner](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/rl/runner.py#L11-L37)。

以下是**尚未执行的原生操作配方**，用于后续 E5 运行验收。先在隔离环境按固定版本的安装说明准备依赖，再执行；不能把纯阅读仓当成已经安装：

```bash
# 在固定提交的 mjlab 源码仓中，检查零动作下的环境响应。
uv run play Mjlab-Velocity-Flat-Unitree-G1 --agent zero --num-envs 1

# 小规模训练连通性检查，使用本地 TensorBoard 日志。
# 两次迭代只检查训练链路，不用于评判策略质量。
uv run train Mjlab-Velocity-Flat-Unitree-G1   --env.scene.num-envs 64 --agent.max-iterations 2   --agent.logger tensorboard --agent.upload-model False

# 把参数替换成上一条运行实际产生的 checkpoint 路径。
uv run play Mjlab-Velocity-Flat-Unitree-G1   --checkpoint-file PATH_TO_CHECKPOINT --num-envs 1
```

CLI 字段来源：[日志与上传配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/rl/config.py#L105-L126)、[play 参数](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/scripts/play.py#L34-L54)。该版本启用 `tyro.conf.FlagConversionOff`，布尔覆盖写作 `--agent.upload-model False`；来源：[CLI flags](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/__init__.py#L22-L33)。参数映射经过源码检查，安装与 CLI 实际解析仍需原生环境验收。

`play` 使用 `load_env_cfg(..., play=True)`，加载 actor，再获取 inference policy。G1 play 会延长 episode、关闭 actor 噪声、去掉 push、清空课程；flat 的 play 路径还修改命令范围。来源：[play 覆盖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L163-L220)、[加载策略](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/scripts/play.py#L203-L208)。

因此播放动画不能替代固定训练分布上的评估。正式评估应记录实际 checkpoint、归一化状态、最终 env/agent 配置、种子、命令分布、终止条件和指标。

## 练习与参考答案

1. 4096 个环境、24 步、5 个学习 epoch、4 个 mini-batch，为什么每轮环境采样量不是再乘 20？

   **答案：** epoch/mini-batch 描述已有样本的更新安排；本课配置中的原始采样数仍是 98,304。具体算法怎样分批需读对应依赖版本。
2. flat 配置删除了 terrain scan，是否证明所有地形相关传感器都被移除？

   **答案：** 没有。它按传感器名字过滤 `terrain_scan`；仍需逐项检查其他传感器和消费它们的观测/奖励。
3. actor 观测无 NaN、reward 无 NaN，是否足够证明物理正常？

   **答案：** 不足够，尤其 reward 路径有数值清理；需检查原始状态、派生量和运行诊断。
4. 自动重置行的命令计时为什么使用 `dt=0`？

   **答案：** 避免新回合命令计时器在刚重置时就消耗一个控制周期，保持与显式 reset 的起点一致。
5. 改为 `auto_reset=False` 后能否直接使用原来的 train 命令？

   **答案：** 不能据此保证。自带 runner 不驱动手动 reset，需符合该契约的调用循环。
6. 这节课实际证明了什么？

   **答案：** 固定源码下的配置数值、接口和调用顺序，以及静态脚本可执行；没有证明 G1 已学会行走。

## 本课产物与下一步

产物是这条可追踪调用链、配置核对脚本和记录。继续学习时，先补动作/观测维度与机器人执行器映射，再固定 RSL-RL 依赖追踪 rollout → returns → loss。路线和依赖见 [roadmap](../docs/roadmap.md)。
