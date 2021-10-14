from astropy.coordinates import SkyCoord  # High-level coordinates
from astropy.coordinates import ICRS, Galactic, FK4, FK5  # Low-level frames
from astropy.coordinates import Angle, Latitude, Longitude  # Angles
import astropy.units as u
import os
import sys
import pandas as pd
import numpy as np
import shutil
from multiprocessing import Pool
import argparse
import json

FRAMES = {"galactic":Galactic, "icrs":ICRS}
COORDS_COLS_NAMES = {"galactic":["l", "b"], "icrs":["ra, dec"]}

cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input_sample_catalog", required=True,
               help="""Sample of the full catalog file ['ID', 'long [deg]', 'b [deg]']
                            / accepts ra/dec degs too (change on config)""")
ap.add_argument("-fc", "--full_catalog", required=True,
                               help="Full catalog file ['ID', 'long', 'b']")
ap.add_argument("-o", "--output_duplicates", required=True,
                               help="Output .csv features file")
ap.add_argument("-c", "--duplicates_config", default=f"{cwd}{os.sep}default_duplicates_config.json",
                               help="Extractor config file (JSON)")
args = vars(ap.parse_args())

def duplicates(i, a1_df, a2_df, config_params):
    max_sep = config_params["MAX_SEP [m_arcsec]"]
    frame = FRAMES[config_params["FRAME"]]
    c1, c2 = COORDS_COLS_NAMES[config_params["FRAME"]]
    a1_df = a1_df.copy().reset_index(drop=True).loc[i:i]
    a1_input = {c1:a1_df[c1], c2:a1_df[c2], "frame":frame, "unit":(u.deg, u.deg)}
    a2_input = {c1:a2_df[c1], c2:a2_df[c2], "frame":frame, "unit":(u.deg, u.deg)}

    a1_coords = SkyCoord(**a1_input) #sample
    a2_coords = SkyCoord(**a2_input) #full

    idx_a1_a2, d2d_a1_a2, d3d_a1_a2 = a2_coords.match_to_catalog_sky(a1_coords)
    a1_a2_best_matches = a1_df.iloc[idx_a1_a2].reset_index(drop=True)
    a1_a2_best_matches["m_sep"] = d2d_a1_a2.arcsec
    a2_a1_crossmatch = a2_df.join(a1_a2_best_matches, rsuffix="_2")
    a2_a1_crossmatch = a2_a1_crossmatch.query(f"m_sep>0.000001 and m_sep<{max_sep}")
    return a2_a1_crossmatch

if __name__=="__main__":
    # user input
    sample_cat = args["input_sample_catalog"]
    full_cat = args["full_catalog"]
    output_file = args["output_duplicates"]
    # CONFIG
    config_file = args["duplicates_config"]
    with open(config_file, 'r', encoding="utf-8") as infile:
        config_params = json.load(infile)
    c1, c2 = COORDS_COLS_NAMES[config_params["FRAME"]]
    # load var file and then prepare input file
    s_data = pd.read_csv(sample_cat, sep=" ").iloc[:,:3]
    output_names = s_data.columns
    s_data.columns = ["ID", c1, c2]
    fc_data = pd.read_csv(full_cat, sep=" ").iloc[:,:3]
    fc_data.columns = ["ID", c1, c2]
    output_data = pd.concat(list(
                    duplicates(i, s_data, fc_data, config_params) for i in range(s_data.shape[0])
                                                                ), ignore_index=True)
    output_data.columns = [*output_names, *list(f"{x}_2" for x in output_names), "m_sep"]
    output_data.to_csv(output_file, sep=" ", index=False)
