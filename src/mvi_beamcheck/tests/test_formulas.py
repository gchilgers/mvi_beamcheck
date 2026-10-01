"""
Tests for mathematical formulas.

These tests verify that the implemented formulas match their mathematical
definitions.
"""

from mvi_beamcheck.formulas import compute_output_deviation, compute_flatness, compute_beam_quality_deviation

def test_output_deviation_formula():
    output_response = 2274400.81656049
    crosscal_response = 2280204.76655822
    crosscal_output = 1.00596546
    target_output = 1.00000000

    computed = compute_output_deviation(output_response, crosscal_response, crosscal_output, target_output)
    expected = ((output_response / crosscal_response * crosscal_output) - 1) / target_output * 100

    assert computed == expected


def test_flatness_formula():
    cax_response = 2279190.438805
    off_axis_responses = [2139018.23578294, 2162542.22689521, 2162542.22689521, 2153745.20425309]

    computed = compute_flatness(cax_response, off_axis_responses)
    expected = sum(off_axis_responses)/(4 * cax_response) 

    assert computed == expected


def test_beam_quality_deviation_formula():
    flatness = 0.942133
    reference_flatness = 0.9456
    beta = -1.23

    computed = compute_beam_quality_deviation(flatness, reference_flatness, beta)
    expected = (flatness/reference_flatness - 1) * 100 * beta

    assert computed == expected
