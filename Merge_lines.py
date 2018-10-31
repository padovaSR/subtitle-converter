#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import os
import codecs
import pysrt
import textwrap
from itertools import zip_longest 


    
def lineMerger(file_in, file_out, len_line, char_num, _gap, kode):
    
    subs = pysrt.open(file_in, encoding=kode)
    
    parni = [x for x in subs[1::2]]         # Svaki drugi element počevši od drugog
    neparni = [x for x in subs[0::2]]        # Svaki drugi počevši od prvog
        
    re_pattern = re.compile(r'<[^<]*>')                     	# tags
    new_j = pysrt.SubRipFile()
    subs.clean_indexes()
    for first, second, in zip_longest(neparni, parni, fillvalue=subs[-1]):
        gap = second.start.ordinal - first.end.ordinal
        trajanje = second.end.ordinal - first.start.ordinal     # ordinal, vreme u milisekundama
        tekst1 = re.sub(re_pattern, '',  first.text)            # Ne računaj tagove u broj znakova
        tekst2 = re.sub(re_pattern, '',  second.text)
        text_len = len(tekst1) + len(tekst2)
        if gap <= _gap and trajanje <= len_line and text_len <= char_num:
            # dodaj spojene linije kao string
            sub = pysrt.SubRipItem(first.index, first.start, second.end, first.text + ' ' + second.text)
            new_j.append(sub)
        else:
            # dodaj originalne linije kao string
            sub1 = pysrt.SubRipItem(first.index, first.start, first.end, first.text)
            sub2 = pysrt.SubRipItem(second.index, second.start, second.end, second.text)
            new_j.append(sub1)
            new_j.append(sub2)
                
        new_j.clean_indexes()
        new_j.save(file_out, encoding=kode)
    
    
 def fixLast(infile, kode):
    subs = pysrt.open(infile, encoding=kode)
    s1 = (subs[-1].start, subs[-1].end, subs[-1].text)
    s2 = (subs[-2].start, subs[-2].end, subs[-2].text)
    if s1 == s2:
        subs.remove(subs[-1])
        subs.clean_indexes()
        subs.save(infile, encoding=kode)

    
