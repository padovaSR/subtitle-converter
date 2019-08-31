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
import os
import sys
import pysrt
from itertools import zip_longest 
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = RotatingFileHandler(os.path.join('resources', 'var', 'FileProcessing.log.log'), mode='a', maxBytes=4000, backupCount=10)
handler.setFormatter(formatter)
logger.addHandler(handler)

def myMerger(file_in, file_out, max_time, max_char, _gap, kode):
    try:
        subs = pysrt.open(file_in, encoding=kode)
    except IOError as e:
        logger.debug("Merger, I/O error({0}): {1}".format(e.errno, e.strerror))
    except Exception as e: #handle other exceptions such as attribute errors
        logger.debug("Merger, unexpected error: {0}".format(sys.exc_info()))    
    if not len(subs) % 2 == 0:
        dsub = pysrt.SubRipItem(subs[-1].index+1, subs[-1].start+6000, subs[-1].end+11000, 'Darkstar test appliance')
        subs.append(dsub)
    else:
        dsub = None
    
    parni = [x for x in subs[1::2]]
    neparni = [x for x in subs[0::2]]
        
    def merge_lines(inPar, inNepar):
        re_pattern = re.compile(r'<[^<]*>')
        new_j = pysrt.SubRipFile()
        for first, second, in zip_longest(inNepar, inPar, fillvalue=subs[-1]):
            gap = second.start.ordinal - first.end.ordinal
            trajanje = second.end.ordinal - first.start.ordinal     # ordinal je vreme u milisekundama
            tekst1 = re.sub(re_pattern, '', first.text) # convert to string
            tekst2 = re.sub(re_pattern, '',  second.text)
            text_len = len(tekst1) + len(tekst2)
            if gap <= _gap and trajanje <= max_time and text_len <= max_char:
                # dodaj spojene linije kao string
                if first.text == second.text and first.start == second.start and first.end == second.end:
                    sub = pysrt.SubRipItem(first.index, first.start, second.end, first.text)
                    new_j.append(sub)
                else:
                    sub = pysrt.SubRipItem(first.index, first.start, second.end, first.text + " " + second.text)
                    new_j.append(sub)
            else:
                # dodaj originalne linije kao string
                sub1 = pysrt.SubRipItem(first.index, first.start, first.end, first.text)
                sub2 = pysrt.SubRipItem(second.index, second.start, second.end, second.text)
                new_j.append(sub1)
                new_j.append(sub2)
                
        if dsub in new_j:
            new_j.remove(dsub)
        new_j.clean_indexes()
        
        parni = [x for x in new_j[1::2]]
        neparni = [x for x in new_j[0::2]]        
        
        return new_j, parni, neparni
    
    out_f, par1, nep1 = merge_lines(parni, neparni)
    out_f, par2, nep2 = merge_lines(par1, nep1)
    out_f, par3, nep3 = merge_lines(par2, nep2)
    out_f, par4, nep4 = merge_lines(par3, nep3)
    
    out_f.save(file_out, encoding=kode)
        

def fixIndexes(infile, kode): 
    subs = pysrt.open(infile, encoding=kode)
    
    # Fix Index and trim white spaces
    for i in range(len(subs)):
        subs[i].index = i + 1
        
    subs.save(infile, encoding=kode)
    
   
def fixGaps(filein, kode):
    
    subs = pysrt.open(filein, encoding=kode)
    
    new_j = pysrt.SubRipFile()
    k = 0
    pfp = 0
    for first, second in zip(subs, subs[1:]):
        
        t1 = first.end.ordinal
        t2 = second.start.ordinal
        
        if t1 > t2:
            pfp += 1
        
        if t1 > t2 or t2 - t1 < 85:
            k += 1
            #first.shift(milliseconds=-25)
            t_fix = pysrt.SubRipTime.from_ordinal((second.start.ordinal) - 70)
            sub = pysrt.SubRipItem(first.index, first.start, t_fix, first.text)
            new_j.append(sub)
        else:
            sub = pysrt.SubRipItem(first.index, first.start, first.end, first.text)
            new_j.append(sub)

    sub = pysrt.SubRipItem(subs[-1].index, subs[-1].start, subs[-1].end, subs[-1].text)
    new_j.append(sub)
    new_j.clean_indexes()
    
    new_f = pysrt.SubRipFile()
    fsub = pysrt.SubRipItem(new_j[0].index, new_j[0].start, new_j[0].end, new_j[0].text)
    new_f.append(fsub)

    for first, second in zip(new_j, new_j[1:]):
        
        t1 = first.end.ordinal
        t2 = second.start.ordinal
        if t2 - t1 < 100:
            t1_fix = pysrt.SubRipTime.from_ordinal((second.start.ordinal) + 15)
            subf = pysrt.SubRipItem(second.index, t1_fix, second.end, second.text)
            new_f.append(subf)
        else:
            subf = pysrt.SubRipItem(second.index, second.start, second.end, second.text)
            new_f.append(subf)        
    
    new_f.clean_indexes()
    new_f.save(filein, encoding=kode)
#    new_j.save(filein, encoding=kode)
    return k, pfp

def fixLast(infile, kode):
    subs = pysrt.open(infile, encoding=kode)
    s1 = (subs[-1].start, subs[-1].end, subs[-1].text)
    s2 = (subs[-2].start, subs[-2].end, subs[-2].text)
    s3 = (subs[-3].start, subs[-3].end, subs[-3].text)
    s4 = (subs[-4].start, subs[-4].end, subs[-4].text)
    
    if s4 == s3 and s3 == s2 and s2 == s1:
        subs.remove(subs[-4])
        subs.remove(subs[-3])
        subs.remove(subs[-2])
        subs.clean_indexes()
        subs.save(infile, encoding=kode)
    elif s1 == s2:
        subs.remove(subs[-1])
        subs.clean_indexes()
        subs.save(infile, encoding=kode)        
