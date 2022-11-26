#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 

from io import StringIO
import os
from os.path import join 
import re
import zipfile
from collections import defaultdict, OrderedDict 
import json

chreg = re.compile("¬")

log_file = os.path.join("resources","var","log","subtitle_converter.log")
log_file_history = os.path.join("resources","var","log","file.history.log")
droppedText = os.path.join('resources', 'var', 'r_text0.pkl')

settings_file = os.path.join("resources", "var", "dialog_settings.db.json")

FILE_HISTORY = []

PREVIOUS = []

WORK_TEXT = StringIO()
    
WORK_SUBS = []

BYTES_TEXT = []

def filePath(*args): return os.path.join(*args)

def printEncoding(entered_enc):
    ''''''
    if entered_enc == "utf-8-sig":
        return "UTF-8 BOM"
    elif entered_enc == "utf-8":
        return "UTF-8"
    else: return entered_enc

def lenZip(infile):
    if zipfile.is_zipfile(infile):
        f = zipfile.ZipFile(infile)
        if not len(f.namelist()) >= 2:
            return infile
    else: return infile
        
def sortList(inlist):
    """"""
    return list(OrderedDict.fromkeys(inlist))
    
with open(log_file_history, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        FILE_HISTORY.append(line)

def preSuffix():
    ''''''
    with open(join("resources", "var", "presuffix_list.bak"), 'r', encoding='utf-8') as l:
        return [line.strip("\n") for line in l if line]

FILE_SETTINGS=defaultdict(str)

with open(settings_file, "r") as f:
    FILE_SETTINGS.update(json.loads(f.read()))

FILE_SETTINGS["Added_ext"] = preSuffix()