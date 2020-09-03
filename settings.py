#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 

from io import StringIO
import os
import re
import pickle
from more_itertools import unique_everseen
import zipfile
from collections import defaultdict 

chreg = re.compile("¬")

log_file = os.path.join("resources","var","log","subtitle_converter.log")
log_file_history = os.path.join("resources","var","log","file.history.log")
droppedText = os.path.join('resources', 'var', 'r_text0.pkl')

FILE_HISTORY = []

PREVIOUS = []

WORK_TEXT = StringIO()
    
WORK_SUBS = []

BYTES_TEXT = []

def filePath(*args): return os.path.join(*args)

def printEncoding(entered_enc):
    ''''''
    if entered_enc == "utf-8-sig":
        entered_enc = "UTF-8 BOM"
    elif entered_enc == "utf-8":
        entered_enc = "UTF-8"
    return entered_enc

def lenZip(infile):
    if zipfile.is_zipfile(infile):
        f = zipfile.ZipFile(infile)
        if not len(f.namelist()) >= 2:
            return infile
    else: return infile
        
def sortList(inlist):
    """"""
    return list(unique_everseen(inlist))

with open(log_file_history, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        FILE_HISTORY.append(line)

def preSuffix():
    ''''''
    with open(
        os.path.join("resources", "var", "presuffix_list.bak"), 'r', encoding='utf-8'
    ) as l:
        added = [line.strip("\n") for line in l if line]

    with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
        ex = pickle.load(f)
        value2_s = ex['cyr_utf8_txt']
        value5_s = ex['lat_utf8_srt']

    with open(os.path.join("resources", "var", "m_extensions.pkl"), "rb") as f:
        value_m = pickle.load(f)  #  Merger suffix

    with open(os.path.join('resources', 'var', 'tcf.pkl'), 'rb') as tf:
        oformat = pickle.load(tf)  # TXT suffix

    return [added, value2_s, value5_s, value_m, oformat, ex]

name_data = preSuffix()

# shelve : key1=fixer, key2=merger, key3=PATHs, key4=font_data, key5=files_settings

FILE_SETTINGS=defaultdict(str)

with open(os.path.join("resources", "var", "dialog_settings.db.dat"), "rb") as f:
    data = pickle.load(f)
    
FILE_SETTINGS.update(data)
