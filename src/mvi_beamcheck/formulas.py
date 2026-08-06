def compute_output_deviation(output_response: float, crosscal_response: float, crosscal_output: float, target_output: float) -> float:
    """Compute output deviation in percent.

    Implements Eq. 1 from Hilgers et al., 2023.
    DOI: 10.1016/j.phro.2023.100411
    """
    output = output_response / crosscal_response * crosscal_output
    deviation = output - target_output
    deviation_in_pct = deviation / target_output * 100

    return deviation_in_pct

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

    flatness = sum(off_axis_responses) / (len(off_axis_responses) * cax_response)
    return flatness



