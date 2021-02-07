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
PROGRAM_TITLE += "  Convertir '.var' a '.csv' DataFrame"+"\n"
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

def var_to_dataframe(var_path, curve_path):
    names = ['vvv','aov1','aov2','aov3']
    usecols = (0, 12, 13, 14)
    df = pd.read_csv(var_path, delim_whitespace=True, skiprows=1,
                                                names=names, usecols=usecols)
    df.to_csv(curve_path, sep=" ", index=False)

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
    params["(OUTPUT) DataFrame de curvas"] = params["(OUTPUT) DataFrame de curvas"]
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
                  "(OUTPUT) DataFrame de curvas": "/path/to/curves/file"}
    params = validate_params(params)
    return params

def vs_var_to_dataframe_front():
    prev_params_path = f'{cwd}{os.sep}prev_var2df_params.txt'
    params = get_params(prev_params_path)
    if len(sys.argv)==1:
        clear_screen()
        params = modify_params_interface(params)
    with open(prev_params_path, 'w', encoding="utf-8") as outfile:
        json.dump(params, outfile)
    var_to_dataframe(params["(INPUT)  Archivo .var"],
                    params["(OUTPUT) DataFrame de curvas"])
    print("\nDone!")

if __name__=="__main__":
    vs_var_to_dataframe_front()
    if len(sys.argv)==1:
        input("(ENTER) to continue.\n")
        print( '*'*40)
        print( '-'*40)
    exit()
