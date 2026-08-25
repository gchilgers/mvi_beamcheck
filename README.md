## Overview
A Python package for verifying beam output and X-ray beam quality on a 1.5 T MRI‑linac using the on-board megavoltage imager (MVI).

This repository implements methods for the analysis of MVI-based beam output and X-ray beam quality previously described in peer-reviewed work [1, 2] and reflects ongoing development toward a structured, reusable software package. It provides a transparent and configurable approach for consistent and reproducible analysis across systems, without requiring user-specific reimplementation.

## Quick start

## Configuration
MVIBeamCheck requires a machine-specific configuration file containing the parameters for output and X-ray beam quality calculations. Users should create their own based on `example.toml`. The example file should not be modified, as it is used by the test suite.

## Methodology

### Pixel discretization
**Note:**  
*For clarity, pixel coordinates in this section are presented as `(col, row)`.*

The machine geometry file stores the vendor-reported beam center using subpixel image coordinates and a 1-based indexing system. These coordinates should be copied unchanged to the configuration file. For example:

```text
mean_isocenter_pixel = [512.837, 650.785]
```

The vendor defines the first pixel as (1, 1), whereas the exported RTIMAGE uses (0, 0) as the first pixel. During processing, the coordinates are therefore converted from 1-based to 0-based indexing:
```text
(512.837, 650.785) → (511.837, 649.785)
```

MVIBeamCheck does not retain the vendor-reported subpixel beam center coordinates. Instead, it determines the pixel containing the converted beam center coordinates:
```text
(511.837, 649.785) → (511, 649)
```

For calculations, pixel centers are assumed to lie at half-integer coordinates (e.g., pixel 0 is centered at 0.5). The beam center used by the software is therefore defined as the center of the containing pixel:
```text
(511.5, 649.5)
```

Off-axis ROI centers are defined at fixed physical distances from the beam center. These distances are converted to pixel offsets. Fractional pixel offsets are discarded, yielding integer pixel displacements relative to the beam center pixel. Consequently, all ROI centers coincide with pixel center locations.

For example, if the beam center is located at (511.5, 649.5) and an off-axis ROI is located 249.996 pixels to the right and 111.109 pixels upward, the off-axis ROI center is placed at:

```text
(511.5 + 249, 649.5 - 111) = (760.5, 538.5)
```

Even though the continuous ROI center would be located slightly further from the beam center, the software uses the integer pixel displacement only. The resulting ROI center position differs from the corresponding continuous position by less than one pixel along each image axis (~0.2 mm at isocenter level).

### ROI dimensions
ROI dimensions are specified directly in pixels and are therefore unaffected by discretization of the ROI center.

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
