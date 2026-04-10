from __future__ import annotations

from pathlib import Path
from typing import Sequence


def build_crest_command(xyz_path: str | Path, charge: int = 0, uhf: int = 0, extra_args: Sequence[str] | None = None, executable: str = "crest") -> list[str]:
    cmd = [executable, str(xyz_path), "--chrg", str(charge), "--uhf", str(uhf)]
    if extra_args:
        cmd.extend(list(extra_args))
    return cmd
