import os
import json
import sys
from pprint import pprint


cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

PROGRAM_TITLE = '-'*40+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '          VS_Classification'+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '-'*40+"\n"
PROGRAM_TITLE += "\n"
PROGRAM_TITLE += '            VS Classify'+"\n"
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

def run_pipeline(params):
    #init
    execution_title = params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"]
    output_dir = params[0]["2.- Donde guardar la carpeta output"]
    num_proc = params[0]["3.- Numero de procesos"]
    vs_classificator_dir = os.path.abspath(f"{os.path.abspath(os.path.dirname(__file__))}{os.sep}..{os.sep}..")

    output_folder = f"{output_dir}{os.sep}{execution_title}"
    if params[1]["1.- Clasificar"]:
        features_file = params[1]["2.- Archivo con features"]
        train_file = params[1]["3.- Archivo con training features"]
        classify_mode = params[1]["4.- Modo del Clasificador"]
        results_output = f"{output_folder}{os.sep}results.csv"
        try:
            os.mkdir(output_folder)
        except OSError as error:
            print(error)
        # EXTRACT_FEATURES
        print()
        os.chdir(f"{vs_classificator_dir}{os.sep}code{os.sep}rf_classificator")
        print("Clasificando...", end='', flush=True)
        os.system(f"python classify.py \"{num_proc}\" \"{train_file}\" \"{features_file}\" \"{results_output}\" \"{classify_mode}\"")
        print("OK")


def params_to_script(params):
    RUN_script = ""
    #init
    execution_title = params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"]
    output_dir = params[0]["2.- Donde guardar la carpeta output"]
    num_proc = params[0]["3.- Numero de procesos"]
    vs_classificator_dir = os.path.abspath(f"{os.path.abspath(os.path.dirname(__file__))}{os.sep}..{os.sep}..")

    rf_classificator = f"{vs_classificator_dir}{os.sep}code{os.sep}rf_classificator"
    send_mail = f"{vs_classificator_dir}{os.sep}code{os.sep}monitoring{os.sep}send_email.py"

    RUN_init = f"""
TITLE=\"{execution_title}\"

NUM_PROC=\"{num_proc}\"
OUTPUT_DIR=\"{output_dir}{os.sep}$TITLE\"
# .var to DataFrame

mkdir \"$OUTPUT_DIR\"
        """
    RUN_script += RUN_init

    if params[1]["1.- Clasificar"]:
        features_file = params[1]["2.- Archivo con features"]
        train_file = params[1]["3.- Archivo con training features"]
        classify_mode = params[1]["4.- Modo del Clasificador"]
        RUN_classify = f"""
# CLASSIFY ONLYRR
cd \"{rf_classificator}\"
PROGRAM=\"classify.py\"
FEATURES_FILE=\"{features_file}\"
PRESET_MODE=\"{classify_mode}\"
TRAIN_FEATURES=\"{train_file}\"
RESULTS_FILE=\"$OUTPUT_DIR{os.sep}results.csv\"

LOG_MSG=\"INICIADO
Proccesors: $NUM_PROC
Train Features: $TRAIN_FEATURES
Features File: $FEATURES_FILE
Output: $RESULTS_FILE
Preset Mode: $PRESET_MODE\"
LOG_MSG_END=\"TERMINADO
CV en $OUTPUT_DIR\"
python \"{send_mail}\" \"$TITLE\" \"$LOG_MSG\"
python \"$PROGRAM\" \"$NUM_PROC\" \"$TRAIN_FEATURES\" \"$FEATURES_FILE\" \"$RESULTS_FILE\" \"$PRESET_MODE\"
python \"{send_mail}\" \"$TITLE\" \"$LOG_MSG_END\"

        """
        RUN_script += RUN_classify
    RUN_end = """
echo \"done!\"
    """
    RUN_script += RUN_end
    return RUN_script

def export_to_script(params):
    RUN_script = params_to_script(params)
    with open(f"{cwd}{os.sep}last_classify_script.sh", "w", encoding="utf-8") as fout:
        fout.write(RUN_script)
    os.system(f"chmod u+x \"{cwd}{os.sep}last_classify_script.sh\"")

def get_default_params():
    initial_params = {"1.- Nombre del sample (Carpeta con outputs)(sin espacios)": "Nombre_del_sample",
                        "2.- Donde guardar la carpeta output": "/path/to/save/output/folder",
                        "3.- Numero de procesos": 20}

    classify_params = {"1.- Clasificar": 1,
                        "2.- Archivo con features": "/path/to/features/file",
                        "3.- Archivo con training features": "/path/to/train/file",
                        "4.- Modo del Clasificador": "rrlyr"}

    params = [initial_params, classify_params]
    return params

def validate_params(params):
    elec_in = {"y":1, "si":1, "1":1, "0":0, "yes":1, "no":0, "n":0, 1:1, 0:0}
    params[0]["3.- Numero de procesos"] = int(params[0]["3.- Numero de procesos"])
    params[1]["1.- Clasificar"] = elec_in[params[1]["1.- Clasificar"]]
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
    params[1]["2.- Archivo con features"] = os.path.abspath(
                                        params[1]["2.- Archivo con features"])
    params[1]["3.- Archivo con training features"] = os.path.abspath(
                                params[1]["3.- Archivo con training features"])
    return params

def vs_classify_front():
    clear_screen()
    prev_params_path = f'{cwd}{os.sep}prev_classify_params.txt'
    params = get_params(prev_params_path)
    if len(sys.argv)==1:
        params = modify_params_interface(params)
    with open(prev_params_path, 'w', encoding="utf-8") as outfile:
        json.dump(params, outfile)
    params = absolute_params(params)
    export_to_script(params)
    run_pipeline(params)
    print("\nDone!")
    input("(ENTER) to continue.\n")

if __name__=="__main__":
    vs_classify_front()
    print( '*'*40)
    print( '-'*40)
    exit()
