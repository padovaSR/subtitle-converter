# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        IsCyrillic module
# Purpose:     Check if text is Cyrillic alphabet
#
# Author:      darkstar
#-------------------------------------------------------------------------------
import sys
import re
import wx
try:
    from charset_normalizer import from_bytes
except ImportError:
    app = wx.App(False)
    wx.MessageBox(
        f"ImportError\n\nTo continue install ‚charset_normalizer’:\n"
        f"’pip insatll charset-normalizer‘",
        "SubtitleConverter",
        wx.OK | wx.ICON_ERROR,
    )
    app.Destroy()
    sys.exit(1)

import logging.config
logger = logging.getLogger(__name__)


def checkCyrillicAlphabet(input_text):
    
    def decode_text() -> str:
        data = from_bytes(input_text)
        first = data.best().encoding        
        for enc in [first, "cp1251", "utf-8"]:
            try:
                return input_text.decode(enc)
            except:
                logger.debug(f"Error with {enc}")
            
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

