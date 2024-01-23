import os
from sys import platform
from zipfile import ZipFile

import wget

BASE_URL = "https://downloads.tuxfamily.org/godotengine/"
VERSIONS = {"3": "3.5.1", "4": "4.0"}

MOST_RECENT_VERSION = "rc5"


def get_version():
    while True:
        version = input("Which Godot version do you want to download (3 or 4)? ")
        if version in VERSIONS:
            return version
        print("Invalid version. Please enter 3 or 4.")


def download_editor():
    version = get_version()
    VERSION = VERSIONS[version]
    NEW_BASE_URL = f"{BASE_URL}{VERSION}/{version}/"
    NAME = "stable"
    if VERSION == "4.0":
        NEW_BASE_URL = f"{BASE_URL}{VERSION}/{MOST_RECENT_VERSION}/"
        NAME = MOST_RECENT_VERSION
    LINUX_FILENAME = f"Godot_v{VERSION}-{NAME}_linux.x86_64.zip"
    if VERSION == "4.0":
        MAC_FILENAME = f"Godot_v{VERSION}-{NAME}_macos.universal.zip"
    else:
        MAC_FILENAME = f"Godot_v{VERSION}-{NAME}_osx.universal.64.zip"
    WINDOWS_FILENAME = f"Godot_v{VERSION}-{NAME}_win64.exe.zip"

    os.makedirs("editor", exist_ok=True)
    FILENAME = ""
    if platform == "linux" or platform == "linux2":
        FILENAME = LINUX_FILENAME
    elif platform == "darwin":
        FILENAME = MAC_FILENAME
    elif platform == "win32" or platform == "win64":
        FILENAME = WINDOWS_FILENAME
    else:
        raise NotImplementedError

    URL = f"{NEW_BASE_URL}{FILENAME}"

    print(f"downloading editor {FILENAME} for platform: {platform}")
    wget.download(URL, out="")
    print()
    print("unzipping")
    with ZipFile(FILENAME, "r") as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall("editor/")
    print("cleaning up")
    os.remove(FILENAME)
