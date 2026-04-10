from __future__ import annotations

from pathlib import Path
from typing import Sequence


def write_xyz(symbols: Sequence[str], coords: Sequence[Sequence[float]], path: str | Path, comment: str = "") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{len(symbols)}\n")
        f.write(comment + "\n")
        for s, (x, y, z) in zip(symbols, coords):
            f.write(f"{s} {x:.8f} {y:.8f} {z:.8f}\n")


def read_xyz(path: str | Path) -> tuple[list[str], list[list[float]], str]:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f]
    if len(lines) < 2:
        raise ValueError(f"Invalid XYZ file: {path}")
    natoms = int(lines[0].strip())
    comment = lines[1] if len(lines) > 1 else ""
    body = lines[2:2+natoms]
    symbols: list[str] = []
    coords: list[list[float]] = []
    for line in body:
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(f"Invalid XYZ row in {path}: {line}")
        symbols.append(parts[0])
        coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return symbols, coords, comment
