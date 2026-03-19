"""Dump a concise directory tree for the ecommerce-api project.

This script ignores large generated directories such as `venv`, `.git`, `htmlcov`, `media`, and `staticfiles`.

Run it from the project root:
  python scripts/dump_structure.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {"venv", ".git", "__pycache__", "htmlcov", "media", "staticfiles"}
MAX_DEPTH = 4

lines = []


def add(line: str) -> None:
    lines.append(line)


def walk(path: Path, prefix: str = "", depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        return
    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return
    for i, entry in enumerate(entries):
        if entry.name in EXCLUDE:
            continue
        connector = "└──" if i == len(entries) - 1 else "├──"
        add(f"{prefix}{connector} {entry.name}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            walk(entry, prefix + extension, depth + 1)


if __name__ == "__main__":
    add(str(ROOT))
    walk(ROOT)

    out_path = ROOT / "PROJECT_STRUCTURE.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path} with {len(lines)} lines")
