import os
import sys
import pandas as pd
import numpy as np
from multiprocessing import Pool


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

if __name__=="__main__":
    # user input
    num_proc = int(sys.argv[1])
    curves_dir = sys.argv[2]
    curves_file = sys.argv[3]
    output_file = sys.argv[4]
    # making needed directories
    gen = (x for x in range(1,99999))
    temp_folder = "temp_0"
    output_pdf_folder = "output_pdf_0"
    while os.path.exists(temp_folder) or os.path.exists(output_pdf_folder):
        n = next(gen)
        temp_folder = f"temp_{n}"
        output_pdf_folder = f"output_pdf_{n}"
    os.system(f'mkdir {temp_folder}')
    os.system(f'mkdir {output_pdf_folder}')
    # load curve file and then prepare input file
    curves_df = pd.read_csv(curves_file, sep=" ")
    input_df = curves_df[["vvv", "aov1"]].copy()
    input_df["ks"] = curves_df.vvv.apply(lambda x:
                                                f"{curves_dir}{os.sep}{x}.dat")
    input_df["j"] = f"j{os.sep}j_empty.dat"
    input_df["h"] = f"h{os.sep}h_empty.dat"
    input_df["output_pdf"] = curves_df.vvv.apply(lambda x:
                                                f"{output_pdf_folder}{os.sep}{x}.pdf")
    del(curves_df)
    # splitting input file
    chunksize = int(np.ceil(input_df.shape[0]/num_proc))
    for i in range(num_proc):
        input_df.iloc[chunksize*i:chunksize*(i+1),:].to_csv(
                                        f"{temp_folder}{os.sep}input_{i}.csv",
                                                        index=False, sep=" ")
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
                            f"{temp_folder}{os.sep}output_{i}.csv", sep=" ")
                                for i in range(num_proc)], ignore_index=True)
    output_df.to_csv(output_file, sep=" ", index=False)
    # cleaning mess
    if os.path.exists(temp_folder):
        os.system(f'rm -r {temp_folder}')
    if os.path.exists(output_pdf_folder):
        os.system(f'rm -r {output_pdf_folder}')
