#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Dictionary-1
with open('dictionaries\\Dictionary-1.txt', 'r', encoding='utf-8') as dict_file:
    dict_1 = {}
    for line in dict_file:
        x = line.strip().split('=>')
        if not line:
            continue
        key = x[0]
        value = x[-1]
        dict_1[key] = value
        
dictionary_1 = dict((k, v) for k, v in dict_1.items() if k)
