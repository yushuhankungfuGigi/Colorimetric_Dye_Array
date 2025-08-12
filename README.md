# Colorimetric Dye Array Analysis Toolkit

A modular Python toolkit for colorimetric analysis of dye arrays. Provides two main functions:

* **calibrate**: Extracts color space information from prepared samples at known concentrations to determine the correlation between concentration and RGB intensities under the customer’s imaging setup.
* **analyze**: Applies user-provided calibration curves to sample images to calculate concentrations and classify adsorption performance.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yushuhankungfuGigi/Colorimetric_Dye_Array.git
   cd Colorimetric_Dye_Array
   ```
2. Create a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Calibration step

Use the `calibrate` subcommand to extract RGB and LAB data from calibration images and generate calibration curves.

```bash
python src/colorimetric_array_analysis.py calibrate \
  --image-folder path/to/calibration_images \
  --output-folder path/to/results/calibrate \
  --target-roi x,y,width,height \
  --background-roi x,y,width,height
```

* **--image-folder**: Directory of images named by concentration (e.g. `0.1.jpg`, `0.2.jpg`).
* **--output-folder**: Where CSVs and plots will be saved.
* **--target-roi**: ROI for the dye spots (format `x,y,width,height`).
* **--background-roi**: ROI for background intensity.

Outputs:

* `calibration_data.csv` containing raw RGB, background, and LAB means.
* Plots: `rgb_intensity.png`, `lab_intensity.png`, `absorbance.png`.
* A calibration JSON (you can rename or merge into your own config).

### 2. Analysis step

Apply your calibration constants to new sample images:

```bash
python src/colorimetric_array_analysis.py analyze \
  --data-folder path/to/sample_images \
  --calibration-json path/to/results/calibrate/calibration_constants.json \
  --roi x,y,width,height \
  --hit-threshold 1.0 \
  --output-folder path/to/results/analyze
```

* **--data-folder**: Directory containing subfolders per dye (each with sample `.jpg` images).
* **--calibration-json**: JSON of slopes, intercepts, and channels.
* **--roi**: ROI for sample spots (format `x,y,width,height`).
* **--hit-threshold**: Concentration cutoff to flag “hits.”
* **--output-folder**: Where results and plots will be saved.

Outputs per dye:

* `<dye>_results.csv` with mean RGB, calculated concentration, and hit flag.
* `<dye>_plot.png` of intensity vs. concentration.

---

## Reference Implementations

For reproducibility, the original lab-specific scripts are provided under `reference/`:

* `reference/calibration_lab_specific.py`
* `reference/analysis_lab_specific.py`

These demonstrate the exact workflow used for the published experiments.

---

## Examples

The `example/` folder contains example datasets for demonstrating the analysis workflow:

* `Data_calibration.zip` — Calibration dataset used to generate example calibration curves.
* `Data_Main_calculation.zip` — Main dataset for concentration analysis using the calibration results.



---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
