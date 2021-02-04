import os
import json
import sys
import pandas as pd
import numpy as np
from pprint import pprint


PROGRAM_TITLE = '-'*40+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '          VS_Classification'+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '-'*40+"\n"


def get_run_script(params, i):
    RUN_script = ""

    #init
    execution_title = params[0]["1.- Nombre del sample (sin espacios)"]
    data_dir = params[0]["2.- Carpeta con .dat s"]
    output_dir = params[0]["3.- Donde guardar la carpeta output"]
    num_proc = params[0]["4.- Numero de procesos"]
    vs_classificator_dir = params[0]["5.- Carpeta que contiene VS_Classification"]

    if i==-1:
        RUN_geryon_header = f"""#!/bin/bash
#
#PBS -V
#PBS -N {execution_title}
#PBS -k eo
#PBS -l nodes=2:ppn=10
#PBS -l walltime=4:00:00
    """
    else:
            RUN_geryon_header = f"""#!/bin/bash
#
#PBS -V
#PBS -N {execution_title}
#PBS -k eo
#PBS -l nodes=1:ppn=1
#PBS -l walltime=3:00:00
        """
    RUN_init = f"""
TITLE=\"{execution_title}\"

NUM_PROC=\"{num_proc}\"
DATA_DIR=\"{data_dir}\"
OUTPUT_DIR=\"{output_dir}/$TITLE\"


    """

    RUN_script = RUN_geryon_header + RUN_init

    if int(params[1]["1.- Extraer features"]) or int(params[1]["2.- Extraer postfeatures"]):
        curve_file = params[1]["3.- Archivo con curvas (DataFrame)"]
        RUN_extract_features_0 = f"""
# .var to DataFrame
CURVES=\"{curve_file}\"
CURVES_FILE=\"$OUTPUT_DIR/curves.csv\"

mkdir \"$OUTPUT_DIR\"
cp \"$CURVES\" \"$CURVES_FILE\"
# EXTRACT_FEATURES
cd {vs_classificator_dir}/VS_Classification/code/feets_extractor
PROGRAM=\"extract_features.py\"
        """
        RUN_script += RUN_extract_features_0

    if params[1]["1.- Extraer features"]:
        features_mode = params[1]["4.- Seleccion de features"]
        RUN_extract_features_1 = f"""
FEATURES_OUTPUT=\"$OUTPUT_DIR/features.csv\"
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
{'' if not i else '#'}python {vs_classificator_dir}/VS_Classification/code/monitoring/send_email.py \"$TITLE\" \"$LOG\"
python $PROGRAM $NUM_PROC $DATA_DIR $CURVES_FILE $FEATURES_OUTPUT $FEATURES_EXTRACTOR_MODE
{'' if not i else '#'}python {vs_classificator_dir}/VS_Classification/code/monitoring/send_email.py \"$TITLE\" \"$LOG_END\"

        """
        RUN_script += RUN_extract_features_1
    if params[1]["2.- Extraer postfeatures"]:
        postfeatures_mode = params[1]["5.- Seleccion de postfeatures"]
        RUN_extract_features_2 = f"""
# POSTFEATURES
POSTFEATURES_OUTPUT=\"$OUTPUT_DIR/postfeatures.csv\"
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
{'' if not i else '#'}python {vs_classificator_dir}/VS_Classification/code/monitoring/send_email.py \"$TITLE\" \"$LOG\"
python $PROGRAM $NUM_PROC $DATA_DIR $CURVES_FILE $POSTFEATURES_OUTPUT $POSTFEATURES_EXTRACTOR_MODE
{'' if not i else '#'}python {vs_classificator_dir}/VS_Classification/code/monitoring/send_email.py \"$TITLE\" \"$LOG_END\"

        """
        RUN_script += RUN_extract_features_2

    if params[2]["1.- Clasificar"]:
        train_file = params[2]["2.- Archivo con training features"]
        classify_mode = params[2]["3.- Modo del Clasificador"]
        RUN_classify = f"""
# CLASSIFY ONLYRR
cd {vs_classificator_dir}/VS_Classification/code/rf_classificator
PROGRAM=\"classify.py\"
FEATURES_FILE=\"$OUTPUT_DIR/features.csv\"
PRESET_MODE=\"{classify_mode}\"
TRAIN_FEATURES=\"{train_file}\"
RESULTS_FILE=\"$OUTPUT_DIR/results.csv\"

LOG_MSG=\"INICIADO
Proccesors: $NUM_PROC
Train Features: $TRAIN_FEATURES
Features File: $FEATURES_FILE
Output: $RESULTS_FILE
Preset Mode: $PRESET_MODE\"
LOG_MSG_END=\"TERMINADO
CV en $OUTPUT_DIR\"
python {vs_classificator_dir}/VS_Classification/code/monitoring/send_email.py \"$TITLE\" \"$LOG_MSG\"
python $PROGRAM $NUM_PROC $TRAIN_FEATURES $FEATURES_FILE $RESULTS_FILE $PRESET_MODE
python {vs_classificator_dir}/VS_Classification/code/monitoring/send_email.py \"$TITLE\" \"$LOG_MSG_END\"

        """
        RUN_script += RUN_classify

    RUN_end = """
echo \"done!\"
    """
    RUN_script += RUN_end
    return RUN_script

def get_initial_params():
    initial_params = {"1.- Nombre del sample (sin espacios)": "Nombre_del_sample",
                        "2.- Carpeta con .dat s": "/path/to/.dat/folder",
                        "3.- Donde guardar la carpeta output": "/path/to/save/output/folder",
                        "4.- Numero de procesos": 20,
                        "5.- Carpeta que contiene VS_Classification": "~"}

    extract_features_params = {"1.- Extraer features": 1,
                                "2.- Extraer postfeatures": 1,
                                "3.- Archivo con curvas (DataFrame)": "/path/to/curve/file",
                                "4.- Seleccion de features": "rrlyr",
                                "5.- Seleccion de postfeatures": "rrlyr_postfeatures"}

    classify_params = {"1.- Clasificar": 1,
                        "2.- Archivo con training features": "/path/to/train/file",
                        "3.- Modo del Clasificador": "rrlyr"}

    params = [initial_params, extract_features_params, classify_params]
    return params

def rectify(params):
    elec_in = {"y":1, "si":1, "1":1, "0":0, "yes":1, "no":0, "n":0, 1:1, 0:0}
    params[0]["4.- Numero de procesos"] = int(params[0]["4.- Numero de procesos"])
    params[1]["1.- Extraer features"] = elec_in[params[1]["1.- Extraer features"]]
    params[1]["2.- Extraer postfeatures"] = elec_in[params[1]["2.- Extraer postfeatures"]]
    params[2]["1.- Clasificar"] = elec_in[params[2]["1.- Clasificar"]]
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
    while True:
        os.system("clear")
        print(PROGRAM_TITLE)
        params = rectify(params)
        if i >= 3:
            final_election = 'ELECTION'
            while final_election not in ['y', 'n', 'p', 'q', '']:
                print("Confirmar ejecucion")
                final_election = input("(y or ENTER) yes, (n) no, (p) previous, (q) quit: \n")
            if final_election == 'y' or final_election == '':
                break
            elif final_election == 'p' or final_election == 'n':
                i = i - 1
                continue
            elif final_election == 'q':
                print( '-'*40)
                print( '*'*40)
                print( '    Abortando VS_Classification')
                print( '*'*40)
                print( '-'*40)
                exit()
                break
        election = "ELECTION"
        election_msg = ["Parametros Iniciales", "Extractor de Features", "Clasificador"]
        print(f"Paso {i+1}/{3}: {election_msg[i]}")
        pprint(params[i])
        while election not in ['y', 'n', 'p', 'q', '']:
            election = input("Modificar?: (y) yes, (n or ENTER) no, (p) previous, (q) quit: \n")

        if election == 'y':
            os.system("clear")
            print(PROGRAM_TITLE)
            print(f"Paso {i+1}/{3}: {election_msg[i]}")
            params[i] = modify_params(params[i])
        elif election == '' or election == "n":
            i = i + 1
        elif election == 'p':
            if i == 0:
                # print( 'No hay pasos previos a este!!')
                continue
            i = i - 1
            continue
        elif election == 'q':
            print( '-'*40)
            print( '*'*40)
            print( '    Abortando VS_Classification')
            print( '*'*40)
            print( '-'*40)
            exit()
            break
    return params

def write_join_features_python(params, subdir_list):
    execution_title = params[0]["1.- Nombre del sample (sin espacios)"]
    output_dir = params[0]["3.- Donde guardar la carpeta output"]
    output_dir = f"{output_dir}{os.sep}{execution_title}"
    new_python_script = f"{output_dir}{os.sep}join_features.py"
    subdir_list = ",\n".join(['\"'+dir+'\"' for dir in subdir_list])
    python_str = f"""
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
del(features_df)
"""
    python_str = python_str.replace("\\", "\\\\")
    with open(f"{new_python_script}", "w") as fout:
        fout.write(python_str)

def write_final_classify_script(params):
    execution_title = params[0]["1.- Nombre del sample (sin espacios)"]
    output_dir = params[0]["3.- Donde guardar la carpeta output"]
    output_dir = f"{output_dir}{os.sep}{execution_title}"
    new_run_script = f"{output_dir}{os.sep}submit_classification.sh"
    new_params = [params[0].copy(), params[1].copy(), params[2].copy()]
    new_params[1]["1.- Extraer features"] = 0
    new_params[1]["2.- Extraer postfeatures"] = 0
    RUN_script = get_run_script(new_params, -1)
    with open(f"{new_run_script}", "w") as fout:
        fout.write(RUN_script)

def run_on_geryon_extract_features(params):
    subdir_list = []
    if not int(params[1]["1.- Extraer features"]) and not int(params[1]["2.- Extraer postfeatures"]):
        return subdir_list
    execution_title = params[0]["1.- Nombre del sample (sin espacios)"]
    output_dir = params[0]["3.- Donde guardar la carpeta output"]
    num_proc = int(params[0]["4.- Numero de procesos"])
    curve_file = params[1]["3.- Archivo con curvas (DataFrame)"]

    new_output_dir = f"{output_dir}{os.sep}{execution_title}"
    os.system(f'mkdir {new_output_dir}')
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
        new_params = [params[0].copy(), params[1].copy(), params[2].copy()]
        new_params[0]["1.- Nombre del sample (sin espacios)"] = new_execution_title
        new_params[0]["3.- Donde guardar la carpeta output"] = new_output_dir
        new_params[0]["4.- Numero de procesos"] = new_num_proc
        new_params[1]["3.- Archivo con curvas (DataFrame)"] = new_curve_file
        new_params[2]["1.- Clasificar"] = 0
        RUN_script = get_run_script(new_params, i)
        with open(f"{new_run_script}", "w") as fout:
            fout.write(RUN_script)
        os.system(f"qsub {new_run_script}")
        subdir_list.append(f"{new_output_dir}{os.sep}{new_execution_title}")
    return subdir_list

def write_final_script(params, subdir_list):
    execution_title = params[0]["1.- Nombre del sample (sin espacios)"]
    output_dir = params[0]["3.- Donde guardar la carpeta output"]
    output_dir = f"{output_dir}{os.sep}{execution_title}"
    RUN_script = f"""
cd {output_dir}

"""
    if int(params[1]["1.- Extraer features"]) or int(params[1]["2.- Extraer postfeatures"]):
        write_join_features_python(params, subdir_list)
        RUN_script += "python join_features.py\n"
    if int(params[2]["1.- Clasificar"]):
        write_final_classify_script(params)
        RUN_script += f"qsub submit_classification.sh\n"
    RUN_script += f"echo 'done!'"
    with open(f"{output_dir}{os.sep}FINAL_SCRIPT.sh", "w") as fout:
        fout.write(RUN_script)
    os.system(f"chmod u+x {output_dir}{os.sep}FINAL_SCRIPT.sh")
    print(f"\nNo olvides ejecutar:\n{output_dir}{os.sep}FINAL_SCRIPT.sh")
    print("Cuando terminen todos los procesos de Geryon2\n")

if __name__=="__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="previous":
            with open("/home/ciquezada/VS_Classification/code/frontend/previous_classify_params.txt", 'r') as infile:
                params = json.load(infile)
            params = modify_params_interface(params)
        else:
            params_file = sys.argv[1]
            with open(params_file, 'r') as infile:
                params = json.load(infile)
    else:
        params = get_initial_params()
        params = modify_params_interface(params)
    with open('previous_classify_params.txt', 'w') as outfile:
        json.dump(params, outfile)
    subdir_list = run_on_geryon_extract_features(params)
    write_final_script(params, subdir_list)
    print( '*'*40)
    print( '-'*40)
    exit()
