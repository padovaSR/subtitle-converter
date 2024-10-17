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
    ''''''
    if entered_enc == "utf-8-sig":
        return "UTF-8 BOM"
    elif entered_enc == "utf-8":
        return "UTF-8"
    elif entered_enc == "utf-16":
        return "UTF-16"
    else: return entered_enc

def lenZip(infile):
    if isinstance(infile, list):
        infile = "".join(infile)
    if zipfile.is_zipfile(infile):
        f = zipfile.ZipFile(infile)
        if not len(f.namelist()) >= 2:
            return infile
    else: return infile
        
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
        FILE_HISTORY.append(line)

# key1=fixer, key2=merger, key3=PATHs, key4=font_data, key5=files_settings

conf_file = os.path.join("resources", "var", "shortcut_keys.cfg")

shortcutsKeys = defaultdict(str)
shortcutsKeys.update(Dictionaries().dict_fromFile(conf_file, "="))

MAIN_SETTINGS=defaultdict(str)

with open(main_settings_file, "r") as f:
    MAIN_SETTINGS.update(json.loads(f.read()))
    
MAIN_SETTINGS["added_ext"] = preSuffix()