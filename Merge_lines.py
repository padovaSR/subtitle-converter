#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import os
import codecs
import string
import srt
import pysrt
import textwrap


    
def lineMerger(file_in, file_out, len_line, char_num, _gap, kode):
    
    subs = pysrt.open(file_in, encoding=kode)
    
    parni = []; neparni = []                #;  treci = []
    for i in range(1, len(subs), 2)         # Svaki drugi element počevši od drugog
        parni.append(subs[i])
    for i in range(0, len(subs), 2):        # Svaki drugi počevši od prvog
        neparni.append(subs[i])
    
    new_j = ''''''
    for first, second, in zip(neparni, parni):
        gap = second.start.ordinal - first.end.ordinal
        trajanje = second.end.ordinal - first.start.ordinal     # ordinal, vreme u milisekundama
        tekst1 = re.sub('(\<[^<]*\>)', '',  first.text)         # to string
        tekst2 = re.sub('(\<[^<]*\>)', '',  second.text)
        text_len = len(tekst1) + len(tekst2)
        if gap <= _gap and trajanje <= len_line and text_len <= char_num:
            # dodaj spojene linije kao string
            first_l = round(len(first.text + second.text) / 2) + 4
            t_strw = textwrap.fill(first.text + ' ' + second.text, width=first_l)
            new_j += '{0}\n{1} --> {2}\n{3}\n\n'.format(first.index, first.start, first.end, t_strw)
        else:
            # dodaj originalne linije kao string
            new_j += '{0}\n{1} --> {2}\n{3}\n\n'.format(first.index, first.start, first.end, first.text)
            new_j += '{0}\n{1} --> {2}\n{3}\n\n'.format(second.index, second.start, second.end, second.text)
    if not len(subs) % 2 == 0:
        new_j += '{0}\n{1} --> {2}\n{3}\n\n{4}'.format(subs[-1].index, subs[-1].start, subs[-1].end, subs[-1].text, '')    
    with open(file_out, 'w', encoding=kode) as fw:
        new_j = new_j.replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')
        fw.write(new_j)
    
def fixIndexes(infile, kode): 
    subs_new = pysrt.open(infile, encoding=kode)
    for i in range(len(subs_new)):
        subs_new[i].index = i + 1
    subs_new.save(infile, encoding=kode)
    
    
    
