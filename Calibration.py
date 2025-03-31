import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import pandas as pd
from glob import glob
from skimage import color
import tkinter as tk
from tkinter import filedialog

# Let the user select the folder (Optional: Uncomment to enable GUI folder selection)
root = tk.Tk()
root.withdraw()
image_folder = filedialog.askdirectory(title="Select Image Folder")


if not image_folder:
    print("⚠️ No folder selected. Exiting.")
    exit()

save_folder = os.path.join(image_folder, "processed_data")
os.makedirs(save_folder, exist_ok=True)  # Ensure save folder exists

# ROI Definitions (for target and background)
ROI = {
    "target": {"x": 922, "y": 616, "width": 50, "height": 50},
    "background": {"x": 1164, "y": 585, "width": 38, "height": 38},
}

# Function to sort images numerically based on filename
def numerical_sort_key(path):
    filename = os.path.basename(path)
    match = re.search(r"(\d+(\.\d+)?)", filename)
    return float(match.group(1)) if match else 0  # Convert numbers safely

# Get sorted list of image paths
image_paths = sorted(glob(os.path.join(image_folder, '*.jpg')), key=numerical_sort_key)
num_files = len(image_paths)

if num_files == 0:
    print("⚠️ No images found in the selected folder. Exiting.")
    exit()

# Extract concentration values from filenames
concentrations = [os.path.splitext(os.path.basename(f))[0] for f in image_paths]

# Initialize arrays for storing values
rgb_data = np.zeros((num_files, 3))  # (samples, 3 for R,G,B)
rgb_background = np.zeros((num_files, 3))  # Background RGB
lab_data = np.zeros((num_files, 3))  # LAB values

# Process images
for k, file_path in enumerate(image_paths):
    img = cv2.imread(file_path)

    if img is None:
        print(f"⚠️ Warning: Could not load {file_path}, skipping.")
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Extract ROI for target and background
    target = ROI["target"]
    background = ROI["background"]
    target_region = img_rgb[target["y"]:target["y"] + target["height"], target["x"]:target["x"] + target["width"]]
    background_region = img_rgb[background["y"]:background["y"] + background["height"], background["x"]:background["x"] + background["width"]]

    # Compute mean RGB
    rgb_data[k, :] = np.mean(target_region, axis=(0, 1))
    rgb_background[k, :] = np.mean(background_region, axis=(0, 1))

    # Convert to LAB and compute mean
    target_lab = color.rgb2lab(target_region / 255.0)
    lab_data[k, :] = np.mean(target_lab, axis=(0, 1))

    # Save ROI-marked image
    img_with_roi = img.copy()
    cv2.rectangle(img_with_roi, (target["x"], target["y"]),
                  (target["x"] + target["width"], target["y"] + target["height"]), (255, 0, 0), 2)
    cv2.rectangle(img_with_roi, (background["x"], background["y"]),
                  (background["x"] + background["width"], background["y"] + background["height"]), (0, 255, 0), 2)

    output_image_path = os.path.join(save_folder, f"roi_{os.path.basename(file_path)}")
    cv2.imwrite(output_image_path, img_with_roi)

    print(f"📸 Processed image {k + 1}/{num_files}: {os.path.basename(file_path)}")

# Save data as CSV
df = pd.DataFrame(rgb_data, columns=['R', 'G', 'B'])
df.insert(0, 'Filename', concentrations)
df[['Background_R', 'Background_G', 'Background_B']] = rgb_background
df[['L*', 'a*', 'b*']] = lab_data
output_csv = os.path.join(save_folder, "color_analysis.csv")
df.to_csv(output_csv, index=False)

print(f"\n🚀 Processing complete! Data saved to: {output_csv}")

# Compute resolved RGB absorbance
rgb_absorbance = np.log10((rgb_background + 1e-6) / (rgb_data + 1e-6))

# Set font size
plt.rcParams.update({'font.size': 18})

# Create plots
colors = ['Red', 'Green', 'Blue']
lab_labels = ['L*', 'a*', 'b*']
x_labels = concentrations  # Use extracted concentrations as X labels

# Function to create and save plots
def plot_data(y_values, labels, title, ylabel, filename):
    plt.figure(figsize=(12, 6))
    for i, label in enumerate(labels):
        plt.plot(x_labels, y_values[:, i], marker='o', label=label)
    plt.xlabel("Concentration (ppm)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.legend(fontsize=14)
    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(save_folder, filename), bbox_inches='tight')
    plt.show()

# **RGB Intensity Plot**
plot_data(rgb_data, colors, "RGB Intensity vs. Concentration", "Intensity", "rgb_intensity_plot.png")

# **LAB Intensity Plot**
plot_data(lab_data, lab_labels, "LAB Intensity vs. Concentration", "LAB Value", "lab_intensity_plot.png")

# **Resolved RGB Absorbance Plot**
plot_data(rgb_absorbance, colors, "Resolved RGB Absorbance vs. Concentration", "Absorbance", "resolved_rgb_absorbance_plot.png")

print("✅ All plots saved successfully!")
