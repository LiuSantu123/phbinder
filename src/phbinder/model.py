from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json

@dataclass
class Candidate:
    candidate_id: str
    structure: str
    target_chain: str = "A"
    binder_chain: str = "B"
    input_sha256: str = ""

    def as_dict(self):
        return asdict(self)

@dataclass
class Result:
    candidate_id: str
    structure: str
    status: str = "complete"
    error: str = ""
    values: dict[str, Any] | None = None

    def as_dict(self):
        d = {"candidate_id": self.candidate_id, "structure": self.structure,
             "status": self.status, "error": self.error}
        d.update(self.values or {})
        return d

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str))
