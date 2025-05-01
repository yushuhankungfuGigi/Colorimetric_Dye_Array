# Accelerated porosity screening using a multichannel colorimetric array

A computer vision–based colorimetry method was developed as an in situ analytical tool for imaging dye arrays before and after adsorption, with outcomes recorded as red, green, and blue (RGB) channels. Due to the considerable number of samples, we created this Python script to automate image processing. 

The script (Main_concentration.py) defines the region of interest (ROI), extracts RGB values, calculates the corresponding concentration after adsorption, and classifies the output into three levels: ‘hit’, ‘moderate fade’, or ‘none’. 

This script calculates the concentration of each sample image based on pre-measured calibration curves (in the script Calibration.py). These calibration curves are generated using images of known concentration samples.

# Requirements

Users should prepare calibration stock dye solutions with concentrations ranging from 1 to 10 ppm to construct calibration curves. The fitting coefficients were generated using Excel and stored in the `CALIBRATION_CONSTANTS` dictionary
The users must create six subfolders within the 'data' folder, each named after the dye type (dye1, dye2, ..., dye6), and store the images of the relevant samples in the respective subfolders.

# Data
Two data folders performed by this workstation were shown in the Test.zip folder, including:
(1) Six calibration stock dye solutions with concentrations ranging from 1 to 10 ppm
(2) Images of 50 tested materitals in each dyes (50*6)
