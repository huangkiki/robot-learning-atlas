"""Check course links and pinned source references, without network access."""

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "docs/sources.json").read_text())
    repositories = {p["repository"]: p for p in manifest["projects"].values()}
    errors = []
    links = 0
    source_links = 0

    for page in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in page.relative_to(ROOT).parts):
            continue
        fence = chr(96) * 3
        prose = re.sub(rf"(?ms)^{fence}.*?^{fence}[ \t]*$", "", page.read_text())
        for target in re.findall(r"!?\[[^\]]*\]\(([^)\s]+)\)", prose):
            links += 1
            url = urlsplit(target)
            if url.scheme:
                if "/blob/" not in target:
                    continue
                repository, reference = target.split("/blob/", 1)
                if repository not in repositories:
                    continue
                spec = repositories[repository]
                revision, path = reference.split("/", 1)
                path = unquote(path.split("#", 1)[0])
                info = spec["files"].get(path)
                if revision != spec["commit"] or info is None:
                    errors.append(f"{page.relative_to(ROOT)}: unpinned source {target}")
                    continue
                if url.fragment:
                    lines = re.fullmatch(r"L(\d+)(?:-L(\d+))?", url.fragment)
                    if not lines or not (
                        1 <= int(lines[1]) <= int(lines[2] or lines[1]) <= info["lines"]
                    ):
                        errors.append(f"{page.relative_to(ROOT)}: invalid source lines {target}")
                source_links += 1
            elif url.path:
                path = (page.parent / unquote(url.path)).resolve()
                if not path.is_relative_to(ROOT) or not path.exists():
                    errors.append(f"{page.relative_to(ROOT)}: missing/outside local link {target}")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Passed: {links} links, including {source_links} pinned source references.")
    print("Local existence and source line bounds only; no runtime or web rendering check.")


if __name__ == "__main__":
    main()
