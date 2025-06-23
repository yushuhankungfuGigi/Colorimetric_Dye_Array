# This script calculates the concentration of each sample image based on pre-measured calibration curves.
# Six subfolders are created, each corresponding to a different dye (dye6 to dye1).
# Each subfolder contains images of individual samples.
# Using the predefined calibration equations and the relevant color channel (Green for dye6-dye3, Blue for dye2-dye1),
# the concentration associated with each image is determined.


import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import color
import os
import re
import pandas as pd
from glob import glob

# Define root folder
root_folder = r"C:\d+(?:\.\d+)?"

# Define correlation functions for each dye type
def calculate_concentration(rgb_value, dye_type):
    correlation_map = {
        'dye6': lambda v: (160.16 - v) / 2.1853,
        'dye5': lambda v: (156.91 - v) / 9.5192,
        'dye4': lambda v: np.exp((151.4 - v) / 50.58),
        'dye3': lambda v: (162.51 - v) / 3.3036,
        'dye2': lambda v: (165.77 - v) / 5.8655,
        'dye1': lambda v: (164.37 - v) / 2.8291,
    }
    return correlation_map.get(dye_type, lambda v: None)(rgb_value)

# Function to extract numerical values from filenames
def numerical_sort_key(path):
    filename = os.path.basename(path)
    match = re.search(r"(\d+(\.\d+)?)", filename)
    return float(match.group(1)) if match else float('inf')

# Function to process images in a given folder
def process_images_in_folder(subfolder_path, save_folder):
    image_paths = sorted(glob(os.path.join(subfolder_path, '*.jpg')), key=numerical_sort_key)
    num_files = len(image_paths)
    folder_name = os.path.basename(subfolder_path)
    
    if num_files == 0:
        print(f"⚠️ No images found in {subfolder_path}, skipping.")
        return
    
    # Extract concentration values from filenames
    concentrations = [os.path.splitext(os.path.basename(f))[0] for f in image_paths]

    # Define fixed ROI (x, y, width, height)
    # Due to slight variations in sample positioning across different images, the ROI is dynamically adjusted to ensure accurate analysis.
    # target_roi = (982, 656, 50, 50)
    target_roi = (872, 656, 50, 50)
    background_roi = (1164, 585, 38, 38)

    # Initialize arrays for storing values
    rgb_data = np.zeros((num_files, 3))
    calculated_concentrations = []
    hit_column = []

    # Process images
    for k, file_path in enumerate(image_paths):
        img = cv2.imread(file_path)
        if img is None:
            print(f"⚠️ Warning: Could not load {file_path}, skipping.")
            continue

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        target_region = img_rgb[target_roi[1]:target_roi[1]+target_roi[3], target_roi[0]:target_roi[0]+target_roi[2]]
        
        # Make a copy of the original image (BGR format) for visualization
        img_display = img.copy()
        cv2.rectangle(img_display, (target_roi[0], target_roi[1]), (target_roi[0] + target_roi[2], target_roi[1] + target_roi[3]), (255, 0, 0), 2)
        cv2.rectangle(img_display, (background_roi[0], background_roi[1]), (background_roi[0] + background_roi[2], background_roi[1] + background_roi[3]), (0, 255, 0), 2)
        cv2.imshow(f"ROI - {os.path.basename(file_path)}", img_display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Compute mean RGB
        rgb_means = np.mean(target_region, axis=(0, 1))
        rgb_data[k, :] = rgb_means

        # Calculate concentration based on focused channel (Green for dye6-dye3, Blue for dye2-dye1)
        focus_channel = 1 if folder_name in ['dye6', 'dye5', 'dye4', 'dye3'] else 2
        concentration = calculate_concentration(rgb_means[focus_channel], folder_name)
        
        if concentration < 1:
            calculated_concentrations.append('< 1 ppm')
            hit_column.append('Hit')
        else:
            calculated_concentrations.append(concentration)
            hit_column.append('')
        
        print(f"📸 Processed image {k + 1}/{num_files}: {os.path.basename(file_path)}")

    print("\n🚀 Processing complete, saving data...")
    
    # Create DataFrame and save CSV
    df = pd.DataFrame(rgb_data, columns=['R', 'G', 'B'])
    df.insert(0, 'Filename', concentrations)
    df['Calculated_Concentration'] = calculated_concentrations
    df['HIT'] = hit_column
    output_file = os.path.join(save_folder, f"{folder_name}_data.csv")
    df.to_csv(output_file, index=False)
    print(f"🎉 Data saved to: {output_file}")

    # Convert calculated_concentrations to numerical values for plotting
    numeric_concentrations = [float(c) if c != '< 1 ppm' else 0 for c in calculated_concentrations]

    # Plot and save Concentration vs. Focused Channel Plot with Image Names (adjusted manually to avoid overlap)
    plt.figure(figsize=(12, 6))
    plt.scatter(rgb_data[:, focus_channel], numeric_concentrations, color='b', marker='o')
    for i, txt in enumerate(concentrations):
        plt.annotate(txt, (rgb_data[i, focus_channel], numeric_concentrations[i]), fontsize=9, ha='right', va='bottom', rotation=15)
    plt.xlabel(f"{'Green' if focus_channel == 1 else 'Blue'} Channel Intensity", fontsize=16)
    plt.ylabel("Calculated Concentration (ppm)", fontsize=16)
    plt.title(f"Concentration vs. Focused Channel - {folder_name}", fontsize=18)
    plt.grid()
    plt.savefig(os.path.join(save_folder, "concentration_vs_channel_plot.png"))
    plt.show()

# Main processing
subfolders = [f.path for f in os.scandir(root_folder) if f.is_dir()]

for subfolder in subfolders:
    print(f"🔍 Processing subfolder: {subfolder}")
    process_images_in_folder(subfolder, subfolder)

print("✅ All processing completed!")