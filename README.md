## Overview
A Python package for verifying beam output and X-ray beam quality on a 1.5 T MRI‑linac using the on-board megavoltage imager (MVI).

This repository implements methods for the analysis of MVI-based beam output and X-ray beam quality previously described in peer-reviewed work [1, 2] and reflects ongoing development toward a structured, reusable software package. It provides a transparent and configurable approach for consistent and reproducible analysis across systems, without requiring user-specific reimplementation.

## Quick start

## Test Suite

The test suite combines unit and integration tests to verify configuration
parsing, formula implementations, end-to-end processing, and ROI geometry.

### Configuration parsing

The example configuration (`config/example.toml`) is validated by verifying
that it can be parsed into a `BeamCheckConfig` dataclass.

### Formula implementations

Unit tests verify that the implementations of the output deviation, flatness,
and beam quality deviation formulas match their mathematical definitions.

### End-to-end pipeline

Pipeline tests process a representative RTIMAGE (`rtimg_example_anon.dcm`)
using the example configuration and compare the computed results against known
reference values.

### ROI geometry

ROI geometry is validated using the synthetic RTIMAGE test pattern
`rtimg_test_pattern.dcm`. These tests verify the flatness ROI geometry, whereas
the output ROI geometry is verified indirectly through the end-to-end pipeline
tests.

## References:<br>
1.  Hilgers et al. (2023) - https://doi.org/10.1016/j.phro.2023.100411
2.  Hilgers et al. (2026) - https://doi.org/10.1016/j.phro.2026.100930

## Disclaimer

This software is intended for research and quality assurance purposes. It has not been validated as a medical device and is not intended to be used as the sole basis for decisions affecting clinical use of the system.
