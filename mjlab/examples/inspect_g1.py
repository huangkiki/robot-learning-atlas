"""Read the pinned G1 task's timing literals; never import or execute mjlab."""

import argparse
import ast
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "Mjlab-Velocity-Flat-Unitree-G1"


def keyword(call: ast.Call, name: str) -> ast.expr:
    return next(kw.value for kw in call.keywords if kw.arg == name)


def named_call(tree: ast.AST, name: str) -> ast.Call:
    matches = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {name} call, found {len(matches)}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--num-envs", default=4096, type=int)
    args = parser.parse_args()
    if args.num_envs < 1:
        parser.error("--num-envs must be positive")

    spec = json.loads((ROOT / "docs/sources.json").read_text())["projects"]["mjlab"]
    command = ["git", "-C", str(args.source)]
    head = subprocess.check_output(command + ["rev-parse", "HEAD"], text=True).strip()
    if head != spec["commit"]:
        raise SystemExit("HEAD differs from the course pin; use the reviewed source commit.")

    def read(path: str) -> ast.Module:
        data = subprocess.check_output(command + ["show", f"{head}:{path}"])
        if hashlib.sha256(data).hexdigest() != spec["files"][path]["sha256"]:
            raise SystemExit(f"Source digest differs: {path}")
        return ast.parse(data, filename=path)

    prefix = "src/mjlab/tasks/velocity/"
    base = read(prefix + "velocity_env_cfg.py")
    runner = read(prefix + "config/g1/rl_cfg.py")
    registered = read(prefix + "config/g1/__init__.py")
    # Pin the robot-specific overrides too: this script does not evaluate arbitrary factories.
    read(prefix + "config/g1/env_cfgs.py")
    if not any(
        isinstance(node, ast.Constant) and node.value == TASK_ID
        for node in ast.walk(registered)
    ):
        raise SystemExit("The reviewed task ID was not found.")

    env_cfg = named_call(base, "ManagerBasedRlEnvCfg")
    physics_cfg = named_call(base, "MujocoCfg")
    rl_cfg = named_call(runner, "RslRlOnPolicyRunnerCfg")
    physics_dt = ast.literal_eval(keyword(physics_cfg, "timestep"))
    decimation = ast.literal_eval(keyword(env_cfg, "decimation"))
    duration = ast.literal_eval(keyword(env_cfg, "episode_length_s"))
    horizon = ast.literal_eval(keyword(rl_cfg, "num_steps_per_env"))
    step_dt = physics_dt * decimation

    result = {
        "evidence": "static-source-analysis",
        "source_commit": head,
        "task_id": TASK_ID,
        "physics_dt_s": physics_dt,
        "decimation": decimation,
        "policy_dt_s": step_dt,
        "policy_hz": 1 / step_dt,
        "episode_steps": math.ceil(duration / step_dt),
        "rollout_steps_per_env": horizon,
        "num_envs_assumed": args.num_envs,
        "transitions_per_rollout": args.num_envs * horizon,
        "simulated_seconds_per_env_per_rollout": horizon * step_dt,
        "runtime_executed": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
