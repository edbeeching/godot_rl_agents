# we download examples from github and we save them in the examples folder

import os
import shutil
from sys import platform
import wget
from zipfile import ZipFile

BANCHES = {"4" : "main",
           "3" : "godot3.5"}

BASE_URL="https://github.com/edbeeching/godot_rl_agents_examples"

def download_examples():
    #select branch
    print("Select Godot version:")
    for key in BANCHES.keys():
        print(f"{key} : {BANCHES[key]}")
    
    branch = input("Enter your choice: ")
    BRANCH = BANCHES[branch]  
    os.makedirs("examples", exist_ok=True)
    URL=f"{BASE_URL}/archive/refs/heads/{BRANCH}.zip"
    print(f"downloading examples from {URL}")
    wget.download(URL, out="")
    print()
    print(f"unzipping")
    with ZipFile("main.zip", 'r') as zipObj:
    # Extract all the contents of zip file in different directory
        zipObj.extractall('examples/')
    print(f"cleaning up")
    os.remove("main.zip")
    print(f"moving files")
    for file in os.listdir("examples/godot_rl_agents_examples-main"):
        shutil.move(f"examples/godot_rl_agents_examples-main/{file}", "examples")
    os.rmdir("examples/godot_rl_agents_examples-main")
    