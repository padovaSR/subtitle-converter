# -*- coding: UTF-8 -*-
# 

import os
import json
import zipfile
from io import StringIO
from collections import defaultdict, OrderedDict

from resources.DictHandle import Dictionaries 

log_file = os.path.join("resources","var","log","subtitle_converter.log")
log_file_history = os.path.join("resources","var","log","file.history.log")
droppedText = os.path.join('resources', 'var', 'r_text0.pkl')

main_settings_file = os.path.join("resources", "var", "settings.db.json")

I_PATH = os.path.join("resources", "icons")

WORK_TEXT = StringIO()

FILE_HISTORY = []

MULTI_FILE = []

PREVIOUS = []


def printEncoding(entered_enc):
    """Normalizes encoding strings into a clean, human-readable format."""
    mapping = {
        "utf-8-sig": "UTF-8 BOM",
        "utf-8": "UTF-8",
        "utf_8": "UTF-8",
        "utf-16": "UTF-16",
    }
    if entered_enc in mapping:
        return mapping[entered_enc]
    if entered_enc.startswith("cp"):
        return entered_enc.replace("cp", "windows-", 1)
    return entered_enc

def lenZip(infile):
    if isinstance(infile, list):
        infile = "".join(infile)
    if not zipfile.is_zipfile(infile):
        return infile
    with zipfile.ZipFile(infile, "r") as f:
        files = [info for info in f.infolist() if not info.is_dir()]
        if len(files) == 1:
            return infile
    return None 
        
def sortList(inlist):
    """"""
    return list(OrderedDict.fromkeys(inlist))
    
def updateRecentFiles(file_list):
    with open(log_file_history, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if os.path.isfile(line):
                file_list.append(line)

def preSuffix():
    ''''''
    with open(
        os.path.join("resources", "var", "presuffix_list.bak"), 'r', encoding='utf-8'
    ) as l:
        return [line.strip("\n") for line in l if line]

with open(log_file_history, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if os.path.exists(line):
            FILE_HISTORY.append(line)

# key1=fixer, key2=merger, key3=PATHs, key4=font_data, key5=files_settings

conf_file = os.path.join("resources", "var", "shortcut_keys.cfg")

shortcutsKeys = defaultdict(str)
shortcutsKeys.update(Dictionaries().dict_fromFile(conf_file, "="))

MAIN_SETTINGS=defaultdict(str)

with open(main_settings_file, "r") as f:
    MAIN_SETTINGS.update(json.loads(f.read()))

defaults = {
    "Notify": True,
    "bom_utf8": False,
    "utf8_txt": False,
    "roman_numerals": False,
}

prefs = MAIN_SETTINGS.setdefault("Preferences", {})

for key, value in defaults.items():
    prefs.setdefault(key, value)    

MAIN_SETTINGS["added_ext"] = preSuffix()