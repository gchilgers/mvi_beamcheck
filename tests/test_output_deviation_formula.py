import numpy as np
from mvi_beamcheck import MVIBeamCheck

def test_output_deviation_formula():
    computed = MVIBeamCheck._output_deviation_formula(
        2274423.1626736,    # output_response
        2280231,            # crosscal_response
        1.005965,           # crosscal_output
        1.000000            # target_output
    )

    expected = ((2274423.1626736 / 2280231 * 1.005965) - 1.000000) / 1.000000 * 100

    print(computed, expected)

    assert np.isclose(computed, expected, rtol=1e-6)