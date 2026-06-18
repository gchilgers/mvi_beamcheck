def compute_output_deviation(output_response: float, crosscal_response: float, crosscal_output: float, target_output: float) -> float:
    output = output_response / crosscal_response * crosscal_output
    return (output - target_output) / target_output * 100