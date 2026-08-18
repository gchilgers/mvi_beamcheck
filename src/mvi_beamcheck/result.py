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

        d = {
            'timestamp': self.timestamp.isoformat(),
            'output_response': self.output_response,
            'output_deviation': self.output_deviation,
            'flatness': self.flatness,
            'beam_quality_deviation': self.beam_quality_deviation,
        }

        d.update(
            {f'flatness_{k}': float(v)
            for k, v in self.flatness_responses.items()}
        )

        return d


    def __repr__(self):
        flatness_responses_str = (
            '{'
            + ', '.join(
                f'{name}: {value:.6f}'
                for name, value in self.flatness_responses.items()
            )
            + '}'
        )

        return (
            f'BeamCheckResult('
            f'timestamp={self.timestamp.isoformat()}, '
            f'output_response={self.output_response:.6f}, '
            f'output_deviation={self.output_deviation:.2f}%, '
            f'flatness_responses={flatness_responses_str}, '
            f'flatness={self.flatness:.6f}, '
            f'beam_quality_deviation={self.beam_quality_deviation:.2f}%)'
        )