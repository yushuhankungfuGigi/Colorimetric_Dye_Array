# Accelerated Porosity Screening with Multichannel Colorimetric Arrays

A computer vision–based colorimetry workflow for high-throughput porosity screening. This repository provides Python scripts to:

- Extract calibration data (RGB/LAB intensities and absorbance) from known-concentration dye images.
- Apply calibration constants to test images to compute dye concentrations.
- Classify adsorption performance and generate visual summaries.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
   - [Calibration Data Extraction](#calibration-data-extraction)
   - [Concentration Calculation](#concentration-calculation)
6. [Configuration](#configuration)
7. [Data Structure](#data-structure)
8. [Test Data](#test-data)
9. [Contributing](#contributing)
10. [License](#license)

---

## Overview

This project streamlines porosity screening by imaging dye adsorption tests before and after exposure to porous materials. Two scripts are provided:

1. **Calibration.py**: Processes calibration images at known concentrations to extract raw RGB/LAB intensities and compute absorbance.
2. **Main_calculation.py**: Uses pre-determined calibration constants to calculate concentrations in test images and classify adsorption performance.

## Features

- Calibration data extraction (RGB means, LAB values, background absorbance).
- Batch processing of test images across six dye types.
- Predefined ROI and background ROI for consistent analysis.
- Concentration calculation using custom calibration functions (linear or logarithmic).
- Automatic classification into **Hit**, **Moderate fade**, or **None**.
- Output of CSV summaries and publication-quality plots.

## Prerequisites

- Python 3.7+
- Install required packages:
  ```bash
  pip install numpy opencv-python matplotlib scikit-image pandas
  ```
- Standard libraries: `os`, `re`, `glob`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/porosity-screening.git
   cd porosity-screening
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # macOS/Linux
   source venv/bin/activate
   # Windows
   venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Calibration Data Extraction

1. Open `Calibration.py` and set:
   - `image_folder`: Path to your calibration images (e.g., `'data/dye1_calib/'`).
   - `save_folder`: Path to save outputs (can be the same as `image_folder`).
   - `target_roi`: `(x, y, width, height)` for sample region.
   - `background_roi`: `(x, y, width, height)` for background.
2. Ensure images are named to include concentration (e.g., `1.jpg`, `2.5.jpg`, `10.jpg`).
3. Run:
   ```bash
   python Calibration.py
   ```
4. Outputs in `save_folder`:
   - `target_RGB_mean.txt`: Tab-delimited R, G, B means per concentration.
   - `rgb_intensity_plot.png`: RGB intensities vs. concentration.
   - `lab_intensity_plot.png`: LAB channel values vs. concentration.
   - `resolved_rgb_absorbance_plot.png`: Absorbance vs. concentration.

5. Use these plots or exported data to fit calibration curves (e.g., in Excel) and update `CALIBRATION_CONSTANTS` in `Main_calculation.py`.

### Concentration Calculation

1. Organize test images under `data/` with six subfolders: `dye1` … `dye6`.
2. In `Main_calculation.py`, adjust if needed:
   ```python
   CALIBRATION_CONSTANTS = {
       'dye1': {'slope': ..., 'intercept': ..., 'channel': 'B'},
       # ... dye2–dye6
   }
   ROI = dict(x_top_left=892, y_top_left=616, width=50, height=50)
   HIT_THRESHOLD = 1  # ppm cutoff for 'Hit'
   ```
3. Run:
   ```bash
   python Main_calculation.py
   ```
4. For each dye folder, the script:
   - Reads all `*.jpg` files.
   - Extracts predefined ROI and computes mean RGB.
   - Calculates concentration via the specified channel and calibration formula.
   - Classifies samples below `HIT_THRESHOLD` as **Hit**.
   - Saves `<dye>_data.csv` with columns: `Filename`, `R`, `G`, `B`, `Calculated_Concentration`, `HIT`.
   - Generates `concentration_vs_channel_plot.png` for each dye.

## Configuration

- **Calibration.py**:
  - `image_folder` and `save_folder` (raw paths or relative to script).
  - `target_roi`, `background_roi` for sampling areas.

- **Main_calculation.py**:
  - `CALIBRATION_CONSTANTS`: slope, intercept, and channel per dye.
  - `ROI`: analysis window.
  - `HIT_THRESHOLD`: adsorption cutoff.
  - `root_folder`: defaults to `'data'` directory beside the script.

## Data Structure

```text
porosity-screening/
├── data/
│   ├── dye1/           # test images
│   ├── dye1_calib/     # calibration images
│   ├── …
│   └── dye6_calib/
├── Calibration.py
├── Main_calculation.py
├── requirements.txt
└── README.md
```

## Test Data

Provided in `Test.zip`:

1. **Data_calibration.zip** – Calibration images (1–10 ppm) for six dyes (60 images total)
2. **Data_Main_calculation.zip** – 50 sample images per dye (300 images total).

## Contributing

Contributions welcome! Open an issue or pull request for fixes, enhancements, or documentation updates.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

