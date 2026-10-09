"""Verify the reviewed upstream Git objects against the course manifest."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    specs = json.loads((ROOT / "docs/sources.json").read_text())["projects"]
    parser = argparse.ArgumentParser(description=__doc__)
    for name in specs:
        parser.add_argument(f"--{name}", required=True, type=Path)
    args = parser.parse_args()
    count = 0

    for name, spec in specs.items():
        checkout = getattr(args, name)
        command = ["git", "-C", str(checkout)]
        head = subprocess.check_output(command + ["rev-parse", "HEAD"], text=True).strip()
        if head != spec["commit"]:
            raise SystemExit(f"{name}: HEAD differs from the reviewed commit")
        for path, expected in spec["files"].items():
            data = subprocess.check_output(command + ["show", f"{head}:{path}"])
            actual = {
                "sha256": hashlib.sha256(data).hexdigest(),
                "lines": len(data.decode("utf-8").splitlines()),
            }
            if actual != expected:
                raise SystemExit(f"{name}: source digest or line count differs: {path}")
            count += 1
        print(f"{name}: {len(spec['files'])} Git blobs verified at {head}")
    print(f"Passed: {count} source files. Working-tree edits and runtime were not evaluated.")


if __name__ == "__main__":
    main()
