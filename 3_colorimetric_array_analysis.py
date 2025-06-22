#!/usr/bin/env python3
"""
Colorimetric Array Analysis Toolkit

This script provides two main functions:

1. calibrate: Extracts color space information from prepared samples at known concentrations to determine the correlation between concentration and RGB intensities under the customer imaging setup.

2. analyze: Applies user-provided calibration curves to sample images to calculate concentrations and classify adsorption performance.

Usage:
  python colorimetric_array_analysis.py calibrate \
      --image-folder path/to/calibration_images \
      --output-folder path/to/save/results \
      --target-roi x,y,width,height \
      --background-roi x,y,width,height

  python colorimetric_array_analysis.py analyze \
      --data-folder path/to/sample_images \
      --calibration-json path/to/calibration_constants.json \
      --roi x,y,width,height \
      --hit-threshold 1 \
      --output-folder path/to/save/results

Calibration JSON example:
{
  "dye1": {"slope": 2.8, "intercept": 164.4, "channel": "B"},
  "dye2": {"slope": 5.9, "intercept": 165.8, "channel": "B"},
  ...
}
"""
import os
import re
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
from glob import glob
from skimage import color


def parse_roi(arg):
    try:
        parts = [int(x) for x in arg.split(',')]
        if len(parts) != 4:
            raise ValueError
        return tuple(parts)
    except ValueError:
        raise argparse.ArgumentTypeError("ROI must be x,y,width,height with integers")


def numerical_sort_key(path):
    fname = os.path.basename(path)
    match = re.search(r"(\d+(?:\.\d+)?)", fname)
    return float(match.group(1)) if match else 0


def calibrate(args):
    image_paths = sorted(glob(os.path.join(args.image_folder, '*.jpg')), key=numerical_sort_key)
    if not image_paths:
        raise FileNotFoundError("No .jpg images found in calibration folder.")

    concentrations = [os.path.splitext(os.path.basename(p))[0] for p in image_paths]
    n = len(image_paths)
    rgb_data = np.zeros((n,3))
    rgb_bg   = np.zeros((n,3))
    lab_data = np.zeros((n,3))

    # create output folder
    os.makedirs(args.output_folder, exist_ok=True)

    for i, path in enumerate(image_paths):
        img = cv2.imread(path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        tx, ty, tw, th = args.target_roi
        bx, by, bw, bh = args.background_roi
        target = img_rgb[ty:ty+th, tx:tx+tw]
        bg     = img_rgb[by:by+bh, bx:bx+bw]
        rgb_data[i] = target.mean(axis=(0,1))
        rgb_bg[i]   = bg.mean(axis=(0,1))
        lab = color.rgb2lab(target/255.)
        lab_data[i] = lab.mean(axis=(0,1))

    df = pd.DataFrame(rgb_data, columns=['R','G','B'])
    df.insert(0,'Concentration', concentrations)
    df[['Bg_R','Bg_G','Bg_B']] = rgb_bg
    df[['L*','a*','b*']] = lab_data
    df.to_csv(os.path.join(args.output_folder,'calibration_data.csv'), index=False)

    # absorbance
    absorb = np.log10((rgb_bg + 1e-6)/(rgb_data + 1e-6))

    def plot(y, labels, title, fname, ylabel):
        plt.figure(figsize=(8,5))
        for idx, label in enumerate(labels):
            plt.plot(concentrations, y[:,idx], marker='o', label=label)
        plt.xlabel('Concentration')
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout(); plt.savefig(os.path.join(args.output_folder, fname))

    plot(rgb_data, ['R','G','B'], 'RGB Intensity vs Concentration', 'rgb_intensity.png', 'Intensity')
    plot(lab_data, ['L*','a*','b*'], 'LAB Intensity vs Concentration', 'lab_intensity.png', 'LAB')
    plot(absorb,  ['R','G','B'], 'Absorbance vs Concentration', 'absorbance.png', 'Absorbance')
    print(f"Calibration complete. Results in {args.output_folder}")


def analyze(args):
    with open(args.calibration_json) as f:
        cal = json.load(f)

    folders = [d for d in glob(os.path.join(args.data_folder,'*')) if os.path.isdir(d)]
    os.makedirs(args.output_folder, exist_ok=True)

    for sub in folders:
        dye = os.path.basename(sub)
        paths = glob(os.path.join(sub,'*.jpg'))
        results = []
        rgb_vals = []
        for p in paths:
            img = cv2.imread(p)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            x,y,w,h = args.roi
            region = img_rgb[y:y+h, x:x+w]
            means = region.mean(axis=(0,1))
            rgb_vals.append(means)
            chan = cal[dye]['channel'].upper()
            idx = {'R':0,'G':1,'B':2}[chan]
            if dye in cal and idx is not None:
                slope = cal[dye]['slope']
                intercept = cal[dye]['intercept']
                if dye == 'dye4':
                    conc = -np.log(means[idx]/intercept)/slope
                else:
                    conc = (intercept - means[idx]) / slope
            else:
                conc = np.nan
            hit = 'Hit' if conc < args.hit_threshold else ''
            results.append({'Filename': os.path.basename(p), 'R':means[0],'G':means[1],'B':means[2],
                            'Concentration': round(conc,3), 'Hit': hit})

        df = pd.DataFrame(results)
        out_csv = os.path.join(args.output_folder, f"{dye}_results.csv")
        df.to_csv(out_csv, index=False)

        # plot
        vals = np.array([r[['R','G','B']][cal[dye]['channel'].upper()] for r in results])
        concs = df['Concentration'].fillna(0)
        plt.figure(figsize=(6,4))
        plt.scatter(vals, concs)
        plt.xlabel(f"{cal[dye]['channel'].upper()} intensity")
        plt.ylabel("Concentration")
        plt.title(f"{dye} Analysis")
        plt.tight_layout(); plt.savefig(os.path.join(args.output_folder,f"{dye}_plot.png"))
        plt.close()
        print(f"Processed {dye}, results: {out_csv}")


def main():
    parser = argparse.ArgumentParser(description="Colorimetric Array Analysis Toolbox")
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_cal = sub.add_parser('calibrate')
    p_cal.add_argument('--image-folder', required=True)
    p_cal.add_argument('--output-folder', required=True)
    p_cal.add_argument('--target-roi', type=parse_roi, required=True)
    p_cal.add_argument('--background-roi', type=parse_roi, required=True)
    p_cal.set_defaults(func=calibrate)

    p_ana = sub.add_parser('analyze')
    p_ana.add_argument('--data-folder', required=True)
    p_ana.add_argument('--calibration-json', required=True)
    p_ana.add_argument('--roi', type=parse_roi, required=True)
    p_ana.add_argument('--hit-threshold', type=float, default=1.0)
    p_ana.add_argument('--output-folder', required=True)
    p_ana.set_defaults(func=analyze)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
