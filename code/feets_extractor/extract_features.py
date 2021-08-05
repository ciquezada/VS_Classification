import os
import sys
import pandas as pd
import numpy as np
import shutil
from multiprocessing import Pool
from astropy.io import ascii
import argparse
import json

cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input_var", required=True,
                               help="Input .var file")
ap.add_argument("-o", "--output_features", required=True,
                               help="Output .csv features file")
ap.add_argument("-lc", "--lc_directory", required=True,
                               help="Light curves .dat files directory")
ap.add_argument("-p", "--processes", default=1, type=int,
                               help="Parallel processes")
ap.add_argument("-fs", "--features_set", required=True,
                               help="Features set file to extract (JSON)")
ap.add_argument("-c", "--extractor_config", default=f"{cwd}{os.sep}default_extractor_config.json",
                               help="Extractor config file (JSON)")
args = vars(ap.parse_args())

def run_feets_extractor(i_args):
    i, args = i_args
    features_preset, temp_folder = args
    RUN_CODE_STRING = "python adapter_feets_extractor.py " # command line
    RUN_CODE_STRING += f"-i \"{temp_folder}{os.sep}input_{i}.csv\" " # temp input file
    RUN_CODE_STRING += f"-o \"{temp_folder}{os.sep}output_{i}.csv\" " # temp output file
    RUN_CODE_STRING += f"-fs \"{features_preset}\" " # features selection
    os.system(RUN_CODE_STRING)

# In line 52 is the period selection
def period_selection(selection, df):
    if selection=="min_aov":
        return df.min(axis=1)
    else:
        return df[selection]

def os_mkdir(folder_name):
    # making needed directories
    gen = (x for x in range(1,99999))
    aux_folder_name = folder_name[:-1]
    while True:
        try:
            os.mkdir(folder_name)
            break
        except OSError as error:
            folder_name = f"{aux_folder_name}{next(gen)}"
    return folder_name

if __name__=="__main__":
    # user input
    num_proc = args["processes"]
    ks_curves_dir = args["lc_directory"]
    var_file = args["input_var"]
    output_file = args["output_features"]
    features_preset = args["features_set"]
    # CONFIG
    config_file = args["extractor_config"]
    with open(config_file, 'r', encoding="utf-8") as infile:
        config_params = json.load(infile)
    temp_dir = os.path.abspath(config_params["TEMP_DIR"])
    col_id = config_params["VAR_COLS"]["ID"]
    col_p1 = config_params["VAR_COLS"]["P1"]
    col_p2 = config_params["VAR_COLS"]["P2"]
    col_label = config_params["VAR_COLS"]["label"]
    # load var file and then prepare input file
    var_df = ascii.read(var_file).to_pandas()
    input_df = var_df[[col_id]].copy()
    input_df.columns = ["ID"]
    # Period selection by the case
    input_df["period"] = period_selection(col_p1, var_df[[col_p1, col_p2]])

    input_df["ks_path"] = var_df[col_id].apply(lambda x:
                                            f"{ks_curves_dir}{os.sep}{x}.dat")
    if col_label in var_df:
        input_df["label"] = var_df[col_label]
    del(var_df)
    # making needed directories
    temp_folder = f"{temp_dir}{os.sep}temp_0"
    temp_folder = os_mkdir(temp_folder)
    # splitting input file
    chunksize = int(np.ceil(input_df.shape[0]/num_proc))
    for i in range(num_proc):
        input_df.iloc[chunksize*i:chunksize*(i+1),:].to_csv(
                                        f"{temp_folder}{os.sep}input_{i}.csv",
                                                        index=False, sep=" ")
    # calling pyfiner pipeline
    pool = Pool(num_proc)
    pool.map(run_feets_extractor, enumerate(
                                    [(features_preset, temp_folder)]*num_proc
                                                ))
    pool.close()
    pool.join()
    # joining output parts and saving
    output_df = pd.concat([pd.read_csv(
                            f"{temp_folder}{os.sep}output_{i}.csv", sep=" ")
                                for i in range(num_proc)], ignore_index=True)
    output_df.to_csv(output_file, sep=" ", index=False)
    # cleaning mess
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
