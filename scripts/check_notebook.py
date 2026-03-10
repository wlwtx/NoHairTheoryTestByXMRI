#!/usr/bin/env python3
"""Basic sanity checks for notebook code cells.

Checks:
1) Each code cell compiles.
2) Flag suspicious debug leftovers such as one-word identifier expressions.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


def load_notebook(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_suspicious_identifier_expr(source: str) -> bool:
    stripped = source.strip()
    if not stripped:
        return False
    try:
        tree = ast.parse(stripped)
    except SyntaxError:
        return False
    if len(tree.body) != 1:
        return False
    node = tree.body[0]
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Name)


def check_notebook(path: Path) -> int:
    nb = load_notebook(path)
    failures: list[str] = []
    warnings: list[str] = []

    for idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue

        try:
            compile(source, f"{path.name}:cell_{idx}", "exec")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"Cell {idx}: compile error: {exc}")

        if is_suspicious_identifier_expr(source):
            warnings.append(
                f"Cell {idx}: suspicious single identifier expression: {source.strip()!r}"
            )

    for item in failures:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN: {item}")

    if failures or warnings:
        return 1
    print(f"Notebook checks passed: {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    args = parser.parse_args()
    return check_notebook(args.notebook)


if __name__ == "__main__":
    raise SystemExit(main())
