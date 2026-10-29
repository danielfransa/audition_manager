from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImpulseResponse:
    path: Path
    name: str
    sample_rate: int
    channels: int
    favorite: bool = False
    rating: int = 0
    notes: str = ""


@dataclass(frozen=True)
class Capture:
    path: Path
    name: str
    version: str
    architecture: str
    sample_rate: int
    submodel_count: int
    favorite: bool = False
    rating: int = 0
    notes: str = ""

