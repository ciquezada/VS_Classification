import os


VS_DIR = os.path.abspath(f"{os.path.dirname(__file__)}")

if __name__=="__main__":
    os.system(f"pip install \"{VS_DIR}{os.sep}distribution{os.sep}VS_Classification-0.1.0-py3.7.egg\"")
    os.system(f"python \"{VS_DIR}{os.sep}code{os.sep}frontend{os.sep}create_shortcuts.py\"")
