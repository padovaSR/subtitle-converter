#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import zipfile
import sys
import os

class fileOpened(object):
    def isCompressed(self, infile):
        if zipfile.is_zipfile(infile) == True:
            print("ZIP archive: {}".format(os.path.basename(infile)))
            with zipfile.ZipFile(infile, 'r') as zf:
                print(zf.namelist())
                
