import os
import json
import sys
import pandas as pd
import numpy as np
from pprint import pprint


cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

PROGRAM_TITLE = '-'*40+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '          VS_Classification'+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '-'*40+"\n"
PROGRAM_TITLE += "\n"
PROGRAM_TITLE += ' VS extractor de features (Geryon2 mode)'+"\n"
PROGRAM_TITLE += "\n"

def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
    print(PROGRAM_TITLE)

def print_exit():
    print("")
    print( '    Abortando VS_Classification')
    print( '*'*40)
    print( '-'*40)

def params_to_script(params, i):
    RUN_script = ""

    #init
    execution_title = params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"]
    output_dir = params[0]["2.- Donde guardar la carpeta output"]
    num_proc = params[0]["3.- Numero de procesos"]
    vs_classificator_dir = os.path.abspath(f"{os.path.abspath(os.path.dirname(__file__))}{os.sep}..{os.sep}..")
    curve_file = params[1]["3.- Archivo con curvas (DataFrame)"]
    data_dir = params[1]["4.- Carpeta con .dat s"]

    feets_extractor = f"{vs_classificator_dir}{os.sep}code{os.sep}feets_extractor"
    send_mail = f"{vs_classificator_dir}{os.sep}code{os.sep}monitoring{os.sep}send_email.py"

    RUN_geryon_header = f"""#!/bin/bash
#
#PBS -V
#PBS -N {execution_title}
#PBS -k eo
#PBS -l nodes=1:ppn=1
#PBS -l walltime=72:00:00

TITLE=\"{execution_title}\"

NUM_PROC=\"{num_proc}\"
DATA_DIR=\"{data_dir}\"
OUTPUT_DIR=\"{output_dir}{os.sep}$TITLE\"

# .var to DataFrame
CURVES=\"{curve_file}\"
CURVES_FILE=\"$OUTPUT_DIR{os.sep}curves.csv\"

mkdir \"$OUTPUT_DIR\"
cp \"$CURVES\" \"$CURVES_FILE\"
# EXTRACT_FEATURES
cd \"{feets_extractor}\"
PROGRAM=\"extract_features.py\"
        """
    RUN_script += RUN_geryon_header

    if params[1]["1.- Extraer features"]:
        features_mode = params[1]["5.- Seleccion de features"]
        RUN_extract_features_1 = f"""
FEATURES_OUTPUT=\"$OUTPUT_DIR{os.sep}features.csv\"
FEATURES_EXTRACTOR_MODE=\"{features_mode}\"

# FEATURES
LOG=\"INICIADO
PROGRAM: $PROGRAM
Procceses: $NUMPROC
Curves Dir: $DATA_DIR
Curves File: $CURVES_FILE
OUTPUT: $FEATURES_OUTPUT
Extractor Mode: $FEATURES_EXTRACTOR_MODE\"
LOG_END=\"TERMINADO
PROGRAM: $PROGRAM
features en $FEATURES_OUTPUT \"
{'' if not i else '#'}python \"{send_mail}\" \"$TITLE\" \"$LOG\"
python $PROGRAM \"$NUM_PROC\" \"$DATA_DIR\" \"$CURVES_FILE\" \"$FEATURES_OUTPUT\" \"$FEATURES_EXTRACTOR_MODE\"
{'' if not i else '#'}python \"{send_mail}\" \"$TITLE\" \"$LOG_END\"

        """
        RUN_script += RUN_extract_features_1
    if params[1]["2.- Extraer postfeatures"]:
        postfeatures_mode = params[1]["6.- Seleccion de postfeatures"]
        RUN_extract_features_2 = f"""
# POSTFEATURES
POSTFEATURES_OUTPUT=\"$OUTPUT_DIR{os.sep}postfeatures.csv\"
POSTFEATURES_EXTRACTOR_MODE=\"{postfeatures_mode}\"

LOG=\"INICIADO
PROGRAM: $PROGRAM
Procceses: $NUMPROC
Curves Dir: $DATA_DIR
Curves File: $CURVES_FILE
OUTPUT: $POSTFEATURES_OUTPUT
Extractor Mode: $POSTFEATURES_EXTRACTOR_MODE\"
LOG_END=\"TERMINADO
PROGRAM: $PROGRAM
features en $POSTFEATURES_OUTPUT \"
{'' if not i else '#'}python \"{send_mail}\" \"$TITLE\" \"$LOG\"
python \"$PROGRAM\" \"$NUM_PROC\" \"$DATA_DIR\" \"$CURVES_FILE\" \"$POSTFEATURES_OUTPUT\" \"$POSTFEATURES_EXTRACTOR_MODE\"
{'' if not i else '#'}python \"{send_mail}\" \"$TITLE\" \"$LOG_END\"

        """
        RUN_script += RUN_extract_features_2
    RUN_end = """
echo \"done!\"
    """
    RUN_script += RUN_end
    return RUN_script

def export_to_script(params):
    RUN_script = params_to_script(params)
    with open("last_extract_features_script.sh", "w", encoding="utf-8") as fout:
        fout.write(RUN_script)
    os.system("chmod u+x last_extract_features_script.sh")

def get_default_params():
    initial_params = {"1.- Nombre del sample (Carpeta con outputs)(sin espacios)": "Nombre_del_sample",
                        "2.- Donde guardar la carpeta output": "/path/to/save/output/folder",
                        "3.- Numero de procesos": 20}

    extract_features_params = {"1.- Extraer features": 1,
                                "2.- Extraer postfeatures": 1,
                                "3.- Archivo con curvas (DataFrame)": "/path/to/curve/file",
                                "4.- Carpeta con .dat s": "/path/to/.dat/folder",
                                "5.- Seleccion de features": "rrlyr",
                                "6.- Seleccion de postfeatures": "rrlyr_postfeatures"}

    params = [initial_params, extract_features_params]
    return params

def validate_params(params):
    elec_in = {"y":1, "si":1, "1":1, "0":0, "yes":1, "no":0, "n":0, 1:1, 0:0}
    params[0]["3.- Numero de procesos"] = int(params[0]["3.- Numero de procesos"])
    params[1]["1.- Extraer features"] = elec_in[params[1]["1.- Extraer features"]]
    params[1]["2.- Extraer postfeatures"] = elec_in[params[1]["2.- Extraer postfeatures"]]
    return params

def modify_params(params):
    print("Modificar parametros...")
    for k in params:
        mod = input(f"{k} ({params[k]}): ")
        if mod=="":
            continue
        params[k] = mod
    return params

def modify_params_interface(params):
    i = 0
    n = len(params)
    while True:
        clear_screen()
        params = validate_params(params)
        if i >= n:
            final_election = 'ELECTION'
            while final_election not in ['y', 'n', 'p', 'q', '']:
                print("Confirmar ejecucion")
                final_election = input("(y or ENTER) yes, (n) no, (p) previous, (q) quit: ")
            if final_election == 'y' or final_election == '':
                break
            elif final_election == 'p' or final_election == 'n':
                i = i - 1
                continue
            elif final_election == 'q':
                print_exit()
                exit()
                break
        election = "ELECTION"
        election_msg = ["Parametros Iniciales", "Extractor de Features"]
        print(f"Paso {i+1}/{n}: {election_msg[i]}")
        pprint(params[i])
        while election not in ['y', 'n', 'p', 'q', '']:
            election = input("Modificar?: (y) yes, (n or ENTER) no, (p) previous, (q) quit: ")

        if election == 'y':
            clear_screen()
            print(f"Paso {i+1}/{n}: {election_msg[i]}")
            params[i] = modify_params(params[i])
        elif election == '' or election == "n":
            i = i + 1
        elif election == 'p':
            if i == 0:
                continue
            i = i - 1
            continue
        elif election == 'q':
            print_exit()
            exit()
            break

    return params

def write_join_features_python(params, subdir_list):
    execution_title = params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"]
    output_dir = params[0]["2.- Donde guardar la carpeta output"]
    output_dir = f"{output_dir}{os.sep}{execution_title}"
    new_python_script = f"{output_dir}{os.sep}join_features.py"
    subdir_list = ",\n".join(['\"'+dir+'\"' for dir in subdir_list])
    python_str = f"""import glob
import shutil
import os
import pandas as pd
import numpy as np


subdir_list = [{subdir_list}]
"""
    python_str += """
curves_df = pd.concat([pd.read_csv(f\"{dir}{os.sep}curves.csv\", sep=\" \")
                            for dir in subdir_list], ignore_index=True)
"""
    python_str += f"""
curves_df.to_csv(\"{output_dir}{os.sep}curves.csv\", sep=\" \", index=False)
del(curves_df)
"""

    if params[1]["1.- Extraer features"]:
        python_str += """
features_df = pd.concat([pd.read_csv(f\"{dir}{os.sep}features.csv\", sep=\" \")
                                    for dir in subdir_list], ignore_index=True)
"""
        python_str += f"""
features_df.to_csv(\"{output_dir}{os.sep}features.csv\", sep=\" \", index=False)
del(features_df)
"""
    if params[1]["2.- Extraer postfeatures"]:
        python_str += """
postfeatures_df = pd.concat([pd.read_csv(f\"{dir}{os.sep}postfeatures.csv\", sep=\" \")
                                    for dir in subdir_list], ignore_index=True)
"""
        python_str += f"""
postfeatures_df.to_csv(\"{output_dir}{os.sep}postfeatures.csv\", sep=\" \", index=False)
del(postfeatures_df)
"""
    python_str += f"""

fileList1 = glob.glob(\"run_*\")
fileList2 = glob.glob(\"*_curves.csv\")

for filePath1 in fileList1:
    try:
        os.remove(filePath1)
    except:
        print("Error while deleting file : ", filePath1)

for filePath2 in fileList2:
    try:
        os.remove(filePath2)
    except:
        print("Error while deleting file : ", filePath2)

for dir in subdir_list:
    try:
        shutil.rmtree(dir, ignore_errors=True)
    except:
        print("Error while deleting file : ", dir)

try:
    os.remove("join_features.py")
except:
    print("Error while deleting file : ", filePath2)

"""

    python_str = python_str.replace("\\", "\\\\")
    with open(f"{new_python_script}", "w", encoding="utf-8") as fout:
        fout.write(python_str)

def run_on_geryon_extract_features(params):
    subdir_list = []
    if not int(params[1]["1.- Extraer features"]) and not int(params[1]["2.- Extraer postfeatures"]):
        return subdir_list
    execution_title = params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"]
    output_dir = params[0]["2.- Donde guardar la carpeta output"]
    num_proc = int(params[0]["3.- Numero de procesos"])
    curve_file = params[1]["3.- Archivo con curvas (DataFrame)"]

    new_output_dir = f"{output_dir}{os.sep}{execution_title}"
    try:
        os.mkdir(new_output_dir)
    except OSError as error:
        print(error)
    # splitting input file
    input_df = pd.read_csv(curve_file, sep=" ")
    chunksize = int(np.ceil(input_df.shape[0]/num_proc))
    for i in range(num_proc):
        new_execution_title = f"{execution_title}_{i}"
        new_run_script = f"{new_output_dir}{os.sep}run_{new_execution_title}.sh"
        new_num_proc = 1
        new_curve_file = f"{new_output_dir}{os.sep}{new_execution_title}_curves.csv"
        input_df.iloc[chunksize*i:chunksize*(i+1),:].to_csv(
                                        f"{new_curve_file}", index=False, sep=" ")
        new_params = [params[0].copy(), params[1].copy()]
        new_params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"] = new_execution_title
        new_params[0]["2.- Donde guardar la carpeta output"] = new_output_dir
        new_params[0]["3.- Numero de procesos"] = new_num_proc
        new_params[1]["3.- Archivo con curvas (DataFrame)"] = new_curve_file
        RUN_script = params_to_script(new_params, i)
        with open(f"{new_run_script}", "w", encoding="utf-8") as fout:
            fout.write(RUN_script)
        os.system(f"qsub \"{new_run_script}\"")
        subdir_list.append(f"{new_output_dir}{os.sep}{new_execution_title}")
    return subdir_list

def write_final_script(params, subdir_list):
    execution_title = params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"]
    output_dir = params[0]["2.- Donde guardar la carpeta output"]
    output_dir = f"{output_dir}{os.sep}{execution_title}"
    RUN_script = f"""
cd \"{output_dir}\"

"""
    if int(params[1]["1.- Extraer features"]) or int(params[1]["2.- Extraer postfeatures"]):
        write_join_features_python(params, subdir_list)
        RUN_script += "python join_features.py\n"
    RUN_script += f"rm 'FINAL_SCRIPT.sh'\n"
    RUN_script += f"echo 'done!'"
    with open(f"{output_dir}{os.sep}FINAL_SCRIPT.sh", "w", encoding="utf-8") as fout:
        fout.write(RUN_script)
    os.system(f"chmod u+x \"{output_dir}{os.sep}FINAL_SCRIPT.sh\"")
    print(f"\nNo olvides ejecutar:\n{output_dir}{os.sep}FINAL_SCRIPT.sh")
    print("Cuando terminen todos los procesos de Geryon2\n")

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
        params = get_default_params()
    params = validate_params(params)
    return params

def absolute_params(params):
    params[0]["2.- Donde guardar la carpeta output"] = os.path.abspath(
                            params[0]["2.- Donde guardar la carpeta output"])
    params[1]["3.- Archivo con curvas (DataFrame)"] = os.path.abspath(
                                        params[1]["3.- Archivo con curvas (DataFrame)"])
    params[1]["4.- Carpeta con .dat s"] = os.path.abspath(
                                params[1]["4.- Carpeta con .dat s"])
    return params

def vs_extract_features_geryon2_front():
    prev_params_path = f'{cwd}{os.sep}prev_extract_features_params.txt'
    params = get_params(prev_params_path)
    if len(sys.argv)==1:
        clear_screen()
        params = modify_params_interface(params)
    with open(prev_params_path, 'w', encoding="utf-8") as outfile:
        json.dump(params, outfile)
    params = absolute_params(params)
    subdir_list = run_on_geryon_extract_features(params)
    write_final_script(params, subdir_list)
    print("\nDone!")

if __name__=="__main__":
    vs_extract_features_geryon2_front()
    if len(sys.argv)==1:
        input("(ENTER) to continue.\n")
        print( '*'*40)
        print( '-'*40)
    exit()
