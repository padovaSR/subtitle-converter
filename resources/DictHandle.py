# -*- coding: UTF-8 -*-

import sys
import os
from os.path import join

sys.path.append("../dictionaries")


class Dictionaries:
    """A class for storing and accessing dictionaries
    used in a text processing application.

    Attributes:
        dictionary_files (dict): A mapping of dictionary names to file paths.
        dictionaries (dict): A mapping of dictionary names to dictionaries.
    """

    fDict = join('dictionaries', 'Dictionary-1.txt')
    fDict1 = join('dictionaries', 'Dictionary-2.txt')
    fDict0 = join('dictionaries', 'Dictionary-0.txt')
    fDict_special = join('dictionaries', 'Special-Replace.txt')
    prelatCyr = join("resources", "preLatCyr.map.cfg")
    
    def __init__(self):
        """Initialize the dictionaries attribute
        by loading dictionaries from the dictionary files."""

        self.dictionary_1 = self.dict_fromFile(self.fDict, '=>')
        self.dictionary_0 = self.dict_fromFile(self.fDict0, '=>')
        self.dictionary_2 = self.dict_fromFile(self.fDict1, '=>')
        self.searchReplc = self.dict_fromFile(self.fDict_special, '=>')

        self.dict1_n = self.new_dict(self.fDict, n=1)
        self.dict2_n = self.new_dict(self.fDict1, n=1)
        self.dict0_n = self.new_dict(self.fDict0, n=1)

        self.dict2_n2 = self.new_dict2(self.fDict1)
        self.dict1_n2 = self.new_dict2(self.fDict)
        self.dict0_n2 = self.new_dict2(self.fDict0)

        self.pre_cyr = self.dict_fromFile(self.prelatCyr, '=')
        
    def create_dict_other(self, infile):
        with open(infile, 'r', encoding='utf-8') as rplS_fyle:
            n_dict = {}
            for line in rplS_fyle:
                x = line.strip().split('=')
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                if not x[0]:
                    continue
                a = x[0]
                b = x[-1]
                n_dict[a] = b
            return n_dict

    def dict_fromFile(self, text_in, delimiter):
        if not os.path.exists(text_in):
            with open(text_in, 'w', encoding='utf-8', newline="\r\n") as text_file:
                text_file.write('Alpha=>Alfa\n')
        with open(text_in, 'r', encoding='utf-8') as dict_file:
            new_dict = {}
            for line in dict_file:
                x = line.strip().split(delimiter)
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                if not x[0]:
                    continue
                key = x[0].strip()
                value = x[-1].strip()
                new_dict[key] = value
            return new_dict

    def new_dict(self, indict, n=None):
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
                if len(x[0].split(' ')) >= 2 and n != None:
                    key = x[0].replace(' ', '\n', n)
                else:
                    key = x[0]
                value = x[-1]
                newDict[key] = value
            return newDict

    def new_dict2(self, indict):
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
                    key = w[0] + ' ' + w[1] + '\n' + w[-1]
                    value = x[-1]
                    newDict[key] = value
            return newDict

#########################################################################

lat_cir_mapa = {
    'A': 'А', 'B': 'Б', 'C': 'Ц', 'Č': 'Ч', 'Ć': 'Ћ', 'D': 'Д', 'E': 'Е',
    'F': 'Ф', 'G': 'Г', 'H': 'Х', 'I': 'И', 'J': 'Ј', 'K': 'К', 'L': 'Л',
    'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П', 'R': 'Р', 'S': 'С', 'Š': 'Ш',
    'T': 'Т', 'U': 'У', 'V': 'В', 'Z': 'З', 'Ž': 'Ж', 'Đ': 'Ђ','a': 'а',
    'b': 'б', 'c': 'ц', 'č': 'ч', 'ć': 'ћ', 'd': 'д', 'e': 'е', 'f': 'ф',
    'g': 'г', 'h': 'х', 'i': 'и', 'j': 'ј', 'k': 'к', 'l': 'л', 'm': 'м',
    'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 'š': 'ш', 't': 'т',
    'u': 'у', 'v': 'в', 'z': 'з', 'ž': 'ж', 'đ': 'ђ',
}

#########################################################################
