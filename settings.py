#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 

from io import StringIO
import os

def filePath(*args): return os.path.join(*args)

PREVIOUS = []

WORK_TEXT = StringIO()
    
WORK_SUBS = StringIO()



# shelve : key1=fixer, key2=merger, key3=PATHs, key4=font_data, key5=files_settings

