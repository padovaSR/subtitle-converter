#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 

from io import StringIO
import os
import re

def filePath(*args): return os.path.join(*args)

def printEncoding(entered_enc):
    ''''''
    if entered_enc == "utf-8-sig":
        entered_enc = "UTF-8 BOM"
    elif entered_enc == "utf-8":
        entered_enc = "UTF-8"
    return entered_enc

chreg = re.compile("¬")

PREVIOUS = []

WORK_TEXT = StringIO()
    
WORK_SUBS = StringIO()



# shelve : key1=fixer, key2=merger, key3=PATHs, key4=font_data, key5=files_settings

