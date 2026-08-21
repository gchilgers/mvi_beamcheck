"""
Tests for mathematical formulas.

These tests verify that the implemented formulas match their mathematical
definitions.
"""

from mvi_beamcheck.formulas import compute_output_deviation, compute_flatness, compute_beam_quality_deviation

def test_output_deviation_formula():
    output_response = 2274423.1626736
    crosscal_response = 2280230.690419
    crosscal_output = 1.005965
    target_output = 1.000000

    computed = compute_output_deviation(output_response, crosscal_response, crosscal_output, target_output)
    expected = ((output_response / crosscal_response * crosscal_output) - 1) / target_output * 100

    assert computed == expected


def test_flatness_formula():
    cax_response = 2279190.438805
    off_axis_responses = [2139674.321530, 2161641.444203, 2154864.816918, 2135946.821430]

    computed = compute_flatness(cax_response, off_axis_responses)
    expected = sum(off_axis_responses)/(4 * cax_response) 

    assert computed == expected


def test_beam_quality_deviation_formula():
    flatness = 0.942454
    reference_flatness = 0.945883
    beta = -1.23

    computed = compute_beam_quality_deviation(flatness, reference_flatness, beta)
    expected = (flatness/reference_flatness - 1) * 100 * beta

    assert computed == expected
