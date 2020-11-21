import os
import sys
import pandas as pd
import numpy as np
from multiprocessing import Pool


def run_feets_extractor(arg):
    i, features_preset = arg
    RUN_CODE_STRING = "python adapter_feets_extractor.py " # command line
    RUN_CODE_STRING += "temp" + os.sep + "input_{}.csv " # temp input file
    RUN_CODE_STRING += "temp" + os.sep + "output_{}.csv " # temp output file
    RUN_CODE_STRING += features_preset + " " # features selection
    os.system(RUN_CODE_STRING.format(i, i))

# In line 37 is the period selection
def period_selection(selection, df):
    if selection=="min_aov":
        return df.min(axis=1)
    elif selection=="aov1":
        return df["aov1"]

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
                                    ks_curves_dir + os.sep + x + ".dat")
    del(curves_df)
    # making needed directories
    if not os.path.exists("temp"):
        os.system('mkdir temp')
    # splitting input file
    chunksize = int(np.ceil(input_df.shape[0]/num_proc))
    for i in range(num_proc):
        input_df.iloc[chunksize*i:chunksize*(i+1),:].to_csv(
                                    "temp" + os.sep + "input_{}.csv".format(i),
                                                    index=False, sep=" ")
    # calling pyfiner pipeline
    pool = Pool(num_proc)
    pool.map(run_feets_extractor, enumerate([features_preset]*num_proc))
    # joining output parts and saving
    output_df = pd.concat([pd.read_csv("temp{}output_{}.csv".format(os.sep, i), sep=" ")
                            for i in range(num_proc)], ignore_index=True)
    output_df.to_csv(output_file, sep=" ", index=False)
    # cleaning mess
    if os.path.exists("temp"):
        os.system('rm -r temp')
