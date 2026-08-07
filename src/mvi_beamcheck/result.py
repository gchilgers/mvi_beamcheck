from dataclasses import dataclass
from datetime import datetime

@dataclass
class BeamCheckResult:
    timestamp: datetime
    output_response: float
    output_deviation: float
    flatness_responses: dict[str, float]
    flatness: float
    beam_quality_deviation: float

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'output_response': self.output_response,
            'flatness_responses': self.flatness_responses,
            'output_deviation': self.output_deviation,
            'flatness': self.flatness,
            'beam_quality_deviation': self.beam_quality_deviation
        }