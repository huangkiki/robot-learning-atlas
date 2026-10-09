# Isaac Lab 首课：用 Cartpole 对照 Manager 与 Direct

[导读](README.md) · [源码地图](source-map.md) · [mjlab 首课](../mjlab/01-g1-task.md)

**先修：** Python 配置类、批量张量、物理步与策略步、终止与截断。

**目标：** 从一个注册任务追到配置、后端、动作、step/reset 和 RSL-RL；能说明两个工作流在哪些位置相同、哪些位置需要分别核对。

**版本与证据：** Isaac Lab `07daf4426dfa8dcb6d0753768890b4f60dc54f9e` 开发快照。本课是固定源码阅读与静态推导，没有启动 Isaac Lab，也没有训练 Cartpole。不要将当前任务路径套用到旧版发布。

## 1. 先找注册项，再找配置

[注册表](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/__init__.py#L21-L70) 提供两个无 `-v0` 后缀的任务：

| 任务 ID | 环境类 | 环境配置 | RSL-RL 配置 |
|---|---|---|---|
| `Isaac-Cartpole` | `isaaclab.envs:ManagerBasedRLEnv` | `cartpole_manager_env_cfg:CartpoleEnvCfg` | `CartpolePPORunnerCfg` |
| `Isaac-Cartpole-Direct` | `cartpole_direct_env:CartpoleEnv` | `cartpole_direct_env_cfg:CartpoleEnvCfg` | `CartpoleDirectPPORunnerCfg` |

环境与算法配置是两条独立入口。`default_agent="rsl_rl"` 指定默认学习库，不指定物理引擎。

两者使用 `CartpolePhysicsCfg`。在本快照，其 `default` 是 `newton_mjwarp`；另有 PhysX、OvPhysX 与 Kamino 等配置预设。这些是声明的选项，本课没有运行这些组合。不要看到 Isaac Lab 名称就认定本任务默认使用 PhysX。[物理配置预设](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_common.py#L29-L53)

## 2. 把配置换算成可检查的契约

[Manager 配置](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_manager_env_cfg.py#L160-L184) 与 [Direct 配置](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_direct_env_cfg.py#L39-L72) 给出：

| 量 | 默认值 | 含义与推导 |
|---|---|---|
| 物理步 `dt` | 1/120 s | 名义物理频率 120 Hz |
| `decimation` | 2 | 策略步 `step_dt = 1/60 s`，60 Hz |
| 回合上限 | 5 s | `ceil(5 / (1/60)) = 300` 个策略步 |
| 场景 | 4096 个环境，间距 4 m | 环境数可由训练请求覆盖 |
| 动作 | 每环境 1 个数 | 沿 `slider_to_cart` 施加关节力，比例 100 N |
| Direct policy 观测 | 每环境 4 个数 | 相对小车位置、相对杆角、相对小车速度、相对杆角速度 |
| rollout 长度 | 每环境 16 步 | 默认 4096 × 16 = 65,536 条转移/迭代 |

回合长度公式来自 [环境配置基类](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py#L63-L73)，rollout 长度来自 [PPO 配置](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/agents/rsl_rl_ppo_cfg.py#L21-L56)。这里的 300 是时间截断上限；提前失败、随机初始回合长度会改变实际收集到的单个 episode 长度。

### 动作和观测的单位

Manager 的 `JointEffortActionCfg` 选择 `slider_to_cart` 并设置 `scale=100.0`。Direct 在 `_pre_physics_step` 中乘以 `action_scale`，在 `_apply_action` 中写 effort target。因此 `a=0.2` 对应 20 N 的目标输入；实际执行还受执行器和后端约束。是否裁剪动作要继续查 wrapper 和算法配置，不能从 action space 的维数推断。[Manager 动作](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_manager_env_cfg.py#L59-L83)、[Direct 动作与观测](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_direct_env.py#L27-L59)

Direct 明确拼接 `[x-x₀, θ-θ₀, ẋ-ẋ₀, θ̇-θ̇₀]`，单位依次为 m、rad、m/s、rad/s。Manager 拼接 `joint_pos_rel` 后再拼接 `joint_vel_rel`，每组内部遵循所解析的关节顺序。跨工作流交换策略前，要打印真实关节名和索引核对，不能只比较维度 4。Manager 本任务关闭观测 corruption；这不代表所有 Isaac Lab 任务都无噪声。

## 3. 一次 step 的调用链

```text
policy action
  → Manager: process_action / Direct: _pre_physics_step
  → apply_action → scene.write_data_to_sim → sim.step
  → 按需 render → scene.update
  → 回合计数 +1 → termination/done → reward
  → 重置结束行，必要时重新渲染传感器
  → interval event 等后处理 → 生成返回观测
  → RSL-RL wrapper → runner
```

两个基类都计算 `steps_per_call = decimation if _physics_handles_decimation else 1`，循环执行 `decimation // steps_per_call` 次，scene 更新传入 `physics_dt * steps_per_call`。因此 60 Hz 策略步不能靠数 Python `sim.step()` 调用次数判断。[Manager step](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L208-L284)、[Direct step](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/direct_rl_env.py#L396-L469)

本课选择本体状态任务，没有相机观测。`render_interval=2` 是渲染调度参数，不是保证每个观测都来自新的相机帧：渲染开关、后端以及传感器自己的更新条件还会参与。结束行重置后，基类仅在 `render_enabled`、`is_rendering`、RTX sensor 和 rerender 数量等条件满足时执行额外渲染。换成 Camera 任务时，必须单独核对这些条件，不能直接沿用本课的四维状态时序。

## 4. 奖励、失败和 reset

Manager 使用 reward terms；Direct 在 `compute_rewards` 中显式计算。Direct 的总式为：

```text
r = step_dt × [1 × (1-terminated) - 2 × terminated
               - wrap_to_pi(θ)² - 0.01 × |ẋ| - 0.005 × |θ̇|]
```

这份 Direct 实现已经乘 `step_dt`。不能再在外层乘一次，也不能笼统写成“Direct 奖励从不按时间缩放”。Manager 的 reward manager 在调用时接收 `dt=self.step_dt`，权重和具体 term 要沿原始函数核对。[Manager 奖励配置](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_manager_env_cfg.py#L112-L139)、[Direct 奖励公式](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_direct_env.py#L140-L160)

失败与时间结束是两类信号：

- 小车超出 ±3 m：`terminated`。
- 回合计数达到上限：`truncated/time_out`。
- 当前这两条配置都没有“杆角度超限即结束”的条件；杆角偏离通过奖励惩罚，不能照搬其他 Cartpole 教程的结束规则。

来源：[Manager termination](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_manager_env_cfg.py#L142-L152)、[Direct done](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_direct_env.py#L75-L81)。

reset 随机化小车位置 ±1 m、速度 ±0.5 m/s；杆角和角速度各为 ±0.25π，单位分别 rad 与 rad/s。Manager 用 reset event，Direct 在 `_reset_idx` 中采样、裁剪到关节限制并写回物理状态。Direct 的 world root pose 还加上对应场景原点，不能把所有副本重置到世界同一点。[Manager reset](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_manager_env_cfg.py#L86-L109)、[Direct reset](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_tasks/isaaclab_tasks/core/cartpole/cartpole_direct_env.py#L83-L137)

### 返回观测属于哪个回合

Manager 在同一次 step 内重置结束行，最终返回的新观测属于新回合；本课配置继承 `compute_final_obs=False`。启用时，基类会在正常自动重置前保存 `extras["final_obs"]`。这是一条额外数据通路，不等于返回 tuple 中的观测自动变成终止观测。[final_obs 默认值与约定](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py#L47-L60)、[自动重置顺序](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L244-L284)

RSL-RL wrapper 合并 `terminated | truncated`，并在无限时域配置下把 `truncated` 放入 `extras["time_outs"]`。这段 wrapper 不在这里用 `final_obs` 替换观测；消费者如何 bootstrap 要继续读所用算法版本。[RSL-RL wrapper](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py#L155-L168)

## 5. 从训练请求追到 runner

此开发快照已有统一入口。用其显式 Python API 可以避免猜测旧教程的脚本位置：

```python
from isaaclab_rl.entrypoints.api import TrainingRequest, train

request = TrainingRequest(
    backend="rsl_rl",
    task="Isaac-Cartpole",
    num_envs=64,
    seed=42,
    max_iterations=2,
)
# 在准备好对应版本、物理后端和资产的原生环境中才执行：
# exit_code = train(request)
```

此处 `backend` 指学习库。`TrainingRequest` 经 dispatcher 选择 `train_rsl_rl`，后者依次解析任务配置、启动 simulation、覆盖环境/算法配置、创建环境、包 `RslRlVecEnvWrapper`、构造 `OnPolicyRunner`、保存配置并调用 `runner.learn`。两次迭代、64 环境在 16 步 rollout 下名义收集 2048 条转移，足以作为后续连通性检查规模，不能据此评价策略质量。[请求 API](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_rl/isaaclab_rl/entrypoints/api.py#L22-L52)、[训练分发](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_rl/isaaclab_rl/entrypoints/dispatch.py#L79-L105)、[训练主体](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_rl/isaaclab_rl/entrypoints/backends/train_rsl_rl.py#L115-L197)

切换 Direct 时改为注册 ID `Isaac-Cartpole-Direct`；其 runner 配置继承上述 PPO 参数并使用 `cartpole_direct` 实验名。检查产物时应保存解析后的配置、版本、日志与真实 checkpoint 路径，不能假定两次迭代一定触发默认每 50 次的周期保存；最终保存行为还取决于 runner。

## 6. 练习与答案

1. 将 `decimation` 改为 4，保持 dt、5 s 上限和 16 步 rollout 不变，哪些量改变？

   **答案：** 策略频率降为 30 Hz，上限变为 150 步；每环境 rollout 覆盖的仿真时间从约 0.267 s 变成约 0.533 s。环境数不变时转移条数不变。奖励按 dt 缩放，但折扣、控制响应及采样分布并不因此等价。
2. 为什么同样都是四维观测，还不能直接复用策略？

   **答案：** 需要确认关节索引、拼接顺序、相对参考值、单位、动作尺度/裁剪和归一化状态；维数仅是其中一项。
3. `time_out=True` 是否意味着本任务没有自动 reset？

   **答案：** 否。两类结束行都会重置；`time_outs` 保留结束原因供学习器解释。
4. 在训练日志中看到 policy 输入正常，能否证明相机 reset 时序正确？

   **答案：** 不能。本课使用关节状态观测，没有验证相机、渲染或传感器同步。

**交付边界：** 已完成配置与调用链阅读、时间/批量推导和练习。原生导入、请求执行、后端兼容性、训练与回放仍需独立运行证据。
