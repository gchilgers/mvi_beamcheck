from dataclasses import dataclass
from datetime import datetime

@dataclass
class BeamCheckResult:
    timestamp: datetime
    output_response: float
    output_deviation: float
