#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def dict_fromFile(text_in, delim):
    with open(text_in, 'r', encoding='utf-8') as dict_file:
        new_dict = {}
        for line in dict_file:
            x = line.strip().split(delim)
            if not line:
                continue
            if not x[0]:
                continue
            else:
                key = x[0]
            value = x[-1]
            new_dict[key] = value
            
        return new_dict

# Dictionary-0
dictionary_0 = dict_fromFile(text_in='dictionaries\\Dictionary-0.txt', delim='=>')

# Dictionary-1
dictionary_1 = dict_fromFile(text_in='dictionaries\\Dictionary-1.txt', delim='=>')

# Dictionary-2
dictionary_2 = dict_fromFile(text_in='dictionaries\\Dictionary-1.txt', delim='=>')
