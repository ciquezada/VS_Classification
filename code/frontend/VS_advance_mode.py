import os
import sys


cwd = os.path.abspath(f"{os.path.dirname(__file__)}")

PROGRAM_TITLE = '-'*40+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '          VS_Classification'+"\n"
PROGRAM_TITLE += '*'*40+"\n"
PROGRAM_TITLE += '-'*40+"\n"

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

def get_executable_options():
    op = [f"python \"{cwd}{os.sep}VS_classify.py\"",
            f"python \"{cwd}{os.sep}VS_classify_geryon2.py\"",
            f"python \"{cwd}{os.sep}VS_extract_features.py\"",
            f"python \"{cwd}{os.sep}VS_extract_features_geryon2.py\"",
            f"python \"{cwd}{os.sep}VS_ks_metallicites.py\"",
            f"python \"{cwd}{os.sep}VS_ks_metallicites_geryon2.py\"",
            f"python \"{cwd}{os.sep}var_to_dataframe.py\"",
            f"python \"{cwd}{os.sep}build_custom_output.py\"",
            ]
    names = ["1.- VS Classify",
                "2.- VS Classify (Geryon2 mode)",
                "3.- VS extractor de features",
                "4.- VS extractor de features (Geryon2 mode)",
                "5.- VS extractor de metalicidades",
                "6.- VS extractor de metalicidades (Geryon2 mode)",
                "7.- Convertir '.var' a '.csv' DataFrame (Curve File)",
                "8.- Construir custom output"
                ]
    return op, names

if __name__=="__main__":
    election = "election"
    ejecutable, names = get_executable_options()
    while True:
        clear_screen()
        print("\n".join(names))
        print()
        while election not in ['1', '2', '3', '4', '5', '6', '7', '8', '', 'q']:
            election = input("(q or ENTER) to quit: \n")
        if election == 'q' or election == '':
            print_exit()
            exit()
            break
        else:
            clear_screen()
            os.system(ejecutable[int(election)-1])
            election = "election"
