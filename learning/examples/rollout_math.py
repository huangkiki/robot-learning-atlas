"""Scalar GAE exercises; no simulator, Torch, or PPO runtime is executed."""

import json
import math


def returns_for_rollout(
    rewards: list[float],
    values: list[float],
    dones: list[bool],
    last_value: float,
    gamma: float = 0.99,
    lam: float = 0.95,
) -> list[float]:
    """Compute unnormalized GAE returns for one scalar trajectory.

    Rewards must already include any chosen timeout adjustment. The done
    flags still cut the recursion at episode boundaries.
    """
    transitions = list(zip(rewards, values, dones, strict=True))
    returns = [0.0] * len(transitions)
    advantage = 0.0
    next_value = last_value
    for index in reversed(range(len(transitions))):
        reward, value, done = transitions[index]
        mask = float(not done)
        delta = reward + gamma * mask * next_value - value
        advantage = delta + gamma * lam * mask * advantage
        returns[index] = advantage + value
        next_value = value
    return returns


def main() -> None:
    cases = {
        "continuing": returns_for_rollout([1.0, 1.0], [2.0, 3.0], [False, False], 4.0),
        "terminal": returns_for_rollout([1.0, 1.0], [2.0, 3.0], [False, True], 4.0),
        # v5.5.1 process_env_step uses the value saved before env.step.
        # A deliberately large next value demonstrates that done masks it.
        "timeout_v5_5_1": returns_for_rollout([1.0 + 0.99 * 2.0], [2.0], [True], 100.0),
    }
    expected = {
        "continuing": [5.81338, 4.96],
        "terminal": [2.089, 1.0],
        "timeout_v5_5_1": [2.98],
    }
    for name, actual in cases.items():
        for result, target in zip(actual, expected[name], strict=True):
            if not math.isclose(result, target, rel_tol=0.0, abs_tol=1e-10):
                raise AssertionError(f"{name}: {actual} != {expected[name]}")
    print(json.dumps({"evidence": "scalar arithmetic only", "returns": cases}, indent=2))


if __name__ == "__main__":
    main()
