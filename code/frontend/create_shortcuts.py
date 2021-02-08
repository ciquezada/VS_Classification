import os


TRAINING_FEATURES_PATH = "../../data/vvv_shortp_train+onlyrr+gp_drop/features.csv" # PARA VS_lite

VS_DIR = os.path.abspath(f"{os.path.dirname(__file__)}")
TRAINING_FEATURES_PATH = os.path.abspath(f"{VS_DIR}{os.sep}{TRAINING_FEATURES_PATH}")

def export_to_script(script, name):
    with open(f"{VS_DIR}{os.sep}..{os.sep}..{os.sep}{name}", "w", encoding="utf-8") as fout:
        fout.write(script)

def get_vs_lite_script():
    VS_lite_script = """import os
import sys
import json


NUMERO_DE_PROCESOS = 10
CARPETA_OUTPUT = "VS_output"
"""

    VS_lite_script += f"""
TRAINING_FEATURES = \"{TRAINING_FEATURES_PATH}\"
""".replace("\\", "\\\\")

    VS_lite_script += """


#################################################################
#################################################################
PROGRAM_TITLE = '-'*40+'\\n'
PROGRAM_TITLE += '*'*40+'\\n'
PROGRAM_TITLE += '          VS_Classification'+'\\n'
PROGRAM_TITLE += '*'*40+'\\n'
PROGRAM_TITLE += '-'*40+'\\n'

"""

    VS_lite_script += f"vs_frontend_dir = \"{VS_DIR}\"".replace("\\", "\\\\")

    VS_lite_script += """

pipeline = [f"python \\"{vs_frontend_dir}{os.sep}var_to_dataframe.py\\"",
            f"python \\"{vs_frontend_dir}{os.sep}VS_extract_features.py\\"",
            f"python \\"{vs_frontend_dir}{os.sep}VS_classify.py\\"",
            f"python \\"{vs_frontend_dir}{os.sep}build_custom_output.py\\"",
            ]

def get_params(output_folder, var_path, dat_path, num_proc, training_features):
    init_params = {
                    "1.- Nombre del sample (Carpeta con outputs)(sin espacios)": f"{output_folder}",
                    "2.- Donde guardar la carpeta output": os.getcwd(),
                    "3.- Numero de procesos": num_proc
                    }
    var2df_params = {"(INPUT)  Archivo .var": var_path,
                     "(OUTPUT) DataFrame de curvas": f"{output_folder}{os.sep}precurves.csv"}
    extract_features_params = [init_params,
                                {
                                "1.- Extraer features": 1,
                                "2.- Extraer postfeatures": 1,
                                "3.- Archivo con curvas (DataFrame)": f"{output_folder}{os.sep}precurves.csv",
                                "4.- Carpeta con .dat s": dat_path,
                                "5.- Seleccion de features": "rrlyr",
                                "6.- Seleccion de postfeatures": "rrlyr_postfeatures"
                                }]
    classify_params = [init_params,
                        {
                        "1.- Clasificar": 1,
                        "2.- Archivo con features": f"{output_folder}{os.sep}features.csv",
                        "3.- Archivo con training features": training_features,
                        "4.- Modo del Clasificador": "rrlyr_lite"
                           }]
    custom_output_paramns =  {
                                "(INPUT)  Archivo .var": var_path,
                                "(INPUT)  Archivo con features": f"{output_folder}{os.sep}features.csv",
                                "(INPUT)  Archivo con postfeatures": f"{output_folder}{os.sep}postfeatures.csv",
                                "(INPUT)  Archivo con results": f"{output_folder}{os.sep}results.csv",
                                "(OUTPUT) DataFrame output": f"{output_folder}{os.sep}final_output.csv"
                                }
    return [var2df_params, extract_features_params,
                classify_params, custom_output_paramns]

def os_mkdir(output_folder):
    # making needed directories
    gen = (x for x in range(1,99999))
    aux_output_folder = output_folder
    while True:
        try:
            os.mkdir(output_folder)
            break
        except OSError as error:
            output_folder = f"{aux_output_folder}{next(gen)}"
            print(error)
            print(f"Cambiando carpeta output a: {output_folder}")
    return output_folder

def clean_mess(output_folder):
    files_to_clean = [
            f"{output_folder}{os.sep}precurves.csv",
            f"{output_folder}{os.sep}curves.csv",
            f"{output_folder}{os.sep}postfeatures.csv",
            f"{output_folder}{os.sep}results.csv",
            f"{output_folder}{os.sep}param.json"
            ]
    for fil in files_to_clean:
        try:
            os.remove(fil)
        except:
            print("Error while deleting file : ", fil)

if __name__=="__main__":
    print(PROGRAM_TITLE)
    if len(sys.argv)<3 and 0:
        print("HELP:")
        print('\\tinput 1: /path/to/.var/file')
        print('\\tinput 2: /path/to/.dat/folder')
        print()
        print( '*'*40)
        print( '-'*40)
        exit()
    output_folder = CARPETA_OUTPUT
    num_proc = NUMERO_DE_PROCESOS
    var_path = sys.argv[1]
    dat_path = sys.argv[2]
    training_features = TRAINING_FEATURES
    output_folder = os_mkdir(output_folder)
    pipeline_params = get_params(output_folder, var_path, dat_path, num_proc, training_features)
    for script, param in zip(pipeline, pipeline_params):
        with open(f"{output_folder}{os.sep}param.json", 'w', encoding="utf-8") as outfile:
            json.dump(param, outfile)
        os.system(f"{script} {output_folder}{os.sep}param.json")
    clean_mess(output_folder)
    input("(ENTER) to continue.\\n")
    print( '*'*40)
    print( '-'*40)
    exit()
"""
    return VS_lite_script

def get_vs_advance_script():
    VS_advance_script = """import os


"""
    VS_advance_script += f"vs_frontend_dir = \"{VS_DIR}\"".replace("\\", "\\\\")
    VS_advance_script += """
if __name__=="__main__":
    os.system(f"python \\"{vs_frontend_dir}{os.sep}VS_advance_mode.py\\"")
"""
    return VS_advance_script

if __name__=="__main__":
    print('-'*40+"\n")
    print('*'*40+"\n")
    print('          VS_Classification')
    print("\n")
    print("Creando VS_lite.py...  ", end='', flush=True)
    VS_lite_script = get_vs_lite_script()
    export_to_script(VS_lite_script, "VS_lite.py")
    print("Done!")
    print("\tinput 1: /path/to/.var/file")
    print("\tinput 2: /path/to/.dat/folder")
    print("\n")
    print("Creando VS_advance.py...  ", end='', flush=True)
    VS_advance_script = get_vs_advance_script()
    export_to_script(VS_advance_script, "VS_advance.py")
    print("Done!")
    print("\tNo necesita input")
    print("\n")
    print('*'*40+"\n")
    print('-'*40+"\n")
    input("(ENTER) to exit.\n")
