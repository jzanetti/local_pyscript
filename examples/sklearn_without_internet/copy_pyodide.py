import os

PKGS = [
    "dateutil", 
    "pytz",
    "six",
    "numpy",
    "pandas",
    "networkx",
    "matplotlib",
    "packaging",
    "pillow",
    "pyparsing",
    "micropip",
    "cycler",
    "kiwisolver",
    "pydot",
    "joblib",
    "scipy",
    "scikit_learn",
    "threadpoolctl"
]

# PYODIDE_DIR = "C:\\Users\\ZhangSi\\Downloads\\pyodide-0.27.2\\pyodide"
PYODIDE_DIR = "/Users/sijinzhang/Downloads/pyodide"
OUTPUT_DIR = "examples/casual_learn_without_internet/etc/pyodide"
INCLUDE_EXT = ["zip", "js", "json", "wasm", "ts", "map", "mjs"]
EXCLUDE_EXT = ["tar"]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for proc_filename in os.listdir(PYODIDE_DIR):

    found_file = False
    for proc_ext in INCLUDE_EXT:
        if proc_filename.endswith(proc_ext):
            found_file = True
            break

    if not found_file:
        for proc_substring in PKGS:
            if proc_substring in proc_filename:
                found_file = True
                break

    if found_file:
        for proc_ext in EXCLUDE_EXT:
            if proc_filename.endswith(proc_ext):
                found_file = False
                break

    if found_file:
        os.system(f"cp -rf {os.path.join(PYODIDE_DIR, proc_filename)} {os.path.join(OUTPUT_DIR, proc_filename)}")
    