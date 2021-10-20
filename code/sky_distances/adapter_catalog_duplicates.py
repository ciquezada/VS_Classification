import os
import sys
import pandas as pd
import numpy as np
import shutil
from multiprocessing import Pool
import argparse
import json

cwd = os.path.abspath(f"{os.path.dirname(__file__)}")
# SI NO SE EJECUTA DESDE LA MISMA CARPETA, DEBE SER CON UN FRONTEND

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input_catalog", required=True,
                               help="Input catalog file ['ID', 'glon/RA', 'glat/dec'], change frame on config_file")
ap.add_argument("-o", "--output_duplicates", required=True,
                               help="Output catalog file")
ap.add_argument("-p", "--processes", default=1, type=int,
                               help="Parallel processes")
ap.add_argument("-c", "--duplicates_config", default=f"{cwd}{os.sep}default_duplicates_config.json",
                               help="Extractor config file (JSON)")
args = vars(ap.parse_args())

def run_catalog_duplicates(i_args):
    i, args = i_args
    temp_folder, input_file, config_file = args
    RUN_CODE_STRING = "python slow_sky_distances.py " # command line
    RUN_CODE_STRING += f"-i \"{temp_folder}{os.sep}sample_{i}.csv\" " # temp input file
    RUN_CODE_STRING += f"-fc \"{input_file}\" " # features selection
    RUN_CODE_STRING += f"-o \"{temp_folder}{os.sep}output_{i}.csv\" " # temp output file
    RUN_CODE_STRING += f"-c \"{config_file}\" " # temp output file
    os.system(RUN_CODE_STRING)

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
    input_file = args["input_catalog"]
    output_file = args["output_duplicates"]
    # CONFIG
    config_file = args["duplicates_config"]
    with open(config_file, 'r', encoding="utf-8") as infile:
        config_params = json.load(infile)
    temp_dir = config_params["TEMP_DIR"]
    # load var file and then prepare input file
    input_df = pd.read_csv(input_file, delim_whitespace=True)
    col_id = input_df.columns[0]
    # making needed directories
    temp_folder = f"{temp_dir}{os.sep}temp_0"
    temp_folder = os_mkdir(temp_folder)
    # splitting input file
    chunksize = int(np.ceil(input_df.shape[0]/num_proc))
    for i in range(num_proc):
        input_df.iloc[chunksize*i:chunksize*(i+1),:].to_csv(
                                        f"{temp_folder}{os.sep}sample_{i}.csv",
                                                        index=False, sep=" ")
    # calling catalog pipeline
    pool = Pool(num_proc)
    pool.map(run_catalog_duplicates, enumerate(
                                    [(temp_folder, input_file, config_file)]*num_proc
                                                ))
    pool.close()
    pool.join()
    # joining output parts and saving
    output_df = pd.concat([pd.read_csv(
                            f"{temp_folder}{os.sep}output_{i}.csv", delim_whitespace=True)
                                for i in range(num_proc)], ignore_index=True)
    # deleting duplicated rows
    if config_params["DROP_DUPLICATES"]:
        dups = output_df.apply(lambda x: "x".join(
                                    np.sort([x[col_id], x[f"{col_id}_2"]])),
                                                                        axis=1)
        output_df = output_df[~dups.duplicated()]
    # saving
    output_df.to_csv(output_file, sep=" ", index=False)
    # cleaning mess
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
