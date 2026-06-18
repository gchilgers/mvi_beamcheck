from dataclasses import dataclass


@dataclass
class OutputConfig:
    crosscal_response: float
    crosscal_output: float
    target_output: float


@dataclass
class ImagerConfig:
    mean_isocenter_pixel: tuple[float, float]


@dataclass
class BeamCheckConfig:
    output: OutputConfig
    imager: ImagerConfig

    @classmethod
    def from_dict(cls, config: dict) -> 'BeamCheckConfig':
        return cls(
            output = OutputConfig(
                crosscal_response = config['output']['crosscal_response'],
                crosscal_output = config['output']['crosscal_output'],
                target_output = config['output']['target_output']
            ),
            imager = ImagerConfig(
                mean_isocenter_pixel = config['imager']['mean_isocenter_pixel']
            ),
        )
    
        
    
                   
                                                                          
                                                                          