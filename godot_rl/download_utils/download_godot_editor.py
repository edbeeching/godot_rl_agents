import os
import shutil
from sys import platform
import wget
from zipfile import ZipFile

VERSION="beta4"
BASE_URL=f"https://downloads.tuxfamily.org/godotengine/4.0/{VERSION}/"
LINUX_FILENAME=f"Godot_v4.0-{VERSION}_linux.x86_64.zip"
MAC_FILENAME=f"Godot_v4.0-{VERSION}_macos.universal.zip"
WINDOWS_FILENAME=f"Godot_v4.0-{VERSION}_win64.exe.zip"



def download_editor():
    os.makedirs("editor", exist_ok=True)
    FILENAME=""
    if platform == "linux" or platform == "linux2":
       FILENAME = LINUX_FILENAME
    elif platform == "darwin":
        FILENAME = MAC_FILENAME
    elif platform == "win64":
        FILENAME = WINDOWS_FILENAME
    else:
        raise NotImplementedError

    URL=f"{BASE_URL}{FILENAME}"

    print(f"downloading editor {FILENAME} for platform: {platform}")
    wget.download(URL, out="")
    print()
    print(f"unzipping")
    with ZipFile(FILENAME, 'r') as zipObj:
    # Extract all the contents of zip file in different directory
        zipObj.extractall('editor/')
    print(f"cleaning up")
    os.remove(FILENAME)