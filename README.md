## Overview
A Python package for verifying beam output and X-ray beam quality on a 1.5 T MRI‑linac using the on-board megavoltage imager (MVI).

This repository implements methods for the analysis of MVI-based beam output and X-ray beam quality previously described in peer-reviewed work [1, 2] and reflects ongoing development toward a structured, reusable software package. It provides a transparent and configurable approach for consistent and reproducible analysis across systems, without requiring user-specific reimplementation.

## Quick start

## Configuration
MVIBeamCheck requires a machine-specific configuration file containing the parameters for output and X-ray beam quality calculations. Users should create their own based on `example.toml`. 

**Note:**  
*The file `example.toml` should not be modified as it is used by the test suite.*


## Test suite

The test suite combines unit and integration tests to verify configuration parsing, formula implementations, end-to-end processing, and ROI geometry.

### Configuration parsing

The example configuration (`config/example.toml`) is validated by verifying that it can be parsed into a `BeamCheckConfig` dataclass.

### Formula implementations

The formula implementations for calculating the output deviation, flatness, and beam quality deviation are verified against their mathematical definitions.

### Flatness ROI geometry

Flatness ROI geometry tests use a synthetic RTIMAGE test pattern (`rtimg_test_pattern.dcm`) to verify the placement and dimensions of the central and off-axis flatness ROIs.

### End-to-end pipeline

Pipeline tests process a representative RTIMAGE (`rtimg_example_anon.dcm`)
using the example configuration and compare the computed results against known
reference values.


## References:<br>
1.  Hilgers et al. (2023) - https://doi.org/10.1016/j.phro.2023.100411
2.  Hilgers et al. (2026) - https://doi.org/10.1016/j.phro.2026.100930

## Disclaimer

This software is intended for research and quality assurance purposes. It has not been validated as a medical device and is not intended to be used as the sole basis for decisions affecting clinical use of the system.
