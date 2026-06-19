def compute_output_deviation(output_response: float, crosscal_response: float, crosscal_output: float, target_output: float) -> float:
    """Compute output deviation in percent.

    Implements Eq. 1 from Hilgers et al., 2023.
    DOI: 10.1016/j.phro.2023.100411
    """
    output = output_response / crosscal_response * crosscal_output
    deviation = output - target_output
    deviation_in_pct = deviation / target_output * 100

    return deviation_in_pct