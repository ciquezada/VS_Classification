import os
import json
import sys
import shutil
from pprint import pprint


cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

PROGRAM_TITLE = '-'*40+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '          VS_Classification'+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '-'*40+"\n"
PROGRAM_TITLE += "\n"
PROGRAM_TITLE += '        VS extractor de features'+"\n"
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
    data_dir = params[1]["4.- Carpeta con curvas de luz"]
    output_folder = f"{output_dir}{os.sep}{execution_title}"
    if params[1]["1.- Extraer features"] or params[1]["2.- Extraer postfeatures"]:
        curve_file = params[1]["3.- Archivo con IDs (.var)"]
        curves_output = f"{output_folder}{os.sep}curves.var"
        try:
            os.mkdir(output_folder)
        except OSError as error:
            print(error)
        shutil.copyfile(curve_file, curves_output)
        # EXTRACT_FEATURES
        print()
        os.chdir(f"{vs_classificator_dir}{os.sep}code{os.sep}feets_extractor")
        if params[1]["1.- Extraer features"]:
            features_mode = params[1]["5.- Seleccion de features"]
            features_output = f"{output_folder}{os.sep}features.csv"
            print("Extrayendo features...  ", end='', flush=True)
            os.system(f"python extract_features.py -p \"{num_proc}\" -lc \"{data_dir}\" -i \"{curves_output}\" -o \"{features_output}\" -fs \"{features_mode}\"")
            print("OK")
        if params[1]["2.- Extraer postfeatures"]:
            postfeatures_mode = params[1]["6.- Seleccion de postfeatures"]
            postfeatures_output = f"{output_folder}{os.sep}postfeatures.csv"
            print("Extrayendo postfeatures...  ", end='', flush=True)
            os.system(f"python extract_features.py -p \"{num_proc}\" -lc \"{data_dir}\" -i \"{curves_output}\" -o \"{postfeatures_output}\" -fs \"{postfeatures_mode}\"")
            print("OK")

def params_to_script(params):
    RUN_script = ""
    #init
    execution_title = params[0]["1.- Nombre del sample (Carpeta con outputs)(sin espacios)"]
    output_dir = params[0]["2.- Donde guardar la carpeta output"]
    num_proc = params[0]["3.- Numero de procesos"]
    vs_classificator_dir = os.path.abspath(f"{os.path.abspath(os.path.dirname(__file__))}{os.sep}..{os.sep}..")
    curve_file = params[1]["3.- Archivo con IDs (.var)"]
    data_dir = params[1]["4.- Carpeta con curvas de luz"]

    feets_extractor = f"{vs_classificator_dir}{os.sep}VS_Classification{os.sep}code{os.sep}feets_extractor"
    send_mail = f"{vs_classificator_dir}{os.sep}VS_Classification{os.sep}code{os.sep}monitoring{os.sep}send_email.py"

    RUN_init = f"""
TITLE=\"{execution_title}\"

NUM_PROC=\"{num_proc}\"
DATA_DIR=\"{data_dir}\"
OUTPUT_DIR=\"{output_dir}{os.sep}$TITLE\"
# .var to DataFrame
CURVES=\"{curve_file}\"
CURVES_FILE=\"$OUTPUT_DIR{os.sep}curves.var\"

mkdir \"$OUTPUT_DIR\"
cp \"$CURVES\" \"$CURVES_FILE\"
# EXTRACT_FEATURES
cd \"{feets_extractor}\"
PROGRAM=\"extract_features.py\"
        """
    RUN_script += RUN_init

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
python \"{send_mail}\" \"$TITLE\" \"$LOG\"
python $PROGRAM -p \"$NUM_PROC\" -lc \"$DATA_DIR\" -i \"$CURVES_FILE\" -o \"$FEATURES_OUTPUT\" -fs \"$FEATURES_EXTRACTOR_MODE\"
python \"{send_mail}\" \"$TITLE\" \"$LOG_END\"

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
python \"{send_mail}\" \"$TITLE\" \"$LOG\"
python $PROGRAM -p \"$NUM_PROC\" -lc \"$DATA_DIR\" -i \"$CURVES_FILE\" -o \"$POSTFEATURES_OUTPUT\" -fs \"$POSTFEATURES_EXTRACTOR_MODE\"
python \"{send_mail}\" \"$TITLE\" \"$LOG_END\"

        """
        RUN_script += RUN_extract_features_2
    RUN_end = """
echo \"done!\"
    """
    RUN_script += RUN_end
    return RUN_script

def export_to_script(params):
    RUN_script = params_to_script(params)
    with open(f"{cwd}{os.sep}last_extract_features_script.sh", "w", encoding="utf-8") as fout:
        fout.write(RUN_script)
    os.system(f"chmod u+x \"{cwd}{os.sep}last_extract_features_script.sh\"")

def get_default_params():
    initial_params = {"1.- Nombre del sample (Carpeta con outputs)(sin espacios)": "Nombre_del_sample",
                        "2.- Donde guardar la carpeta output": "/path/to/save/output/folder",
                        "3.- Numero de procesos": 20}

    extract_features_params = {"1.- Extraer features": 1,
                                "2.- Extraer postfeatures": 1,
                                "3.- Archivo con IDs (.var)": "/path/to/var/file",
                                "4.- Carpeta con curvas de luz": "/path/to/lightcurves/folder",
                                "5.- Seleccion de features": "/path/to/features_set.json",
                                "6.- Seleccion de postfeatures": "/path/to/postfeatures_set.json"}

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
    params[1]["3.- Archivo con IDs (.var)"] = os.path.abspath(
                                        params[1]["3.- Archivo con IDs (.var)"])
    params[1]["4.- Carpeta con curvas de luz"] = os.path.abspath(
                                params[1]["4.- Carpeta con curvas de luz"])
    params[1]["5.- Seleccion de features"] = os.path.abspath(
                                        params[1]["5.- Seleccion de features"])
    params[1]["6.- Seleccion de postfeatures"] = os.path.abspath(
                                params[1]["6.- Seleccion de postfeatures"])
    return params

def vs_extract_features_front():
    prev_params_path = f'{cwd}{os.sep}prev_extract_features_params.txt'
    params = get_params(prev_params_path)
    if len(sys.argv)==1:
        clear_screen()
        params = modify_params_interface(params)
    with open(prev_params_path, 'w', encoding="utf-8") as outfile:
        json.dump(params, outfile)
    params = absolute_params(params)
    export_to_script(params)
    run_pipeline(params)
    print("\nDone!")

if __name__=="__main__":
    vs_extract_features_front()
    if len(sys.argv)==1:
        input("(ENTER) to continue.\n")
        print( '*'*40)
        print( '-'*40)
    exit()
