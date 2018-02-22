#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import os
import codecs
import string
import srt
import pysrt
import textwrap


def fixIndexes(infile, kode): 
    subs_new = pysrt.open(infile, encoding=kode)
    for i in range(len(subs_new)):
        subs_new[i].index = i + 1
    subs_new.save(infile, encoding=kode)
    
    
    
    
