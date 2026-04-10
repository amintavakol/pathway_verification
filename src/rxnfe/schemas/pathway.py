from __future__ import annotations

from pydantic import BaseModel


class PathwayRecord(BaseModel):
    reaction_id: str
