#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  Copyright (C) 2019  padovaSR
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import os
import pysrt
import webbrowser
import pickle
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(filename=os.path.join("resources", "var", "File_Errors.log"), mode="a", encoding="utf-8")
handler.setFormatter(formatter)
logger.addHandler(handler)

def unifiedL(origList, errorList):
    newList = []
    for i in errorList:
        if i in origList:
            continue
        else:
            newList.append(i)
    return newList
        
def w_position(_pattern, intext):
    intext = intext.replace('\r', '')
    l1 = []; l2 = []
    for match in re.finditer(_pattern, intext):
        # group=match.group()
        begin=match.start()
        end=match.end()
        l1.append(begin)
        l2.append(end)
        
    f_list = [(x,y) for x, y in zip(l1, l2)]
    return f_list

def showMeError(infile, in_text, outfile, kode):
    
    with open(os.path.join('resources', 'var', 'fixer_cb3.data'), 'rb') as f:
        cb3_s = pickle.load(f)
    
    subs = pysrt.from_string(in_text)
    
    if len(subs) > 0:
        
        st = "LINIJE SA GREŠKAMA:\n"
        if kode == 'windows-1251':
            st = "ЛИНИЈЕ СА ГРЕШКАМА:\n"
            kode = "utf-8"
        FP = re.compile(r"\?")
        count = 0
        sl = pysrt.SubRipFile()
        sl.append(st)
        for i in subs:
            t = i.text
            FE = re.findall(FP, t)
            if FE:
                t = t.replace('¬', '?')
                sub = pysrt.SubRipItem(i.index, i.start, i.end, t)
                sl.append(sub)
                count += 1
        if count > 0:
            try:
                sl.save(outfile, encoding=kode)
            except IOError as e:
                logger.debug("ErrorFile, I/O error({0}): {1}".format(e.errno, e.strerror))
            except Exception as e: #handle other exceptions such as attribute errors
                logger.debug("ErrorFile, unexpected error:", sys.exc_info()[0:2])        
            
            if os.path.isfile(outfile): logger.debug(f"ErrorFile: {outfile}")
            if cb3_s == True: webbrowser.open(outfile)
    else:
        logger.debug(f'showMeError: No subtitles found in {os.path.basename(infile)}')

# showMeError(test, outf, kode="utf-8")