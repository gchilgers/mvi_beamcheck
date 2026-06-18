from dataclasses import dataclass
from datetime import datetime

@dataclass
class BeamCheckResult:
    timestamp: datetime
    output_response: float
    output_deviation: float

def to_dict(self) -> dict:
    return {
        'timestamp': self.timestamp.isoformat(),
        'output_response': self.output_response,
        'output_deviation_percent': self.output_deviation,
    }