import pandas as pd
import os
import sys
import json
from pprint import pprint


cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

PROGRAM_TITLE = '-'*40+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '          VS_Classification'+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '-'*40+"\n"
PROGRAM_TITLE += "\n"
PROGRAM_TITLE += "         Armar custom output"+"\n"
PROGRAM_TITLE += "\n"

def print_exit():
    print()
    print( '-'*40)
    print( '*'*40)
    print( '    Cerrando VS_Classification')
    print( '*'*40)
    print( '-'*40)

def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
    print(PROGRAM_TITLE)

def build_output(var_path, features_path, postfeatures_path,
                                                results_path, out_df):
    names = ['filename','Q','AoV1','NPoints1']
    usecols = (0, 11, 12, 17)
    var_df = pd.read_csv(var_path, delim_whitespace=True, skiprows=1,
                                                names=names, usecols=usecols)
    features_df = pd.read_csv(features_path, sep=" ")[["filename", "a0", "iqr", "GP_Skew",
                                                        "GP_RiseDownRatio", "GP_DownRatio"]]
    postfeatures_df = pd.read_csv(postfeatures_path, sep=" ")[["filename", "post_N_peaks", "post_SN_ratio",
                                                                "post_alias_score", "post_mseRRab",
                                                                    "post_mseRRc", "post_N_points"
                                                                    ]]
    results_df = pd.read_csv(results_path, sep=" ")[["filename", "RRab"]]

    out_df = pd.merge(left=var_df, right=features_df, on="filename")
    out_df = pd.merge(left=var_df, right=postfeatures_df, on="filename")
    out_df = pd.merge(left=var_df, right=results_df, on="filename")
    out_df = out_df[['filename', "a0", "iqr", 'AoV1', "RRab", 'Q',
                        "post_SN_ratio", "GP_RiseDownRatio",
                         "GP_DownRatio", "GP_Skew", "post_mseRRab",
                            "post_mseRRc", 'NPoints1', #"post_N_points",
                            "post_N_peaks", "post_alias_score"]]
    out_df.columns = ["ID", "Ks", "Amp", "AoV1", "Prob", "Q", "S/N",
                        "R/D", "D", "Skew", "MSErrab", "MSErrc", "NPoints1", "NPoints2",
                         "Nofmax", "Nbins"]
    out_df.to_csv(out_df, sep=" ", index=False)


def modify_params(params):
    print("Modificar parametros...")
    for k in params:
        mod = input(f"{k} ({params[k]}): ")
        if mod=="":
            continue
        params[k] = mod
    return params

def modify_params_interface(params):
    while True:
        election = "election"
        final_election = "election"
        clear_screen()
        pprint(params)
        print()
        while election not in ['y', 'n', '', 'q']:
            election = input("Modificar?: (y) yes, (n or ENTER) no, (q) quit: ")
        if election == 'n' or election == '':
            while final_election not in ['y', 'n', 'q', '']:
                print("Confirmar ejecucion")
                final_election = input("(y or ENTER) yes, (n) no, (q) quit: ")
            if final_election == 'y' or final_election == '':
                return params
            elif election == 'n':
                continue
            elif final_election == 'q':
                print_exit()
                exit()
                break
        elif election == 'y':
            clear_screen()
            params = modify_params(params)
            params = validate_params(params)
        elif election == 'q':
            print_exit()
            exit()
            break

def validate_params(params):
    params["(INPUT)  Archivo .var"] = params["(INPUT)  Archivo .var"]
    params["(INPUT)  Archivo con features"] = params["(INPUT)  Archivo con features"]
    params["(INPUT)  Archivo con postfeatures"] = params["(INPUT)  Archivo con postfeatures"]
    params["(INPUT)  Archivo con results"] = params["(INPUT)  Archivo con results"]
    params["(OUTPUT) DataFrame output"] = params["(OUTPUT) DataFrame output"]
    return params

def get_params(params_file):
    if len(sys.argv)>1:
        params_file = sys.argv[1]
        if not os.path.exists(params_file):
            print("ERROR: '"+params_file+"' not found")
            print_exit()
            exit()
    if os.path.exists(params_file):
        with open(params_file, 'r', encoding="utf-8") as infile:
            params = json.load(infile)
    else:
        params = {"(INPUT)  Archivo .var": "/path/to/var/file",
                  "(INPUT)  Archivo con features": "/path/to/features/file",
                  "(INPUT)  Archivo con postfeatures": "/path/to/postfeatures/file",
                  "(INPUT)  Archivo con results": "/path/to/results/file",
                  "(OUTPUT) DataFrame output": "/path/to/output/file"}
    params = validate_params(params)
    return params

def vs_build_custom_output_font():
    prev_params_path = f'{cwd}{os.sep}prev_custom_output_params.txt'
    params = get_params(prev_params_path)
    if len(sys.argv)==1:
        clear_screen()
        params = modify_params_interface(params)
    with open(prev_params_path, 'w', encoding="utf-8") as outfile:
        json.dump(params, outfile)
    build_output(params["(INPUT)  Archivo .var"],
                    params["(INPUT)  Archivo con features"],
                    params["(INPUT)  Archivo con postfeatures"],
                    params["(INPUT)  Archivo con results"],
                    params["(OUTPUT) DataFrame output"])
    print("\nDone!")

if __name__=="__main__":
    vs_build_custom_output_font()
    if len(sys.argv)==1:
        input("(ENTER) to continue.\n")
        print( '*'*40)
        print( '-'*40)
    exit()
