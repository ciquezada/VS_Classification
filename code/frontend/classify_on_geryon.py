import os
import json
import sys
from pprint import pprint


def get_run_script(params):
    RUN_script = ""

    #init
    execution_title = params[0]["1.- Nombre del sample (sin espacios)"]
    data_dir = params[0]["2.- Carpeta con .dat s"]
    output_dir = params[0]["3.- Donde guardar la carpeta output"]
    num_proc = params[0]["4.- Numero de procesos"]
    vs_classificator_dir = params[0]["5.- Carpeta que contiene VS_Classification"]

    RUN_geryon_header = f"""#!/bin/bash
#
#PBS -V
#PBS -N {execution_title}
#PBS -k eo
#PBS -l nodes=2:ppn=10
#PBS -l walltime=3:00:00
    """
    RUN_init = f"""
TITLE='{execution_title}'

NUM_PROC='{num_proc}'
DATA_DIR='{data_dir}'
OUTPUT_DIR='{output_dir}/$TITLE'

# INIT
cd {vs_classificator_dir}/VS_Classification/code/monitoring

    """

    RUN_script = RUN_geryon_header + RUN_init

    if params[1]["1.- Extraer features"] or params[1]["2.- Extraer postfeatures"]:
        curve_file = params[1]["3.- Archivo con curvas (DataFrame)"]
        RUN_extract_features_0 = f"""
# .var to DataFrame
cd {vs_classificator_dir}/VS_Classification/code/monitoring
CURVES='{curve_file}'
CURVES_FILE='$OUTPUT_DIR/curves.csv'

mkdir '$OUTPUT_DIR'
cp '$CURVES' '$CURVES_FILE'
# EXTRACT_FEATURES
cd ../feets_extractor
PROGRAM='extract_features.py'
        """
        RUN_script += RUN_extract_features_0

    if params[1]["1.- Extraer features"]:
        features_mode = params[1]["4.- Seleccion de features"]
        RUN_extract_features_1 = f"""
FEATURES_OUTPUT='$OUTPUT_DIR/features.csv'
FEATURES_EXTRACTOR_MODE='{features_mode}'

# FEATURES
LOG='INICIADO
PROGRAM: $PROGRAM
Procceses: $NUMPROC
Curves Dir: $DATA_DIR
Curves File: $CURVES_FILE
OUTPUT: $FEATURES_OUTPUT
Extractor Mode: $FEATURES_EXTRACTOR_MODE'
LOG_END='TERMINADO
PROGRAM: $PROGRAM
features en $FEATURES_OUTPUT '
python ../monitoring/send_email.py '$TITLE' '$LOG'
python $PROGRAM $NUM_PROC $DATA_DIR $CURVES_FILE $FEATURES_OUTPUT $FEATURES_EXTRACTOR_MODE
python ../monitoring/send_email.py '$TITLE' '$LOG_END'

        """
        RUN_script += RUN_extract_features_1
    if params[1]["2.- Extraer postfeatures"]:
        postfeatures_mode = params[1]["5.- Seleccion de postfeatures"]
        RUN_extract_features_2 = f"""
# POSTFEATURES
POSTFEATURES_OUTPUT='$OUTPUT_DIR/postfeatures.csv'
POSTFEATURES_EXTRACTOR_MODE='{postfeatures_mode}'

LOG='INICIADO
PROGRAM: $PROGRAM
Procceses: $NUMPROC
Curves Dir: $DATA_DIR
Curves File: $CURVES_FILE
OUTPUT: $POSTFEATURES_OUTPUT
Extractor Mode: $POSTFEATURES_EXTRACTOR_MODE'
LOG_END='TERMINADO
PROGRAM: $PROGRAM
features en $POSTFEATURES_OUTPUT '
python ../monitoring/send_email.py '$TITLE' '$LOG'
python $PROGRAM $NUM_PROC $DATA_DIR $CURVES_FILE $POSTFEATURES_OUTPUT $POSTFEATURES_EXTRACTOR_MODE
python ../monitoring/send_email.py '$TITLE' '$LOG_END'

        """
        RUN_script += RUN_extract_features_2

    if params[2]["1.- Clasificar"]:
        train_file = params[2]["2.- Archivo con training features"]
        classify_mode = params[2]["3.- Modo del Clasificador"]
        RUN_classify = f"""
# CLASSIFY ONLYRR
cd ../rf_classificator
PROGRAM='classify.py'
FEATURES_FILE='$OUTPUT_DIR/features.csv'
PRESET_MODE='{classify_mode}'
TRAIN_FEATURES='{train_file}'
RESULTS_FILE='$OUTPUT_DIR/results.csv'

LOG_MSG='INICIADO
Proccesors: $NUM_PROC
Train Features: $TRAIN_FEATURES
Features File: $FEATURES_FILE
Output: $RESULTS_FILE
Preset Mode: $PRESET_MODE'
LOG_MSG_END='TERMINADO
CV en $OUTPUT_DIR'
python ../monitoring/send_email.py '$PROGRAM $TITLE' '$LOG_MSG'
python $PROGRAM $NUM_PROC $TRAIN_FEATURES $FEATURES_FILE $RESULTS_FILE $PRESET_MODE
python ../monitoring/send_email.py '$PROGRAM $TITLE' '$LOG_MSG_END'

        """
        RUN_script += RUN_classify

    RUN_end = """
echo 'done!'
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
        params = rectify(params)
        if i >= 3:
            break

        election = 'ELECTION'
        election_msg = ["Parametros Iniciales", "Extractor de Features", "Clasificador"]
        print(f"Paso {i+1}/{3}: {election_msg[i]}")
        pprint(params[i])
        while election not in ['y', 'n', 'p', 'q', '']:
            election = input("Modificar?: (y) yes, (n or ENTER) no, (p) previous, (q) quit: \n")

        if election == 'y':
            os.system("clear")
            print(f"Paso {i+1}/{3}: {election_msg[i]}")
            params[i] = modify_params(params[i])
        if election == '' or election == "n":
            i = i + 1
        if election == 'p':
            if i == 0:
                # print( 'No hay pasos previos a este!!')
                continue
            i = i - 1
            continue
        if election == 'q':
            print( '-'*40)
            print( '*'*40)
            print( 'Abortando VS_Classification')
            print( '*'*40)
            print( '-'*40)
            exit()
            break
    return params

if __name__=="__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="previuos":
            with open("previous_classify_params.txt", 'r') as infile:
                params = json.load(infile)
        else:
            params_file = sys.argv[1]
            with open(params_file, 'r') as infile:
                params = json.load(infile)
    else:
        params = get_initial_params()
        params = modify_params_interface(params)
    with open('previous_classify_params.txt', 'w') as outfile:
        json.dump(params, outfile)
    RUN_script = get_run_script(params)
    with open("temp_classify_on_geryon.sh", "w") as fout:
        fout.write(RUN_script)
    os.system("qsub temp_classify_on_geryon.sh")
