#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

import os
import re
from settings import filePath
from showError import showMeError

import wx

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(
    filename=filePath("resources", "var", "log", "FileProcessing.log"),
    mode="a",
    encoding="utf-8",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

def w_position(_pattern, intext):
    intext = intext.replace('\r', '')
    l1 = []
    l2 = []
    for match in re.finditer(_pattern, intext):
        # group=match.group()
        begin = match.start()
        end = match.end()
        l1.append(begin)
        l2.append(end)

    f_list = [(x, y) for x, y in zip(l1, l2)]
    return f_list

def checkFile(path, newfile, text_s, multi):
    file1_name = path
    try:
        n_sign = text_s.count(r"\?")
        if n_sign > 0:
            poruka = re.sub(
                r"(?: ){2,14}",
                " ",
                u'!! Greška u tekstu\
            !!\n{0}\nNeispravnih znakova\ konvertovanih kao znak `?` ukupno:\
            [{1} ]',
            ).format(os.path.basename(file1_name), n_sign)

            logger.debug(poruka)
            if multi == True:
                file1_name = newfile
            error_text = f"Greška:\n\n{os.path.basename(file1_name)}\nBilo je neispravnih znakova u\
            tekstu\nkonvertovanih kao znak `?`\nUkupno: [{n_sign}]\nProverite tekst."
            if error_text:
                error_text = re.sub("(?: ){2,4}", " ", error_text)
            return error_text
    except UnboundLocalError as e:
        logger.debug(f"File_Check, error({e})")
    except Exception as e:
        logger.debug(f"File_Check, unexpected error: {e}")
        
def checkErrors(text_in):
    
    fpaterns = '|'.join(
        [
            'ï»¿Å',
            'Ä',
            'Å½',
            'Ä',
            'Ä',
            'Å¡',
            'Ä',
            'Å¾',
            'Ä',
            'Ä',
            "ď»ż",
            "Ĺ˝",
            'Ĺ ',
            'ĹĄ',
            'Ĺž',
            'Ä',
            'Å ',
            'Ä‡',
            'Ä¿',
            'Ä²',
            'Ä³',
            'Å¿',
            'Ã¢â',
            "�",
            "Д†",
            "Д‡",
            "Ť",
            "Lˇ",
            "ï»¿",
            "ð",
        ]
    )
    
    MOJIBAKE_SYMBOL_RE = re.compile(
        '[ÂÃĂ][\x80-\x9f€ƒ‚„†‡ˆ‰‹Œ“•˜œŸ¡¢£¤¥¦§¨ª«¬¯°±²³µ¶·¸¹º¼½¾¿ˇ˘˝]|'
        r'[ÂÃĂ][›»‘”©™]\w|'
        '[¬√][ÄÅÇÉÑÖÜáàâäãåçéèêëíìîïñúùûü†¢£§¶ß®©™≠ÆØ¥ªæø≤≥]|'
        r'\w√[±∂]\w|'
        '[ðđ][Ÿ\x9f]|'
        'â€|ï»|'
        'вЂ[љћ¦°№™ќ“”]'+
        fpaterns)                
    
    l1 = []; l2 = []
    try:
        for match in re.finditer(MOJIBAKE_SYMBOL_RE, text_in):
            begin = match.start()
            end = match.end()
            l1.append(begin)
            l2.append(end)
        f_list = [(x,y) for x, y in zip(l1, l2)]
        return f_list
    except Exception as e:
        logger.debug("CheckErrors ({0}):".format(e))
        return []
    
def checkChars(text):
    def percentage(part, whole):
        try:
            return int(100 * part / whole)
        except ZeroDivisionError:
            logger.debug('FileCheck Error, file is empty')
            return 0

    def chars(*args):
        return [
            chr(i) for a in args for i in range(ord(a[0]), ord(a[1]) + 1)
        ]

    slova = "".join(chars("\u0400\u04ff"))

    st_pattern = re.compile(r"[A-Za-z\u0400-\u04FF]", re.U)

    try:
        rx = "".join(re.findall(st_pattern, text))
    except Exception as e:
        logger.debug(f"CheckChars error: ({e})")

    im = []
    for i in rx:
        FP = re.compile(i)
        try:
            if re.search(FP, slova):
                im.append(i)
        except ValueError as e:
            logger.debug(f"Value error: {e},{i}")

    statistic = {}
    for x in im:
        if x in rx:
            num = rx.count(x)
            statistic[x] = num

    all_values = sum(statistic.values())
    procenat = percentage(all_values, len(rx))

    return all_values, procenat, list(set(im))

def displayError(text, tctrl, rdir, path, new_enc, multi):
    """"""
    nlist = w_position(r"\?", text)
    epath = os.path.basename(path)
    
    if type(rdir) == list:
        rdir = [x for rdir[0] in rdir for x in rdir[0]]
        outf = os.path.join(rdir[0], os.path.splitext(epath)[0]+"_error.log")
    else:
        outf = os.path.join(rdir, os.path.splitext(epath)[0]+'_error.log')
    
    showMeError(path, text, outf, new_enc)
    text = text.replace('¬', '?')
    
    if multi == False:
        tctrl.SetValue(text)
        for i in nlist:
            if not len(nlist) > 300:
                tctrl.SetStyle(i[0], i[1], wx.TextAttr("YELLOW","GREEN"))
                tctrl.SetInsertionPoint(i[1])
                
    return text
    