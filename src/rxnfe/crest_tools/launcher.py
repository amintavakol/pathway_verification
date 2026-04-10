from __future__ import annotations

from pathlib import Path

from rxnfe.crest_tools.command_builder import build_crest_command
from rxnfe.utils.shell import run_command


def run_crest(xyz_path: str | Path, output_dir: str | Path, executable: str = "crest", charge: int = 0, uhf: int = 0, extra_args: list[str] | None = None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = build_crest_command(xyz_path, charge=charge, uhf=uhf, extra_args=extra_args, executable=executable)
    return run_command(cmd, cwd=output_dir, check=False)
