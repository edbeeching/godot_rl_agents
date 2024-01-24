# we download examples from github and we save them in the examples folder

import os
import shutil
from zipfile import ZipFile

import wget

BRANCHES = {"4": "main", "3": "godot3.5"}

BASE_URL = "https://github.com/edbeeching/godot_rl_agents_examples"


def download_examples():
    # select branch
    print("Select Godot version:")
    for key in BRANCHES.keys():
        print(f"{key} : {BRANCHES[key]}")

    branch = input("Enter your choice: ")
    BRANCH = BRANCHES[branch]
    os.makedirs("examples", exist_ok=True)
    URL = f"{BASE_URL}/archive/refs/heads/{BRANCH}.zip"
    print(f"downloading examples from {URL}")
    wget.download(URL, out="")
    print()
    print("unzipping")
    with ZipFile(f"{BRANCH}.zip", "r") as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall("examples/")
    print("cleaning up")
    os.remove(f"{BRANCH}.zip")
    print("moving files")
    for file in os.listdir(f"examples/godot_rl_agents_examples-{BRANCH}"):
        shutil.move(f"examples/godot_rl_agents_examples-{BRANCH}/{file}", "examples")
    os.rmdir(f"examples/godot_rl_agents_examples-{BRANCH}")
