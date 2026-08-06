def compute_output_deviation(output_response: float, crosscal_response: float, crosscal_output: float, target_output: float) -> float:
    """Compute output deviation in percent.

    Implements Eq. 1 from Hilgers et al., 2023.
    DOI: 10.1016/j.phro.2023.100411
    """
    output = output_response / crosscal_response * crosscal_output

    return ((output / target_output) - 1) * 100


def compute_flatness(flatness_responses: dict) -> float:
    """ Compute diagonal normalized flatness.
    
    Implements Eq. 2 from Hilgers et al., 2026.
    DOI: 10.1016/j.phro.2026.100930
    """
    cax_response = flatness_responses['flat_cax']

    off_axis_responses = [
        flatness_responses[key]
        for key in ('flat_D1', 'flat_D2', 'flat_D3', 'flat_D4')
    ]

    return sum(off_axis_responses) / (len(off_axis_responses) * cax_response)


def compute_beam_quality_deviation(flatness: float, reference_flatness: float, beta: float) -> float:
    """ Compute beam quality deviation in percent.
    
    Implements Eq. 3 from Hilgers et al., 2026.
    DOI: 10.1016/j.phro.2026.100930
    """

    return ((flatness / reference_flatness) - 1) * 100 * beta

