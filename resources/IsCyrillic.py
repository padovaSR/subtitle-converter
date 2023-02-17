# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        IsCyrillic module
# Purpose:     Check if text is Cyrillic alphabet
#
# Author:      darkstar
#-------------------------------------------------------------------------------

import re
from codecs import BOM_UTF8 

import logging.config
logger = logging.getLogger(__name__)


def checkCyrillicAlphabet(input_text):
    
    def decode_text() -> str:
        if input_text[:4].startswith(BOM_UTF8):
            return input_text.decode("utf-8")
        else:
            for enc in ["cp1251", "utf-8"]:
                try:
                    input_text.decode(enc)
                except:
                    logger.debug(f"Error decoding with {enc}")
                else:
                    logger.debug(f"Decoding with: {enc}")
                    break
            return input_text.decode(enc)
        
    if isinstance(input_text, bytes):
        input_text = decode_text()
            
    def checkChars() -> int:
        def percentage(part, whole):
            try:
                return int(100*part/whole)
            except ZeroDivisionError:
                logger.debug(f"File is empty")
                return 0

        st_pattern = re.compile(r"[\u0400-\u04FF]", re.U)
        rx = "".join((st_pattern.findall(input_text)))
        procenat = percentage(len(rx), len(list(filter(str.isalpha, input_text))))
        logger.debug(f"Procenat ćirilice: {procenat} %")
        return procenat

    def maybeCyrillic() -> bool:
        """"""
        chpattern = re.compile("[бвгдђжзилмнпртћуфхцчшљњџ]")
        if len(set(chpattern.findall(input_text))) > 1:
            return True
        else:
            return False

    if maybeCyrillic() is True:
        return checkChars()
    else:
        return False

