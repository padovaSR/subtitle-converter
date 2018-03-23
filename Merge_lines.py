#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import os
import codecs
import pysrt
import textwrap


    
def lineMerger(file_in, file_out, len_line, char_num, _gap, kode):
    
    subs = pysrt.open(file_in, encoding=kode)
    
    parni = []; neparni = []
    for i in range(1, len(subs), 2)         # Svaki drugi element počevši od drugog
        parni.append(subs[i])
    for i in range(0, len(subs), 2):        # Svaki drugi počevši od prvog
        neparni.append(subs[i])
    
    re_pattern = re.compile(r'<[^<]*>')                     	# tags
    new_j = ''''''
    subs.clean_indexes()
    for first, second, in zip(neparni, parni):
        gap = second.start.ordinal - first.end.ordinal
        trajanje = second.end.ordinal - first.start.ordinal     # ordinal, vreme u milisekundama
        tekst1 = re.sub(re_pattern, '',  first.text)            # Ne računaj tagove u broj znakova
        tekst2 = re.sub(re_pattern, '',  second.text)
        text_len = len(tekst1) + len(tekst2)
        if gap <= _gap and trajanje <= len_line and text_len <= char_num:
            # dodaj spojene linije kao string
            first_l = round(len(first.text + second.text) / 2) + 4
            t_strw = textwrap.fill(first.text + ' ' + second.text, width=first_l)
            new_j += '{0}\n{1} --> {2}\n{3}\n\n'.format(first.index, first.start, second.end, t_strw)
        else:
            # dodaj originalne linije kao string
            new_j += '{0}\n{1} --> {2}\n{3}\n\n'.format(first.index, first.start, first.end, first.text)
            new_j += '{0}\n{1} --> {2}\n{3}\n\n'.format(second.index, second.start, second.end, second.text)
    if not len(subs) % 2 == 0:
        new_j += '{0}\n{1} --> {2}\n{3}\n\n{4}'.format(subs[-1].index, subs[-1].start, subs[-1].end, subs[-1].text, '')    
    with open(file_out, 'w', encoding=kode) as fw:
        new_j = new_j.replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')
        fw.write(new_j)
    
 def fixLast(infile, kode):
    subs = pysrt.open(infile, encoding=kode)
    s1 = (subs[-1].start, subs[-1].end, subs[-1].text)
    s2 = (subs[-2].start, subs[-2].end, subs[-2].text)
    if s1 == s2:
        del subs[-1]
    subs.clean_indexes()
    subs.save(infile, encoding=kode)

    
