import os
import re

path_to_folder = "/Users/Cyrill/Documents/ETH/Semester FS25/Lab/ethel/data/split_by_subproblem/latex"

files = os.listdir(path_to_folder)
files = [f for f in files if os.path.isfile(os.path.join(path_to_folder, f))]

regex = r"\s2\."

for file_name in files:
    if re.search(regex, file_name):
        print(f"Removing file: {file_name}")
        os.remove(os.path.join(path_to_folder, file_name))
    else:
        continue