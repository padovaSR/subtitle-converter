#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 

from io import StringIO
import os
import re
import pickle

def filePath(*args): return os.path.join(*args)

def printEncoding(entered_enc):
    ''''''
    if entered_enc == "utf-8-sig":
        entered_enc = "UTF-8 BOM"
    elif entered_enc == "utf-8":
        entered_enc = "UTF-8"
    return entered_enc

chreg = re.compile("¬")

log_file_history = os.path.join("resources","var","log","file.history.log")

FILE_HISTORY = []

PREVIOUS = []

WORK_TEXT = StringIO()
    
WORK_SUBS = StringIO()

with open(os.path.join('resources', 'var', 'obsE.pkl'), 'rb') as f:
    kodek = pickle.load(f).strip()

with open(log_file_history, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        FILE_HISTORY.append(line)

# shelve : key1=fixer, key2=merger, key3=PATHs, key4=font_data, key5=files_settings

