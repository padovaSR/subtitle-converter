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

import os
import codecs


fDict = os.path.join('dictionaries', 'Dictionary-1.txt')
fDict1 = os.path.join('dictionaries', 'Dictionary-2.txt')
fDict0 = os.path.join('dictionaries', 'Dictionary-0.txt')
fDict_special = os.path.join('dictionaries', 'Special-Replace.txt')
    

def remBom(infile):
    _BOM = codecs.BOM_UTF8
    buffer_size = 4096
    bom_length = len(_BOM)
    with open(infile, "r+b") as fp:
        chunk = fp.read(buffer_size)
        if chunk.startswith(_BOM):
            i = 0
            chunk = chunk[bom_length:]
            while chunk:
                fp.seek(i)
                fp.write(chunk)
                i += len(chunk)
                fp.seek(bom_length, os.SEEK_CUR)
                chunk = fp.read(buffer_size)
            fp.seek(-bom_length, os.SEEK_CUR)
            fp.truncate()    

def dict_fromFile(text_in, delim):
    if not os.path.exists(text_in):
        with open(text_in, 'w', encoding='utf-8', newline="\r\n") as text_file:
            t = 'Alpha=>Alfa\n'
            text_file.write(t)
    with open(text_in, 'r', encoding='utf-8') as dict_file:
        
        new_dict = {}
        
        for line in dict_file:
            x = line.strip().split(delim)
            if not line:
                continue
            if line.startswith('#'):
                continue
            if not x[0]:
                continue
            else:
                key = x[0]
            value = x[-1]
            new_dict[key] = value
        return new_dict

def new_dict(indict, n):
    with open(indict, 'r', encoding='utf-8') as dict_file:
        
        newDict = {}
        
        for line in dict_file:
            x = line.strip().split('=>')
            if not line:
                continue
            if line.startswith('#'):
                continue
            if not x[0]:
                continue            
            if len(x[0].split(' ')) >= 2:
                key = x[0].replace(' ', '\n', n)
                value = x[-1]
                newDict[key] = value
        return newDict

def new_dict2(indict):
    with open(indict, 'r', encoding='utf-8') as dict_file:
        
        newDict = {}
        
        for line in dict_file:
            x = line.strip().split('=>')
            if not line:
                continue
            if line.startswith('#'):
                continue
            if not x[0]:
                continue            
            if len(x[0].split(' ')) == 3:
                w = x[0].split()
                key = w[0]+' '+w[1]+'\n'+w[-1]
                value = x[-1]
                newDict[key] = value
        return newDict
    
remBom(fDict)
remBom(fDict1)
remBom(fDict0)
remBom(fDict_special)

dictionary_1 = dict_fromFile(fDict, delim='=>')  # ex sviPojmovi
dictionary_0 = dict_fromFile(fDict0, delim='=>')
dictionary_2 = dict_fromFile(fDict1, delim='=>')
searchReplc = dict_fromFile(fDict_special, delim='=>')

dict1_n = new_dict(fDict, n=1)
dict2_n = new_dict(fDict1, n=1)
dict0_n = new_dict(fDict0, n=1)

dict2_n2 = new_dict2(fDict1)
dict1_n2 = new_dict2(fDict)
dict0_n2 = new_dict2(fDict0)

rplS = os.path.join('resources', 'LATIN_chars.cfg')
remBom(rplS)

with open(rplS, 'r', encoding='utf-8') as rplS_fyle:
    drep = {}
    for line in rplS_fyle:
        x = line.strip().split('=')
        if not line:
            continue
        if line.startswith('#'):
            continue
        if not x[0]:
            continue
        else:
            a = x[0]
        b = x[-1]
        drep[a] = b

rplSmap = dict((k, v) for k, v in drep.items() if k)

#-------------------------------------------------------------------------------------------------------------#

lat_cir_mapa = {'đ': 'ђ', 'Đ': 'Ђ', 'e': 'е', 'r': 'р', 't': 'т', 'z': 'з', 'u': 'у', 'i': 'и',
             'o': 'о', 'p': 'п', 'a': 'а', 's': 'с', 'd': 'д', 'f': 'ф', 'g': 'г', 'h': 'х',
             'j': 'ј', 'k': 'к', 'l': 'л', 'c': 'ц', 'v': 'в', 'b': 'б', 'n': 'н', 'm': 'м',
             'š': 'ш', 'ž': 'ж', 'č': 'ч', 'ć': 'ћ', 'E': 'Е', 'R': 'Р', 'T': 'Т', 'Z': 'З',
             'U': 'У', 'I': 'И', 'O': 'О', 'P': 'П', 'A': 'А', 'S': 'С', 'D': 'Д', 'F': 'Ф',
             'G': 'Г', 'H': 'Х', 'J': 'Ј', 'K': 'К', 'L': 'Л', 'C': 'Ц', 'V': 'В', 'B': 'Б',
             'N': 'Н', 'M': 'М', 'Š': 'Ш', 'Ž': 'Ж', 'Č': 'Ч', 'Ć': 'Ћ'}

#-------------------------------------------------------------------------------------------------------------#

prelatCyr = os.path.join('resources', 'preLatCyr.map.cfg')
remBom(prelatCyr)
LatFile = os.path.join('resources', 'cp1250.replace.cfg')
remBom(LatFile)

with open(LatFile, 'r', encoding='utf-8') as inLat:
    ln = {}
    for line in inLat:
        x = line.strip().split('=')
        if not line:
            continue
        if line.startswith('#'):
            continue        
        a = x[0]
        b = x[-1]
        ln[a] = b

pLatin_rpl = dict((k, v) for k, v in ln.items() if k)

pre_cyr = dict_fromFile(prelatCyr, delim='=')

conf_file = os.path.join("resources", "shortcut_keys.cfg")
shortcutsKey = dict_fromFile(conf_file, delim="=")
