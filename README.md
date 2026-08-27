## Overview
A Python package for verifying beam output and X-ray beam quality on a 1.5 T MRI‑linac using the on-board megavoltage imager (MVI).

This repository implements methods for the analysis of MVI-based beam output and X-ray beam quality previously described in peer-reviewed work [1, 2] and reflects ongoing development toward a structured, reusable software package. It provides a transparent and configurable approach for consistent and reproducible analysis across systems, without requiring user-specific reimplementation.

## Quick start

## Configuration
MVIBeamCheck requires a machine-specific configuration file containing the parameters for output and X-ray beam quality calculations. Users should create their own based on `example.toml`. 

**Note:**  
*The file `example.toml` should not be modified as it is used by the test suite.*

## Methodology

### Pixel discretization
`MVIBeamCheck` does not perform subpixel ROI placement. Fractional pixel information in both the vendor-reported beam center and the calculated ROI offsets is rounded to the nearest pixel, resulting in ROI centers defined on the image pixel grid. Consequently, the discretized beam center may differ from the vendor-reported beam center by up to 0.5 pixel (~0.1 mm at isocenter) along each axis in the worst case. For off-axis ROIs, the independent rounding of both the beam center and the ROI offset may result in a displacement of up to 1 pixel (~0.2 mm at isocenter) along each axis relative to the corresponding continuous position. ROI sizes are defined directly in integer pixels and therefore do not introduce additional discretization uncertainty. In practice, the impact on the measured signal is negligible because the analysis ROIs are substantially larger than a single pixel.

**Note:**   
*For clarity, pixel coordinates in this section are presented as `(column, row)`.* 

The machine geometry file stores the vendor-reported beam center using subpixel image coordinates and a 1-based indexing system. These coordinates should be copied unchanged to the configuration file. For example:
```text
mean_isocenter_pixel = [512.837, 650.785]
```
The vendor defines the first pixel as (1, 1), whereas the exported 'RTImage' uses (0, 0) as the first pixel. During processing, the coordinates are therefore converted from 1-based to 0-based indexing:
```text
(512.837, 650.785) → (511.837, 649.785)
```
`MVIBeamCheck` then rounds the converted beam center coordinates to the nearest image pixel:
```text
(511.837, 649.785) → (512, 650)
```
Off-axis ROI centers are defined as fixed physical distances from the beam center. These distances are converted to pixel offsets and discretized independently. For example, if the calculated ROI center offset is 249.996 pixels to the right and 111.109 pixels upward from the beam center, the corresponding integer pixel offset becomes
```text
(249.996, -111.109) → (250, -111)
```
Combining this offset with the discretized beam center yields:
```text
(512 + 250, 650 - 111) = (762, 539)
```
### Response calculation
For each ROI, the response is calculated as the arithmetic mean of the individual pixel responses. No subpixel weighting or interpolation is performed, and each pixel contributes equally to the average. The resulting ROI responses are used to calculate beam output and X-ray beam-quality deviations according to the published methodology. 

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
