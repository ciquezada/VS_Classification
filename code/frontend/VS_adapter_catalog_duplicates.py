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
PROGRAM_TITLE += "       Duplicados de un catalogo"+"\n"
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

def run_pipeline(params):
    #init
    catalog_in = params["(INPUT)  Catalogo [ID, glon, glat]"]
    catalog_out = params["(OUTPUT) Catalogo con posibles duplicados"]
    num_proc = params["Numero de procesos"]
    vs_classificator_dir = os.path.abspath(f"{os.path.abspath(os.path.dirname(__file__))}{os.sep}..{os.sep}..")
    # EXTRACT_FEATURES
    print()
    os.chdir(f"{vs_classificator_dir}{os.sep}code{os.sep}sky_distances")
    print("Buscando duplicados...  ", end='', flush=True)
    os.system(f"python adapter_catalog_duplicates.py -p \"{num_proc}\" -i \"{catalog_in}\" -o \"{catalog_out}\"")
    print("OK")


def absolute_params(params):
    params["(INPUT)  Catalogo [ID, glon, glat]"] = os.path.abspath(
                            params["(INPUT)  Catalogo [ID, glon, glat]"])
    params["(OUTPUT) Catalogo con posibles duplicados"] = os.path.abspath(
                            params["(OUTPUT) Catalogo con posibles duplicados"])

    return params

def validate_params(params):
    params["(INPUT)  Catalogo [ID, glon, glat]"] = params["(INPUT)  Catalogo [ID, glon, glat]"]
    params["(OUTPUT) Catalogo con posibles duplicados"] = params["(OUTPUT) Catalogo con posibles duplicados"]
    params["Numero de procesos"] = int(params["Numero de procesos"])
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
        params = {"(INPUT)  Catalogo [ID, glon, glat]": "/path/to/Catalog/file",
                  "(OUTPUT) Catalogo con posibles duplicados": "/path/to/curves/file",
                  "Numero de procesos": 1}
    params = validate_params(params)
    return params

def adapter_catalog_duplicates_front():
    prev_params_path = f'{cwd}{os.sep}prev_adapter_catalog_duplicates_params.txt'
    params = get_params(prev_params_path)
    if len(sys.argv)==1:
        clear_screen()
        params = modify_params_interface(params)
    with open(prev_params_path, 'w', encoding="utf-8") as outfile:
        json.dump(params, outfile)
    params = absolute_params(params)
    run_pipeline(params)
    print("\nDone!")

if __name__=="__main__":
    adapter_catalog_duplicates_front()
    if len(sys.argv)==1:
        input("(ENTER) to continue.\n")
        print( '*'*40)
        print( '-'*40)
    exit()
