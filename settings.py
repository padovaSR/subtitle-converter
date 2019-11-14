#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 

from io import StringIO
import os

def filePath(*args): return os.path.join(*args)

WORK_TEXT = StringIO()
    
WORK_SUBS = StringIO()

TEXT = r""

ENT_ENCODING = ""

NEW_ENCODING = StringIO()
    
# shelve : key1=fixer, key2=merger, key3=PATHs, key4=font_data, key5=files_settings

