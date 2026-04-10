from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence


class CommandError(RuntimeError):
    pass


def run_command(cmd: Sequence[str], cwd: str | Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(list(cmd), cwd=cwd, text=True, capture_output=True)
    if check and proc.returncode != 0:
        raise CommandError(
            f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc
