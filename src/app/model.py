import uuid
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class TodoItem:
    title: str
    description: Optional[str] = ""
    done: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))