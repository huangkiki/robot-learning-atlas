# PPO 专题：一条转移如何进入 GAE 与 loss

[首页](../README.md) · [G1 观测与动作](../mjlab/02-observations-actions.md) · [随机化与课程](../mjlab/03-randomization-curriculum.md)

**先修：** actor/critic、batch 与 time 维度、log probability、终止与截断。

**目标：** 沿真实 runner、storage 和 PPO 函数解释 `obs_t, action_t, reward_t, done_t` 的时刻、超时处理、GAE 与更新过程。

**版本：** mjlab 精确依赖 `rsl-rl-lib==5.5.1`；本课固定官方 `v5.5.1` 对应提交 `857de6165c5fd479726ec8ac5c9303a497766f30`，并核对该提交包版本。此选择只覆盖本课 mjlab 路径，不宣称 Isaac Lab、UniLab 的任意安装都解析到同一版本。[mjlab 依赖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/pyproject.toml#L35-L50)、[RSL-RL 版本](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/pyproject.toml#L5-L22)

## 1. 采样与更新的两个阶段

```text
get_observations
  → PPO.act：保存 obs_t、action_t、V_t、旧 log_prob、分布参数
  → env.step：返回下一观测、reward_t、done_t、extras
  → process_env_step：处理 timeout，copy 到 RolloutStorage
  → 重复 T 步
  → compute_returns：反向 GAE + return
  → update：minibatches × epochs
  → 更新 normalization → clear storage 游标 → 下一轮
```

runner 采样段放在 `torch.inference_mode()`；PPO 更新段重新构建可求导的前向计算。`act` 保存的是物理执行前的观测，虽然 `process_env_step` 又收到新观测，存进 transition 的起点观测仍是旧的。[runner.learn](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/runners/on_policy_runner.py#L56-L108)、[act 与 process_env_step](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/algorithms/ppo.py#L124-L164)

## 2. Storage 的形状与所有权

以 G1、N=4096、T=24、A=29 为源码推导例：

| Buffer | 形状 | 保存的时间意义 |
|---|---|---|
| actor observation | `[24,4096,99]`（预期） | action 之前的输入 |
| critic observation | `[24,4096,111]`（预期） | 同时刻、不同信息集 |
| actions | `[24,4096,29]` | 当时采样的原始动作 |
| rewards / dones | `[24,4096,1]` | 这次执行的结果；reward 可能已做 timeout 修正 |
| values / old log probabilities | `[24,4096,1]` | 采样时模型给出的旧值 |
| returns / advantages | `[24,4096,1]` | rollout 完成后计算的训练目标 |

`add_transition` 使用 `copy_` 写入预分配 buffer；这也是它能清空临时 Transition 而不丢样本的原因。自己写 collector 时不能照搬“保存一个 env.state 引用”的做法。[storage 分配与写入](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/storage/rollout_storage.py#L125-L205)

总 batch 为 98,304。G1 配置 4 个 minibatch、5 个 epoch，所以每个 minibatch 24,576 条，名义执行 20 次更新。该 feedforward generator 用整数除法，未整除时只抽取 `num_mini_batches * mini_batch_size` 个索引；应检查可整除性。这里不覆盖 recurrent、分布式或 symmetry 增广后的样本量。[minibatch generator](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/storage/rollout_storage.py#L225-L243)、[G1 PPO 参数](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/rl_cfg.py#L28-L45)

## 3. Timeout：必须读实际消费者

mjlab wrapper 将 done 合并，并在无限时域配置下把 `truncated` 作为 `extras["time_outs"]`。RSL-RL v5.5.1 的这条代码在保存样本前执行：

```text
stored_reward = env_reward + gamma * transition.values * time_outs
```

这里 `transition.values` 来自当前 step 之前 `act(obs_t)` 计算的 critic。它不是在此处重新对 final observation 估值，也不是把自动 reset 后新回合的观测当作真实终止观测。解释这个版本时应忠实记录实现；是否采用其他 time-limit bootstrap 设计需要独立实验，不能悄悄把源码描述改成另一种算法。[mjlab wrapper](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/rl/vecenv_wrapper.py#L72-L89)、[timeout 消费](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/algorithms/ppo.py#L137-L164)

数值例：env reward=1，V_t=2，γ=0.99，timeout=1，则存入的 reward=2.98。done=1 仍然截断后续 GAE 递推，避免跨 reset 把下一回合接上。

## 4. GAE 反向递推

对保存后的 reward（记作 r̃），代码计算：

```text
mask_t  = 1 - done_t
δ_t     = r̃_t + γ * mask_t * V_(t+1) - V_t
A_t     = δ_t + γ * λ * mask_t * A_(t+1)
return_t = A_t + V_t
```

rollout 最后一步的 next value 来自最后返回的 observation；其他位置取 storage 的下一个 value。done mask 决定它是否参与。计算 return 后，若未启用 per-minibatch normalization，整个 rollout 的 advantage 再做标准化；因此公式中的原始 advantage 与优化时输入并非总是同一数值。[compute_returns](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/algorithms/ppo.py#L166-L191)

手算：两步 reward 都为 1，values=[2,3]，last value=4，两个 done 都为 0，γ=0.99，λ=0.95：A₁=1.96，A₀=3.81338，returns=[5.81338,4.96]。若第二步是真实 terminal，则 A₁=-2、A₀=0.089，returns=[2.089,1]。下面的纯 Python 示例核对这些边界与上面的 timeout 例子：

```bash
python3 learning/examples/rollout_math.py
```

它只做标量算术，不导入 Torch/RSL-RL，也不是运行过原生 PPO 的证明。

## 5. PPO 更新重新评价旧 action

每个 minibatch 使用新参数计算旧 action 的 log probability，再与采样时保存的旧 log probability 比较：

```text
ratio = exp(new_log_prob(old_action) - old_log_prob)
policy_loss = mean(max(-A * ratio, -A * clip(ratio, 1-ε, 1+ε)))
loss = policy_loss + value_loss_coef * value_loss - entropy_coef * entropy
```

G1 的 ε=0.2、value coefficient=1、entropy coefficient=0.01，并启用 clipped value loss：新 value 的变化按旧 value 限幅，两个平方误差取较大者。剪切对象是概率比或 value 的变化，不是直接把 action 截成 ±0.2。[PPO losses](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/algorithms/ppo.py#L268-L285)

adaptive schedule 用 KL 调学习率；随后 backward、梯度 norm 限制、optimizer.step。该版本在所有 minibatch 更新后，用当前 rollout 更新 actor/critic normalization，再清空 storage 游标。归一化统计的时序和 checkpoint 必须一起复现。[KL schedule](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/algorithms/ppo.py#L240-L266)、[梯度与 normalization](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/algorithms/ppo.py#L296-L330)、[清空 storage](https://github.com/leggedrobotics/rsl_rl/blob/857de6165c5fd479726ec8ac5c9303a497766f30/rsl_rl/algorithms/ppo.py#L344-L358)

## 6. 练习与答案

1. `compute_returns` 为何不对下一回合的 reset observation 无条件 bootstrap？

   **答案：** done mask 把跨边界 next value 与 GAE continuation 清零；timeout 的修正在保存 reward 时单独处理。
2. 4 个 minibatch、5 个 epoch 是否意味着新采集 20 倍数据？

   **答案：** 否，同一 rollout 重用 5 次，每次分 4 批；新环境转移仍是 N×T。
3. 把物理 dt 翻倍，保持 gamma=0.99，是否保持相同真实时间折扣？

   **答案：** 不保持。gamma 按策略步作用；物理时间变化同时改变控制、奖励积累与有效折扣时域。
4. 不带 normalization 统计只导出 actor 权重，是否足以复现训练时行为？

   **答案：** 对启用 normalization 的 G1 配置不够，还需输入映射、统计、动作尺度、偏置与控制时钟等契约。

**验证边界：** 源码与标量计算已核对；未执行 Torch PPO 更新、原生仿真、学习曲线复现或策略评估。
