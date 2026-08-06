from dataclasses import dataclass

@dataclass
class ImagerConfig:
    mean_isocenter_pixel: tuple[float, float]

@dataclass
class OutputConfig:
    crosscal_response: float
    crosscal_output: float
    target_output: float

@dataclass
class BeamQualityConfig:
    reference_flatness: float
    beta: float

@dataclass
class BeamCheckConfig:
    imager: ImagerConfig
    output: OutputConfig
    beam_quality: BeamQualityConfig

    @classmethod
    def from_dict(cls, config: dict) -> 'BeamCheckConfig':
        return cls(
            imager = ImagerConfig(
                mean_isocenter_pixel = config['imager']['mean_isocenter_pixel']
            ),            
            output = OutputConfig(
                crosscal_response = config['output']['crosscal_response'],
                crosscal_output = config['output']['crosscal_output'],
                target_output = config['output']['target_output']
            ),
            beam_quality = BeamQualityConfig(
                reference_flatness = config['beam_quality']['reference_flatness'],
                beta = config['beam_quality']['beta']
            ),
        )
                   
                                                                          
                                                                          