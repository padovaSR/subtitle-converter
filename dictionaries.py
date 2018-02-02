#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def dict_fromFile(text_in, delim):
    with open(text_in, 'r', encoding='utf-8') as dict_file:
        new_dict = {}
        for line in dict_file:
            x = line.strip().split(delim)
            if not line:
                continue
            key = x[0]
            value = x[-1]
            new_dict[key] = value
            
    new_dict = dict((k, v) for k, v in new_dict.items() if k)
    
    return new_dict

# Dictionary-1
dictionary_1 = dict_fromFile(text_in='dictionaries\\Dictionary-1.txt', delim='=>')

