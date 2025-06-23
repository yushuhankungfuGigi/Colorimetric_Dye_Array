import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import color
import os
import re
from glob import glob

# Define file paths
image_folder = r"(\d+(\.\d+)?)"
save_folder = r"(\d+(\.\d+)?)"
os.makedirs(save_folder, exist_ok=True)  # Ensure save folder exists

# Get sorted list of images
def numerical_sort_key(path):
    filename = os.path.basename(path)
    match = re.search(r"(\d+(\.\d+)?)", filename)  # Extracts only valid numbers (integers or decimals)
    return float(match.group(1)) if match else 0  # Convert to float safely

image_paths = sorted(glob(os.path.join(image_folder, '*.jpg')), key=numerical_sort_key)
num_files = len(image_paths)

# Extract concentration values from filenames
concentrations = [os.path.splitext(os.path.basename(f))[0] for f in image_paths]  # Remove extension

# Define fixed ROI (x, y, width, height)
target_roi = (922, 616, 50, 50)
background_roi = (1164, 585, 38, 38)  # Background region for absorbance calculation

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

    # Extract ROI
    x, y, w, h = target_roi
    bx, by, bw, bh = background_roi
    target_region = img_rgb[y:y+h, x:x+w]
    background_region = img_rgb[by:by+bh, bx:bx+bw]

    # Compute mean RGB
    rgb_data[k, :] = np.mean(target_region, axis=(0, 1))  # Store R, G, B means
    rgb_background[k, :] = np.mean(background_region, axis=(0, 1))

    # Convert to LAB and compute mean
    target_lab = color.rgb2lab(target_region / 255.0)
    lab_data[k, :] = np.mean(target_lab, axis=(0, 1))  # Store L*, a*, b* means

    print(f"📸 Processed image {k + 1}/{num_files}: {os.path.basename(file_path)}")

print("\n🚀 Processing complete, saving data...")

# Save RGB mean values (only target region)
output_file = os.path.join(save_folder, "target_RGB_mean.txt")
np.savetxt(output_file, rgb_data, fmt="%.4f", delimiter="\t", header="R\tG\tB", comments='')

print(f"🎉 Processing complete! Data saved to: {output_file}")

# Compute resolved RGB absorbance
rgb_absorbance = np.log10((rgb_background + 1e-6) / (rgb_data + 1e-6))

# Set font size
plt.rcParams.update({'font.size': 24})

# Create plots
colors = ['Red', 'Green', 'Blue']
lab_labels = ['L*', 'a*', 'b*']

# Set X-axis labels
x_labels = concentrations  # Use extracted concentrations as X labels

### **RGB Intensity Plot**
plt.figure(figsize=(12, 6))
for i in range(3):  # Iterate over R, G, B
    plt.plot(x_labels, rgb_data[:, i], marker='o', label=f'{colors[i]} Intensity')
plt.xlabel("Concentration (ppm)", fontsize=24)
plt.ylabel("Intensity", fontsize=24)
plt.title("RGB Intensity vs. Concentration", fontsize=24)
plt.xticks(rotation=45, ha="right")  # Rotate labels for better visibility
plt.subplots_adjust(bottom=0.2)  # Add extra space at bottom
plt.legend(fontsize=20)
plt.grid()
plt.tight_layout()  # Ensure everything fits
plt.savefig(os.path.join(save_folder, "rgb_intensity_plot.png"), bbox_inches='tight')  # Ensure labels are saved
plt.show()

### **LAB Intensity Plot**
plt.figure(figsize=(12, 6))
for i in range(3):  # Iterate over L*, a*, b*
    plt.plot(x_labels, lab_data[:, i], marker='o', label=f'{lab_labels[i]} Intensity')
plt.xlabel("Concentration (ppm)", fontsize=24)
plt.ylabel("LAB Value", fontsize=24)
plt.title("LAB Intensity vs. Concentration", fontsize=24)
plt.xticks(rotation=45, ha="right")
plt.subplots_adjust(bottom=0.2)
plt.legend(fontsize=20)
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(save_folder, "lab_intensity_plot.png"), bbox_inches='tight')
plt.show()

### **Resolved RGB Absorbance Plot**
plt.figure(figsize=(12, 6))
for i in range(3):  # Iterate over R, G, B absorbance
    plt.plot(x_labels, rgb_absorbance[:, i], marker='o', label=f'{colors[i]} Absorbance')
plt.xlabel("Concentration (ppm)", fontsize=24)
plt.ylabel("Absorbance", fontsize=24)
plt.title("Resolved RGB Absorbance vs. Concentration", fontsize=24)
plt.xticks(rotation=45, ha="right")
plt.subplots_adjust(bottom=0.2)
plt.legend(fontsize=20)
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(save_folder, "resolved_rgb_absorbance_plot.png"), bbox_inches='tight')
plt.show()

print("✅ All plots saved successfully!")
