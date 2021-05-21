import os
import sys
import pandas as pd
import numpy as np
from multiprocessing import Pool
import shutil


TEMP_DIR = os.path.abspath("/data4/ciquezada/VS_Classification/code/ks_metallicities")
# TEMP_DIR = "..\\ks_metallicities"

"""
Adapter for Ks_metalicity to work with VS_Classification curves files format
[vvv, aov1, aov2, ...] and parallel procceses

Args:
    parallel procceses (int): how many parallel procceses
    curves_dir (str): directory of curves .dat files
    curves_file (str): path to Dataframe of curves [vvv, aov1, aov2, ...]
    output_file (str): path to output Dataframe file returned by pyfiner

Raises:
    bunch of inofesive warnings

Returns:
    output_df (DataFrame): metallicity output returned by pyfiner
    output_pdf/.. (pdf): fitted curves returned by pyfiner
"""

def run_ks_metallicity(i_args):
    i, args = i_args
    temp_folder, output_pdf_folder = args
    RUN_CODE_STRING = "python Ks_metalicity.py " # command line
    RUN_CODE_STRING += f"{temp_folder}{os.sep}input_{i}.csv " # temp input file
    RUN_CODE_STRING += f"{temp_folder}{os.sep}output_{i}.csv " # temp output file
    RUN_CODE_STRING += f"{temp_folder}{os.sep}pymerlin_{i}.csv " # temp pymerlin file
    os.system(RUN_CODE_STRING)

def run_only_pyfiner(i_args):
    i, args = i_args
    temp_folder, output_pdf_folder = args
    RUN_CODE_STRING = "python Ks_metalicity.py " # command line
    RUN_CODE_STRING += f"{temp_folder}{os.sep}input_{i}.csv " # temp input file
    RUN_CODE_STRING += f"{temp_folder}{os.sep}output_{i}.csv " # temp output file
    RUN_CODE_STRING += "-p-no_pymerlin " # temp pymerlin file
    os.system(RUN_CODE_STRING)

def os_mkdir(folder_name, folder_name_pdf):
    # making needed directories
    gen = (x for x in range(1,99999))
    aux_folder_name = folder_name[:-1]
    aux_folder_name_pdf = folder_name_pdf[:-1]
    while True:
        try:
            os.mkdir(folder_name)
            os.mkdir(folder_name_pdf)
            break
        except OSError as error:
            i = next(gen)
            folder_name = f"{aux_folder_name}{i}"
            folder_name_pdf = f"{aux_folder_name_pdf}{i}"
    return folder_name, folder_name_pdf

if __name__=="__main__":
    # user input
    num_proc = int(sys.argv[1])
    curves_dir_ks = sys.argv[2]
    curves_file = sys.argv[3]
    output_file = sys.argv[4]
    curves_dir_j = sys.argv[sys.argv.find("-jdir")+1] if "-jdir" in sys.argv else False
    curves_dir_h = sys.argv[sys.argv.find("-hdir")+1] if "-hdir" in sys.argv else False
    # CONFIG
    temp_dir = TEMP_DIR
    # making needed directories
    temp_folder = f"{temp_dir}{os.sep}temp_0"
    output_pdf_folder = f"{temp_dir}{os.sep}output_pdf_0"
    temp_folder, output_pdf_folder = os_mkdir(temp_folder, output_pdf_folder)
    # load curve file and then prepare input file
    curves_df = pd.read_csv(curves_file, sep=" ")
    input_df = curves_df[["vvv", "aov1"]].copy()
    input_df["ks"] = curves_df.vvv.apply(lambda x:
                                            f"{curves_dir_ks}{os.sep}{x}.dat")
    input_df["j"] = f"j{os.sep}j_empty.dat"
    input_df["h"] = f"h{os.sep}h_empty.dat"
    if curves_dir_j:
        input_df["j"] = curves_df.vvv.apply(lambda x:
                                            f"{curves_dir_j}{os.sep}{x}.dat")
    if curves_dir_h:
        input_df["h"] = curves_df.vvv.apply(lambda x:
                                            f"{curves_dir_h}{os.sep}{x}.dat")
    input_df["output_pdf"] = curves_df.vvv.apply(lambda x:
                                            f"{output_pdf_folder}{os.sep}{x}.pdf")
    del(curves_df)
    # splitting input file
    chunksize = int(np.ceil(input_df.shape[0]/num_proc))
    for i in range(num_proc):
        input_df.iloc[chunksize*i:chunksize*(i+1),:].to_csv(
                                        f"{temp_folder}{os.sep}input_{i}.csv",
                                                        index=False, header=False)
    # calling pyfiner pipeline
    pool = Pool(num_proc)
    if not "-p-no_pymerlin" in sys.argv:
        pool.map(run_ks_metallicity, enumerate([
                                                (temp_folder, output_pdf_folder)
                                                ]*num_proc))
    else:
        pool.map(run_only_pyfiner, enumerate([
                                                (temp_folder, output_pdf_folder)
                                                ]*num_proc))
    pool.close()
    pool.join()
    # joining output parts and saving
    output_df = pd.concat([pd.read_csv(
                            f"{temp_folder}{os.sep}output_{i}.csv")
                                for i in range(num_proc)], ignore_index=True)
    output_df.to_csv(output_file, sep=" ", index=False)
    # cleaning mess
    # cleaning mess
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
    # if os.path.exists(output_pdf_folder):
    #     shutil.rmtree(output_pdf_folder, ignore_errors=True)
