import os
import sys
import pandas as pd
import numpy as np
import shutil
from multiprocessing import Pool


def run_feets_extractor(i_args):
    i, args = i_args
    features_preset, temp_folder = args
    RUN_CODE_STRING = "python adapter_feets_extractor.py " # command line
    RUN_CODE_STRING += f"{temp_folder}{os.sep}input_{i}.csv " # temp input file
    RUN_CODE_STRING += f"{temp_folder}{os.sep}output_{i}.csv " # temp output file
    RUN_CODE_STRING += features_preset + " " # features selection
    os.system(RUN_CODE_STRING)

# In line 52 is the period selection
def period_selection(selection, df):
    if selection=="min_aov":
        return df.min(axis=1)
    elif selection=="aov1":
        return df["aov1"]

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
    num_proc = int(sys.argv[1])
    ks_curves_dir = sys.argv[2]
    curves_file = sys.argv[3]
    output_file = sys.argv[4]
    if len(sys.argv)>5:
        features_preset = sys.argv[5]
    else:
        features_preset = "test"
    # load curve file and then prepare input file
    curves_df = pd.read_csv(curves_file, sep=" ")
    input_df = curves_df[["vvv"]].copy()
    # Period selection by the case
    input_df["period"] = period_selection("aov1", curves_df[["aov1", "aov2"]])

    input_df["ks_path"] = curves_df.vvv.apply(lambda x:
                                            f"{ks_curves_dir}{os.sep}{x}.dat")
    if "label" in curves_df:
        input_df["label"] = curves_df.label
    del(curves_df)
    # making needed directories
    temp_folder = os_mkdir("temp_0")
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
