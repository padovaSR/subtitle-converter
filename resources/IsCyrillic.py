# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------------------------------------
# Name:        IsCyrillic module
# Purpose:     To check if a given input text contains Cyrillic characters and 
#              return the percentage of Cyrillic characters in the text along with the encoding if detected
#
# Author:      darkstar
#----------------------------------------------------------------------------------------------------------
import re

import logging.config
logger = logging.getLogger(__name__)


def checkCyrillicAlphabet(input_text):
    """"""
    encoding = None
    def decode_text() -> str:
        for enc in ["cp1251", "utf-8", "utf-16", "cp1250"]:
            try:
                return input_text.decode(enc), enc
            except:
                logger.debug(f"Error with {enc}")
            
    if isinstance(input_text, bytes):
        input_text,encoding = decode_text()
            
    def checkChars() -> int:
        st_pattern = re.compile(r"[\u0400-\u04FF]", re.U)
        cyrillic = len(st_pattern.findall(input_text))
        letters = sum(ch.isalpha() for ch in input_text)
    
        if letters == 0:
            return 0
    
        percent = cyrillic * 100 / letters
        logger.debug(f"Procenat ćirilice: {percent:.2f}%")
        return round(percent)

    def maybeCyrillic() -> bool:
        """"""
        chpattern = re.compile("[бвгдђжзилмнпртћуфхцчшљњџ]")
        if len(set(chpattern.findall(input_text))) > 1:
            return True
        else:
            return False

    if maybeCyrillic() is True:
        return checkChars(), encoding
    else:
        return False, encoding

