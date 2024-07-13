from dataclasses import dataclass
from enum import Enum

class VscoMediaType(Enum):
    IMAGE = 0
    VIDEO = 1

@dataclass
class VscoMedia:
    type: VscoMediaType
    download_url: str
    timestamp: int
    
