#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  Copyright (C) 2021  padovaSR
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
# 
import os
from os.path import basename as baseName
import pickle
import shutil
import webbrowser
from collections import namedtuple, defaultdict
from pydispatch import dispatcher
from settings import (
    WORK_TEXT,
    PREVIOUS,
    FILE_HISTORY,
    BYTES_TEXT,
    filePath,
    lenZip,
    droppedText,
    chreg,
    FILE_SETTINGS,
    name_data, 
)
import codecs
import zipfile
from choice_dialog import MultiChoice

from codecs import BOM_UTF8

import re
import unicodedata
import srt
from textwrap import TextWrapper

import wx

import logging.config

logger = logging.getLogger(__name__)

codelist = [
    'utf-8',
    'utf-8-sig',
    'utf-16',
    'utf-32',
    'utf-16-be',
    'utf-16-le',
    'utf-32-be',
    'utf-32-le',
]

class ChangeEncoding:
    """Change text encoding"""

    def __init__(self, text):
        """Constructor"""
        self.text = text
        
    def toUTF_8(self, new_enc="utf-8"):
        """change encoding to utf-8"""
        try:
            text = self.text.encode(encoding=new_enc, errors="surrogatepass")
            return text.decode(encoding=new_enc, errors="surrogatepass")
        except Exception as e:
            logger.debug(f"ConvertText: {e}")
    
    def toANSI(self, new_enc="cp1250"):
        """change to ANSI"""
        try:
            text = self.text.encode(encoding=new_enc, errors="replace")
            return text.decode(encoding=new_enc, errors="replace")
        except Exception as e:
            logger.debug(f"ConvertText: {e}")
    
class ConvertText:
    """Change encoding and Latin alphabet to Cyrillic"""

    def __init__(self, text):
        """Constructor"""
        self.text = text

    def toCyrANSI(self, new_enc="cp1251"):
        """change to cp1251"""
        try:
            text = self.text.encode(encoding=new_enc, errors="replace")
            return text.decode(encoding=new_enc, errors="replace")
        except Exception as e:
            logger.debug(f"ConvertText: {e}")
            
    def changeLetters(self, preProc=False, reversed_action=False):
        '''Function used for transliteration'''
        ## pre_cyr je rečnik iz preLatCyr.map.cfg
        text = fixI(self.text)
    
        ## Preprocessing ###########################################################
        try:
            if reversed_action is False:
                robjCyr = re.compile('(%s)' % '|'.join(map(re.escape, pre_cyr.keys())))
                text = robjCyr.sub(lambda m: pre_cyr[m.group(0)], text)
            elif reversed_action is True:
                pre_lat = dict(map(reversed, pre_cyr.items()))
                robjLat = re.compile('(%s)' % '|'.join(map(re.escape, pre_lat.keys())))
                text = robjLat.sub(lambda m: pre_lat[m.group(0)], text)
        except Exception as e:
            logger.debug(f"Preprocessing, unexpected error: {e}")
        ############################################################################
        MAPA = lat_cir_mapa
        if reversed_action is True:
            cyr_lat_mapa = dict(map(reversed, lat_cir_mapa.items()))
            MAPA = cyr_lat_mapa
    
        cir_lat = {
            'ЛЈ': 'Љ',
            'НЈ': 'Њ',
            'ДЖ': 'Џ',
        }
    
        intab = 'АБВГДЕЗИЈКЛМНОПРСТУФХЦЋЧЂШЖабвгдезијклмнопрстуфхцћчђшж'
        outab = 'ABVGDEZIJKLMNOPRSTUFHCĆČĐŠŽabvgdezijklmnoprstufhcćčđšž'
        transltab = str.maketrans(intab, outab)
    
        rd = {"Љ": "Lj", "Њ": "Nj", "Џ": "Dž", "љ": "lj", "њ": "nj", "џ": "dž"}
    
        ## preslovljavanje ########################################################
        if text:
            try:
                text_ch = ""
    
                for c in text:
                    if c in MAPA:
                        text_ch += MAPA[c]
                    else:
                        text_ch += c
    
                ## Fix string #####################################################
                if preProc is True:
                    text_ch, msg = rplStr(text_ch)
                else:
                    msg = "0"
    
                ## Fine tune ######################################################
                robjCyr = re.compile('(%s)' % '|'.join(map(re.escape, cir_lat.keys())))
                text_ch = robjCyr.sub(lambda m: cir_lat[m.group(0)], text_ch)
    
                ## reverse translate ##############################################
                f_reg = re.compile("<[^<]*?>|www\.\w+\.\w+", (re.I | re.M))
    
                cf = f_reg.findall(text_ch)
    
                lj = [x.translate(transltab) for x in cf]
    
                for i in lj:
                    for k, v in rd.items():
                        a = lj.index(i)
                        i = i.replace(k, v)
                        lj[a] = i
    
                dok = dict(zip(cf, lj))
    
                for key, value in dok.items():
                    text_ch = text_ch.replace(key, value)  # Replace list items
    
                text_ch = remTag(text_in=text_ch)
    
                return text_ch, msg
            except Exception as e:
                logger.debug(f"Preslovljavanje, unexpected error: {e}")
        else:
            logger.debug(f"Preslovljavanje, no text found!")
            
def bufferText(intext, buffer):

    buffer.truncate(0)
    buffer.write(intext)
    buffer.seek(0)

def normalizeText(code_in, path, data):
    '''text normalization'''
    # error = "strict"
    # error="surogateescape"
    error = "replace"
    if code_in in codelist:
        error = 'surrogatepass'
    if path:
        with open(path, "rb") as f: content = f.read()
        if code_in == "windows-1251":
            c = 0
            for i in "аеио".encode("cp1251"):
                if content.find(i) < 0:
                    c += 1
                    code_in = "windows-1250"
            if c > 0:
                ErrorDlg = wx.MessageDialog(
                    None,
                    f"UnicodeDecodeError\n\n"
                    f"Detektovane greške u tekstu!\n"
                    f"Pretražite tekst [�,ð...]\n"
                    f"ili je encoding možda pogrešan",
                    "SubtitleConverter",
                    style=wx.OK | wx.ICON_ERROR,
                )
                if ErrorDlg.ShowModal() == wx.ID_OK:
                    ErrorDlg.Destroy()
        try:
            with open(path, 'r', encoding=code_in, errors=error) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            logger.debug(f"normalizeText: {e}")
            text = f"{os.path.basename(path)}\n\n{e}"
    else:
        try:
            text = data.decode(encoding=code_in, errors=error)
        except UnicodeDecodeError as e:
            logger.debug(f"normalizeText: {e}")
            text = f"{e}"
    text_normalized = unicodedata.normalize('NFKC', text)
    return text_normalized
    
def rplStr(in_text):

    ## Rečnik je 'rplSmap' - LATIN_chars.
    ## Lista ključeva(keys) je 'rplsList'.

    p = in_text
    n_pattern = re.compile("|".join(list(rplSmap.keys())))
    nf = n_pattern.findall(p)

    # starts = [x.start() for x in re.finditer(n_pattern,in_text)]
    # ends = [x.end() for x in re.finditer(n_pattern, in_text)]
    # f_list = [(x,y) for x, y in zip(starts, ends)]

    logger.debug('\nSpecijalnih znakova ukupno: [{0}]'.format(len(nf)))
    message = ""
    if len(nf) > 0:
        logger.debug(f'SpecChars: ( {" ".join(set(nf))} )\n')
        message = f'{", ".join(set(nf))}.'

    for key, value in rplSmap.items():
        p = p.replace(key, value)

    # Dodatni replace u binarnom formatu:
    # xc2\xad = SOFT HYPHEN, \xef\xbb\xbf = bom utf-8, \xe2\x80\x91 = NON-BREAKING HYPHEN

    try:
        p = p.encode(encoding="utf-8", errors="surrogatepass")
        mp = (
            p.replace(b'\xc2\xad', b'')
            .replace(b'\xd0\x94\xc4', b'D')
            .replace(b"\xc4\x8f\xc2\xbb\xc5\xbc", b"")
            .replace(b'\xe2\x80\x91', b'')
            .replace(b'\xc3\x83\xc2\xba', b'u')
            .replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94')
            .replace(b'\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94')
            .replace(b'\xef\xbb\xbf', b'')
            .replace(b'\xc5\xb8\xc5\x92', b'')
            .replace(b"\xc2\x81", b"")
            .replace(b"\xc2\x90", b"")
            .replace(b"\xef\xbf\xbd", b"")            
        )
        # .replace(b'\x9e', b'\xc5\xbe') \xe2\x96\xa0 = ■
        if mp:
            text = mp.decode(encoding="utf-8", errors="surrogatepass")
            return text, message
    except Exception as e:
        logger.debug(f"■ rplStr encode error: {e}")    

def fixI(in_text):

    try:
        p = in_text.encode(encoding="utf-8", errors="surrogatepass")
        # Slova č,ć,đ,Č,Ć,Đ se nalaze i u rplStr() fukciji takođe.
        # ligature: ǈ=b'\xc7\x88' ǋ=b'\xc7\x8b' ǉ=b'\xc7\x89' ǌ=b'\xc7\x8c' \xe2\x96\xa0 = ■
        # \xc2\xa0 = NO-BREAK SPACE, \xe2\x80\x94 = EM DASH
        fp = (
            p.replace(b'/ ', b'/')
            .replace(b' >', b'>')
            .replace(b'- <', b'-<')
            .replace(b'</i> \n<i>', b'\n')
            .replace(b'< ', b'<')
            .replace(b'<<i>', b'<i>')
            .replace(b'\xc3\x83\xc2\xba', b'\x75')
            .replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94')
            .replace(b' \n', b'\n')
            .replace(b'\xe2\x82\xac\xe2\x80\x9d', b'V')
            .replace(b'\xef\xbb\xbf', b'')
            .replace(b'\xc5\xb8\xc5\x92', b'')
            .replace(b'\xd0\x94\xa0', b'\x44')
            .replace(b'\xc2\xa0', b' ')
            .replace(b"\xc2\x81", b"")
            .replace(b"\xc4\x8f\xc2\xbb\xc5\xbc", b"")
            .replace(b"\xc2\x90", b"")
            .replace(b"\xef\xbf\xbd", b"")            
        )
        # .replace(b'\xc7\x88', b'\x4c\x6a') \
        # .replace(b'\xc7\x8b', b'\x4e\x6a').replace(b'\xc7\x89', b'\x6c\x6a').replace(b'\xc7\x8c', b'\x6e\x6a')
        if fp:
            text = fp.decode(encoding="utf-8", errors="surrogatepass")
        return text
    except Exception as e:
        logger.debug(f"fixI unexpected error, {e}")

def preLatin(text_in):
    """"""
    ## pLatin_rpl je rečnik iz cp1250.replace.cfg
    ## PreLatin ################################################################
    robjLatin = re.compile('(%s)' % '|'.join(map(re.escape, pLatin_rpl.keys())))
    try:
        text = robjLatin.sub(lambda m: pLatin_rpl[m.group(0)], text_in)
    except Exception as e:
        logger.debug(f"PreLatin, unexpected error: {e}")

    return text

def remTag(text_in):
    '''Remove unnecessary tags'''

    taglist = ["<i>", "</i>", "<b>", "</b>", "<u>", "</u>", "</font>"]

    n_reg = re.compile(r"<[^<]*?>", re.I)

    nf = n_reg.findall(text_in)

    new_f = [x for x in nf if x not in taglist and not x.startswith("<font ")]

    new_r = [re.sub(r"[<>]", "", x) for x in new_f]

    fdok = dict(zip(new_f, new_r))

    for k, v in fdok.items():
        text_in = text_in.replace(k, v)

    return text_in

def zameniImena(text_in):

    if len(list(srt.parse(text_in))) == 0:
        logger.debug(f"Transkrib, No subtitles found.")
    else:
        text_in = srt.compose(srt.parse(text_in, ignore_errors=True))

    robj1 = re.compile(r'\b(' + '|'.join(map(re.escape, dictionary_1.keys())) + r')\b')
    robj2 = re.compile(r'\b(' + '|'.join(map(re.escape, dictionary_2.keys())) + r')\b')
    robj3 = re.compile(r'\b(' + '|'.join(map(re.escape, dictionary_0.keys())) + r')\b')

    robjN1 = re.compile(r'\b(' + '|'.join(map(re.escape, dict1_n.keys())) + r')\b')
    robjN2 = re.compile(r'\b(' + '|'.join(map(re.escape, dict2_n.keys())) + r')\b')
    robjN0 = re.compile(r'\b(' + '|'.join(map(re.escape, dict0_n.keys())) + r')\b')

    robjL0 = re.compile(r'\b(' + '|'.join(map(re.escape, dict0_n2.keys())) + r')\b')
    robjL1 = re.compile(r'\b(' + '|'.join(map(re.escape, dict1_n2.keys())) + r')\b')
    robjL2 = re.compile(r'\b(' + '|'.join(map(re.escape, dict2_n2.keys())) + r')\b')
    try:
        t_out1 = robj1.subn(lambda x: dictionary_1[x.group(0)], text_in)
        t_out2 = robj2.subn(lambda x: dictionary_2[x.group(0)], t_out1[0])
        t_out3 = robj3.subn(lambda x: dictionary_0[x.group(0)], t_out2[0])

        t_out4 = robjN1.subn(lambda x: dict1_n[x.group(0)], t_out3[0])
        t_out5 = robjN2.subn(lambda x: dict2_n[x.group(0)], t_out4[0])
        t_out6 = robjN0.subn(lambda x: dict0_n[x.group(0)], t_out5[0])
    except Exception as e:
        logger.debug(F"Transkripcija, error: {e}")

    def doRepl(inobj, indict, text):
        try:
            out = inobj.subn(lambda x: indict[x.group(0)], text)
            return out[1]
        except IOError as e:
            logger.debug(f"Replace keys, I/O error: {e}")
        except Exception as e:
            logger.debug(f"Replace keys, unexpected error: {e}")

    if len(dict1_n2) != 0:
        doRepl(robjL1, dict1_n2, t_out6[0])
    if len(dict2_n2) != 0:
        doRepl(robjL2, dict2_n2, t_out6[0])
    if len(dict0_n2) != 0:
        doRepl(robjL0, dict0_n2, t_out6[0])

    much = t_out1[1] + t_out2[1] + t_out3[1] + t_out4[1] + t_out5[1] + t_out6[1]
    logger.debug('Transkripcija u toku.\n--------------------------------------')
    logger.debug(f'Zamenjeno ukupno {much} imena i pojmova')

    return much, t_out6[0]

def doReplace(text_in):

    robj_r = re.compile("(%s)" % "|".join(map(re.escape, searchReplc.keys())))
    try:
        t_out = robj_r.subn(lambda m: searchReplc[m.group(0)], text_in)
    except IOError as e:
        logger.debug("DoReplace, I/O error({0}): {1}".format(e.errno, e.strerror))
    except AttributeError as e:
        logger.debug(f"DoReplace AttributeError: {e}")
    except UnicodeEncodeError as e:
        logger.debug(f"DoReplace, UnicodeEncodeError: {e}")
    except UnicodeDecodeError as e:
        logger.debug(f"DoReplace, UnicodeDecodeError: {e}")
    except Exception as e:
        logger.debug(f"DoReplace, unexpected error: {e}")
    else:
        much = t_out[1]
        logger.debug(f'DoReplace, zamenjeno [{much}] objekata')
        return much, t_out[0]

def cleanUp(text_in):

    # okrugle zagrade                     '(\([^\)]*\))'
    # kockaste zagrade                    '(\[[^]]*\])'
    # vitičaste zagrade                   '(\{[^}]*\})'
    # crtice na početku prazne linije     '^\s*?\-+\s*?(?<=$)'
    # Tačka na kraju, prazna linija       '(^\s*?\.+)$'
    # Zarez na kraju, prazna linija       '(^\s*?,+)$'
    # Tačka zarez na kraju, prazna linija '(^\s*?;+)$'
    # Spejs na kraju linije         '(\s*?)$'
    # Uzvičnici                     '(^\s*?!+\s*?)$'
    # Znak pitanja                  '(^\s*?\?+\s*?)$'
    # Prva prazna linija            '(?<=,\d\d\d)\n\n(?=\w)'
    # '(?<=,\d\d\d)\n\n(?=\s*\S*?)'
    # reg-4 = re.compile(r'((?!\n)([A-Z\s]*){1,3}(?=\:)(?<![0-9a-z])\:\s)')
    reg_4 = re.compile(
        r"^\s*\-\.+\s+|(([A-Z ]*){1,3}(?=\:)(?<![0-9a-z])\:\s)|^[ \t]*", re.M
    )
    reg_P6 = re.compile(
        r"(\([^\)]*\))|(\[[^]]*\])|(\{[^}]*\})|(<i>\s*<\/i>)|^\s*?\-+\s*?(?<=$)", re.M
    )
    reg4n = re.compile(r'([A-Z ]*) [0-3](?=\:)')  # MAN 1: broj 1-3
    reg_P8 = re.compile(
        r"(\s*?)$|(^\s*?\.+)$|(^\s*?,+)$|(^\s*?;+)$|(^\s*?!+\s*?)$|(^\s*?\?+\s*?)$",
        re.M,
    )
    reg_S9 = re.compile("(?<=,\d\d\d)\n\n(?=\w)|(?<=,\d\d\d)\n\n(?=\s*\S*?)", re.M)
    reg8a = re.compile(
        r'^\s*(?<=.)|^-(?<=$)', re.M
    )  # Spejs na pocetku linije, i crtica na početku prazne linije
    regN = re.compile(r'(?<=^-)\:\s*', re.M)  # dve tacke iza crtice
    regColon = re.compile(r"^\s*: *", re.M)
    RL = re.compile(
        r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}(?=\n\s*\d+\n*?)"
    )
    r_dash = re.compile(r"^\s*- *-*\s*$", re.M)
    # def opFile(in_text):
    # return in_text.replace(']:', ']').replace('):', ')').replace('}:', '}').replace('  ', ' ')

    textis = srt.parse(text_in, ignore_errors=True)
    text_subs = srt.compose(textis)

    try:
        fp3 = reg_4.sub("", text_subs)

        fp5 = reg_P6.sub("", fp3)

        # rf1 = opFile(fp5)
        rf1 = regColon.sub("", fp5)

        fp11 = reg_P8.sub("", rf1)
        fp13 = reg_S9.sub("\n", fp11)
        fp13 = RL.sub("\n", fp13)
        fp14 = regN.sub('', fp13)
        fp14a = r_dash.sub('', fp14)
        fp15 = reg8a.sub('', fp14a)

        return fp15

    except Exception as e:
        logger.debug(f"CleanSubtitle proc, unexpected error: {e}")

def cleanLine(text_in):

    try:
        subs = list(srt.parse(text_in, ignore_errors=True))
        if len(subs) > 0:
            # Trim white spaces
            text_stripped = []
            for i in range(len(subs)):
                orig_text = subs[i].content
                stripped_text = subs[i].content.strip()
                if orig_text != stripped_text:
                    text_stripped.append(subs[i].index)
                    subs[i].content = subs[i].content.strip()

            # Find the list index of the empty lines. This is different than the srt index!
            # The list index starts from 0, but the srt index starts from 1.
            count = 0
            to_delete = []
            for sub in subs:
                if not sub.content:
                    to_delete.append(count)
                count = count + 1

            to_delete.sort(reverse=True)

            # Delete the empty/blank subtitles
            for i in to_delete:
                del subs[i]

            # Fix Index and trim white spaces
            for i in range(len(subs)):
                subs[i].index = i + 1

            if not text_stripped and not to_delete:
                logger.debug("CleanLine, Subtitle clean. No changes made.")
                return 0, srt.compose(subs)

            else:
                logger.debug(
                    "Index of subtitles deleted: {0}".format([i + 1 for i in to_delete])
                )
                logger.debug("Index of subtitles trimmed: {0}".format(text_stripped))
                logger.debug(
                    '{0} deleted, {1} trimmed'.format(
                        len(to_delete), len(text_stripped)
                    )
                )
                return len(subs), srt.compose(subs)
        else:
            logger.debug('No subtitles found.')
    except Exception as e:
        logger.debug(f"CleanSubtitle_CL, unexpected error: {e}")

def rm_dash(text_in):

    # fix settings ------------------------------------------------------------------------------
    try:
        ex = FILE_SETTINGS['key1']
        cb1_s = ex['fixgap']
        cb2_s = ex['linije']
        cb3_s = ex['italik']
        cb4_s = ex['crtice']
        cb5_s = ex['crtice_sp']
        cb6_s = ex['spejsevi']
        cb7_s = ex['kolor']
        cb_nl = ex['breaks']
        cb8_s = ex['nuliranje']
    except IOError as e:
        logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
    except Exception as e:
        logger.debug(f"FixSubtitle, unexpected error: {e}")
    # ------------------------------------------------------------------------------------------ #
    #  cb1_s Popravi gapove, cb2_s Poravnaj linije, cb3_s italik tagovi, cb8_s=nuliranje         #
    #  cb4_s Crtice na pocetku prvog reda, cb5_s Spejs iza crtice, cb6_s Vise spejseva u jedan   #
    # ------------------------------------------------------------------------------------------ #

    reg_0 = re.compile(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}")
    for_rpls = re.compile(r'(?<=\d,\d\d\d\n)-+\s*')
    _space_r = re.compile(r'^ +', re.M)
    f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
    spaceS_r = re.compile(r' {2,}')
    pe_r = re.compile(r"^\s*(?<=.)| +$", re.M)
    cs_r = re.compile(r"(?<=\W\s)- +\b|^\s*- +", re.M)
    ct_r = re.compile(r"</*font.*?>", re.I)
    sp_n = 0

    def remSel(text_in, rep, reple):
        s1 = rep.sub(reple, text_in)
        return s1

    text = remSel(text_in, _space_r, '')

    if cb4_s is True:
        text = remSel(text, for_rpls, '')

    if cb6_s is True:
        text = remSel(text, spaceS_r, ' ')
        text = remSel(text, pe_r, "")

    if cb5_s is True:
        text = remSel(text, cs_r, '-')
    elif cb5_s is False:
        sp_n = text.count('- ')
        if sp_n >= 3:
            text = remSel(text, cs_r, '-')

    if cb7_s is True:
        subs = list(srt.parse(text, ignore_errors=True))
        if len(subs) > 0:
            new_f = []
            for i in range(len(subs)):
                t = subs[i].content
                t = (
                    t.replace('</i><i>', '')
                    .replace('</i> <i>', ' ')
                    .replace('</i>\n<i>', '\n')
                    .replace('</i>-<i>', '-')
                    .replace('</i>\n-<i>', '-\n')
                )
                new_f.append(srt.Subtitle(subs[i].index, subs[i].start, subs[i].end, t))
            text = srt.compose(new_f)
        else:
            logger.debug('Fixer: No subtitles found!')

    if cb2_s is True:
        subs = list(srt.parse(text, ignore_errors=True))
        if len(subs) > 0:
            new_s = []
            for i in subs:
                n = poravnLine(i.content)
                if cb5_s is False and sp_n >= 3:
                    n = cs_r.sub(r'- ', n)
                new_s.append(srt.Subtitle(i.index, i.start, i.end, n))
            text = srt.compose(new_s)
        else:
            if not len(subs) > 0:
                logger.debug('Fixer: No subtitles found!')

    if cb3_s is True:
        text = remSel(text, ct_r, "")
        
    if cb_nl is True:
        subs = list(srt.parse(text, ignore_errors=True))
        new_s = []
        for i in subs:
            t = i.content
            if re.search(r"\n(?=[a-zA-Z -])", t, re.M):
                t = t.replace("\n", " ")
            new_s.append(srt.Subtitle(i.index, i.start, i.end, t))
        text = srt.compose(new_s)
            
    if cb8_s is True:
        if not cb1_s:
            try:
                text = remSel(text, reg_0, "00:00:00,000 --> 00:00:00,000")
            except Exception as e:
                logger.debug(f'Fixer: {e}')

    return text

def poravnLine(intext):
    def proCent(percent, whole):
        return (percent * whole) // 100

    def myWrapper(intext):
        f_rpl = re.compile(r'^((.*?\n.*?){1})\n', re.I)
        # n = len(intext) // 2
        n = proCent(48, len(intext))
        wrapper = TextWrapper(break_long_words=False, break_on_hyphens=False, width=n)
        te = wrapper.fill(intext)
        if te.count('\n') >= 2:
            te = f_rpl.sub(r'\1 ', te)
        elif te.count('\n') >= 3:
            te = f_rpl.sub(r'\1 ', te)
        elif te.count('\n') >= 4:
            te = f_rpl.sub(r'\1 ', te)
        elif te.count('\n') >= 5:
            te = f_rpl.sub(r'\1 ', te)
        elif te.count('\n') == 6:
            te = f_rpl.sub(r'\1 ', te)
        return te

    def movPos(text, n):
        # where - pozicija gde se nalazi zeljeni spejs
        text = text.replace('\n', ' ').replace('- ', '-')
        where = [m.start() for m in re.finditer(' ', text)][n - 1]
        # before - tekst ispred pozicije
        before = text[:where]
        # after - tekst iza pozicije
        after = text[where:]
        after = after.replace(' ', '\n', 1)  # zameni prvi spejs
        newText = before + after
        return newText

    n = intext
    # f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
    s_rpl = re.compile(' +')
    tag_rpl = re.compile(r'<[^<]*>')

    n = n.replace('\r', '').replace('\n', ' ')

    n = s_rpl.sub(' ', n)  # vise spejseva u jedan

    ln = re.sub(r"[\.\,\!\'\-]", "", n)
    ln = tag_rpl.sub(' ', ln)
    ln = s_rpl.sub(' ', ln)

    if len(ln) >= 30 and not n.startswith('<font'):
        s1 = myWrapper(n)
        prva = s1.split('\n')[0]
        prva = re.sub(r"[\.\,\!\-\?]", "", prva)
        druga = s1.split('\n')[-1]
        druga = re.sub(r"[\.\,\!\'\-\?]", "", druga)
        druga = tag_rpl.sub(' ', druga)
        druga = s_rpl.sub(' ', druga)
        len_prva = len("".join(prva))
        len_druga = len("".join(druga))
        tar1 = len_prva - len_druga
        tar2 = len_druga - len_prva
        if tar1 >= 4 or tar2 >= 4:
            s1 = myWrapper(s1)
            fls1 = tag_rpl.sub(' ', s1)
            fls1 = s_rpl.sub(' ', fls1)
            drugaS = len("".join(fls1.split('\n')[-1]))
            prvaS = len("".join(fls1.split('\n')[0]))
            if drugaS - prvaS >= 4:
                fls1 = tag_rpl.sub(' ', s1)
                fls1 = s_rpl.sub(' ', fls1)
                lw = fls1.split('\n')[-1].split()
                lw = [re.sub(r"[\.\!\,\'\-\?ijl]", "", i) for i in lw]
                dw = [len(x) for x in lw]  # duzine reci u listi
                c1 = s1.split('\n')[0].count(' ') + 1
                if len(lw) >= 1:
                    if (dw[0] + prvaS) <= (drugaS - dw[0]) + 2:
                        c = c1 + 1
                        s1 = movPos(s1, c)
                    sub = s1
                else: sub = s1
            else: sub = s1
        else: sub = s1
    else: sub = n

    return sub

class FileOpened:
    ''''''
    internal = []
    internPath = []
    internEnc = ""
    
    def __init__(self, path, multi=False):

        self.path = path
        self.multi = multi

        self.ErrorDlg = wx.MessageDialog(
            None,
            f"UnicodeDecodeError\n\n"
            f"Detektovane greške u tekstu,\n"
            f"ako je previše grešaka\n"
            f"pokušajte drugo kodiranje,\n"
            f"i opciju ReloadFile",
            "SubtitleConverter",
            style=wx.OK | wx.ICON_ERROR,
        )

    def isCompressed(self):

        # basepath = 'tmp'
        basepath = os.path.dirname(self.path)
        fileName = baseName(self.path)
        
        with zipfile.ZipFile(self.path, 'r') as zf:
            if len(zf.namelist()) == 1:
                singleFile = zf.namelist()[0]
                outfile = [filePath(basepath, singleFile)]
                if self.multi is False:
                    with open(outfile[0], 'wb') as f:
                        f.write(zf.read(singleFile))     ## zf.read() equaly bytes  ##
                else: self.internal.append(zf.read(singleFile).replace(b"\r\n", b"\n"))
                outfile1 = filePath(
                    os.path.dirname(self.path), singleFile
                )
                return outfile, outfile1
            elif not zf.namelist():
                logger.debug(f"{fileName} is empty")
            elif len(zf.namelist()) >= 2:
                izbor = [x for x in zf.namelist() if not x.endswith('/')]
                if len(zf.namelist()) > 9:
                    dlg = MultiChoice(None, "Pick files:", fileName, choices=izbor)
                else:
                    dlg = wx.MultiChoiceDialog(None, 'Pick files:', fileName, izbor)
                try:
                    if dlg.ShowModal() == wx.ID_OK:
                        response = dlg.GetSelections()
                        files = [izbor[x] for x in response]
                        names = [baseName(i) for i in files]
                        outfiles = [filePath(basepath, x) for x in names]
                        single = filePath(
                            os.path.dirname(self.path),
                            baseName(files[-1]),
                        )
                        if len(files) == 1:
                            with open(outfiles[0], "wb") as f:
                                f.write(zf.read(files[0]))
                        for i in files:
                            self.internal.append(zf.read(i).replace(b"\r\n", b"\n"))
                        self.internPath.extend((files))
                        return outfiles, single
                    else:
                        logger.debug(f'{self.path}: Canceled.')
                        dlg.Destroy()
                finally:
                    dlg.Destroy()

    @staticmethod
    def addBytes(path, enc, content):
        '''Create and append namedtuple to BYTES_TEXT list'''
        multi = namedtuple("multi", ["path","enc", "content"])
        BYTES_TEXT.append(multi(path, enc, content))
        
    @staticmethod
    def fCodeList():
        """"""
        kodek = FILE_SETTINGS["CB_value"].strip()
        if kodek == "auto":
            return [
                'utf-8',
                'windows-1250',
                'windows-1251',
                'windows-1252',
                'UTF-16LE',
                "UTF-16BE",
                'utf-8-sig',
                'iso-8859-1',
                'iso-8859-2',
                'utf-16',
                'ascii',
            ]
        else:
            return [kodek]
    
    def getByteText(self):
        """"""
        with open(self.path, "rb") as dat_file:
            return dat_file.read().replace(b"\r\n", b"\n")
        
    def findCode(self):
        ''''''
        data = open(self.path, "rb").read(4)
        if data.startswith(BOM_UTF8):
            return "utf-8-sig"
        else:
            for enc in self.fCodeList():
                try:
                    with codecs.open(self.path, 'r', encoding=enc) as fh:
                        fh.readlines()
                        fh.seek(0)
                except:
                    if  FILE_SETTINGS["CB_value"].strip() == "auto":
                        pass
                    else:
                        if self.ErrorDlg.ShowModal() == wx.ID_OK:
                            self.ErrorDlg.Destroy()
                else:
                    logger.debug(f'{baseName(self.path)}: {enc}')
                    break
            self.internEnc = enc
            return enc
    
    def findByteCode(self, n=0):
        """"""
        ## n is selecting number for multifile list ##  
        dat = self.internal[n]
        if dat[:4].startswith(BOM_UTF8):
            return "utf-8-sig"
        else:
            for enc in self.fCodeList():
                try:
                    dat.decode(enc)
                except:
                    if FILE_SETTINGS["CB_value"].strip() == "auto":
                        pass
                    else:
                        if self.ErrorDlg.ShowModal() == wx.ID_OK:
                            self.ErrorDlg.Destroy()
                else:
                    logger.debug(f"{baseName(self.path)}: {enc}")
                    break        
            self.internEnc = enc
            return enc

def newName(path, pre_suffix, multi=False):
    ''''''
    added = name_data[0]
    value2_s = name_data[1]
    value5_s = name_data[2]
    value_m = name_data[3]
    oformat = name_data[4]
    ex = name_data[5]

    spattern = re.compile(r"(?:\.srt){2,3}", re.I)
    tpattern = re.compile(r"(?:\.txt){2,3}", re.I)
    upattern = re.compile(r"\s*" + value_m + r"\d*", re.I)

    if len(re.findall(upattern, path)) == 2:
        path = upattern.sub("", path, count=2)
    elif len(re.findall(upattern, path)) == 3:
        path = upattern.sub("", path, count=3)
    if re.findall(spattern, path):
        path = spattern.sub(r".srt", path)
    elif re.findall(tpattern, path):
        path = tpattern.sub(r".txt", path)

    fprint = baseName(path)

    n = os.path.splitext(fprint)[0]

    if not "" in list(ex.values()):
        psufix = os.path.splitext(n)[-1]  ## presufix ispred sufixa
    else:
        psufix = n

    if oformat == "txt" and pre_suffix == value5_s:
        sufix = ".txt"
    elif oformat == "txt" and pre_suffix == value2_s:
        sufix = ".txt"
    ## srt,txt ili neki drugi otvoren
    else: sufix = os.path.splitext(path)[-1]

    suffix_list = ["." + x if not x.startswith("_") else x for x in ex.values()] + added
    suffix_list.append(value_m)
    suffix_list = [x.strip(".") if x.startswith(r".(") else x for x in suffix_list]

    _d = "." + pre_suffix  ## pre_suffix je unet u funkciji koja poziva newName
    if pre_suffix.startswith("_") or pre_suffix.startswith(r"("):
        _d = pre_suffix

    if psufix in suffix_list:
        name1 = '{0}{1}'.format(os.path.splitext(n)[0], _d)  ## u tmp/ folderu
    else: name1 = '{0}{1}'.format(n, _d)

    if name1.endswith("."): name1 = name1[:-1]

    for i in suffix_list:
        if i == "." or not i:
            continue
        fpattern = re.compile(i, re.I)
        count_s = len(re.findall(fpattern, name1))
        if count_s >= 2:
            name1 = "".join(name1.rsplit(i, count_s))
            if not name1.endswith(i):
                name1 = name1 + i
    return name1, sufix  ## Vraca samo ime fajla bez putanje

def nameDialog(name_entry, sufix_entry, dir_entry):

    ex = FILE_SETTINGS['key5']

    presuffix_l = filePath("resources", "var", "presuffix_list.bak")
    real_dir = dir_entry
    name1 = name_entry
    sufix = sufix_entry

    caption_str = '{}'.format(real_dir)
    dlg = wx.TextEntryDialog(
        None,
        'Ime fajla:',
        caption=caption_str,
        value="",
        style=wx.OK | wx.CANCEL | wx.CENTER,
        pos=wx.DefaultPosition,
    )
    dlg.SetValue(name1)

    if dlg.ShowModal() == wx.ID_OK:
        name = dlg.GetValue()
        nameO = '{0}{1}'.format(filePath(real_dir, name), sufix)
        if nameO.endswith("."):
            nameO = nameO[:-1]
        dlg.Destroy()

        with open(presuffix_l, 'a', encoding='utf-8') as f:
            if not '' in list(ex.values()):
                presuffix_x = os.path.splitext(os.path.splitext(nameO)[0])[-1] + "\n"
                if "_" in presuffix_x:
                    presuffix_ = "_" + presuffix_x.split("_")[-1] + "\n"
                else:
                    presuffix_ = ""
            else:
                presuffix_x = ""
                presuffix_ = os.path.splitext(os.path.splitext(nameO)[0])[-1] + "\n"
            f.write(presuffix_)
        return nameO
    else:
        dlg.Destroy()
        return None

def writeToFile(text, path, enc, multi=False, ask=False):
    
    if enc in codelist:
        error = 'surrogatepass'
    else: error = 'replace'
    if multi is False:
        if os.path.isfile(path) and os.path.dirname(path) != "tmp" and ask is True:
            dlg = wx.MessageBox(
                f"{baseName(path)}\nFile already exists! Proceed?",
                "Overwrite the file?",
                wx.ICON_INFORMATION | wx.YES_NO,
                None,
            )
            if dlg == wx.NO:
                return
    text = chreg.sub("?", text)
    try:
        with open(path, 'w', encoding=enc, errors=error, newline='\r\n') as n_File:
            n_File.write(text)
        logger.debug(f"Write: {path}; {enc}")
        return True
    except IOError as e:
        logger.debug(f"writeToFile IOError: {e}")
    except AttributeError as e:
        logger.debug(f"writeToFile, AttributeError: {e}")
    except UnicodeEncodeError as e:
        logger.debug(f"writeToFile, UnicodeEncodeError: {e}")
    except UnicodeDecodeError as e:
        logger.debug(f"writeToFile, UnicodeDecodeError: {e}")
    except LookupError as e:
        logger.debug(f"writeToFile, LookupError: {e}")
    except Exception as e:
        logger.debug(f"writeToFile, Unexpected error: {e}")
        
        
def addPrevious(action, enc="utf-8", content="empty", psuffix="empty", tpath="empty", rpath="empty"):
    '''This function creates namedtuple'''
    prev = namedtuple("prev", ["action", "enc", "content", "psuffix", "tpath", "rpath"])
    PREVIOUS.append(prev(action, enc, content, psuffix, tpath, rpath))

def fileHandle(infiles, text_control, fdrop=False):
    """"""
    c = 0
    if type(infiles) != list:
        infiles = [infiles]
    
    def file_go(infile, rfile):
        enc = FileOpened(infile).findCode()
        text = normalizeText(enc, infile, data=None)
        text = text.replace("\r\n", "\n")
        bufferText(text, WORK_TEXT)
        text = WORK_TEXT.getvalue()
        nlist = checkErrors(text)
        text_control.SetValue(text)
        text_control.SetInsertionPoint(0)
        if fdrop is False:
            if nlist:
                for i in nlist:
                    text_control.SetStyle(i[0], i[1], wx.TextAttr("YELLOW", "BLUE"))
                    text_control.SetInsertionPoint(i[1])
        PREVIOUS.clear()
        addPrevious("Open", enc, text, "", infile, rfile)
        logger.debug(f"Opened: {baseName(infile)}, {enc}")
        if os.path.exists(droppedText): os.remove(droppedText)
        d_text = {text: enc}
        with open(filePath('resources', 'var', 'r_text0.pkl'), 'wb') as t:
            pickle.dump(d_text, t)

        return enc

    if len(infiles) > 1:
        rpath = [infiles[-1]]
        BYTES_TEXT.clear()
        text_control.SetValue('Files List:\n\n')
        if fdrop is True:
            dispatcher.send("TMP_PATH", message=infiles, msg=[rpath, "", True])
        for i in range(len(infiles)):
            if not zipfile.is_zipfile(infiles[i]):
                try:
                    if not os.path.exists(infiles[i]):
                        logger.debug(f"Skipping {baseName(infiles[i])}")
                        text_control.AppendText(
                            f"\n_SKIP_:{baseName(infiles[i])}"
                        )
                        continue
                    c += 1
                    fop = FileOpened(infiles[i])
                    enc = fop.findCode()
                    fop.addBytes(infiles[i], enc, fop.getByteText())
                    name = baseName(infiles[i])
                    text_control.AppendText(f"{c} - {name}\n")
                except Exception as e:
                    logger.debug(f'FileHandler: {e}')
            else:
                try:
                    fop = FileOpened(infiles[i], multi=True)
                    fop.internal.clear()
                    outfile, rfile = fop.isCompressed()
                except:
                    logger.debug('FileHandler: No files selected.')
                else:
                    if len(outfile) == 1:
                        c += 1
                        fop = FileOpened(outfile[0])
                        enc = fop.findByteCode(n=0)
                        fop.addBytes(fop.path, enc, fop.internal[0])
                        nam = outfile[0]
                        text = baseName(nam)
                        text_control.AppendText(f"{c} - {text}\n")
                        fop.internal.clear()
                    elif len(outfile) > 1:
                        for i in range(len(outfile)):
                            c += 1
                            fop = FileOpened(outfile[i])
                            enc = fop.findByteCode(n=i)
                            fop.addBytes(outfile[i], enc, fop.internal[i])
                            text = baseName(outfile[i])
                            text_control.AppendText(f"{c} - {text}\n")
                        fop.internal.clear()
        logger.debug('FileHandler: Ready for multiple files.')
    else:
        name = "".join(infiles)
        if zipfile.is_zipfile(name):
            logger.debug(f'ZIP archive: {baseName(name)}')
            try:
                fop = FileOpened(name)
                fop.internal.clear()
                BYTES_TEXT.clear()
                outfile, rfile = fop.isCompressed() ## outfile in tmp
            except Exception as e:
                logger.debug(f'ZIP; {e}.')
            else:
                if len(outfile) == 1:
                    if lenZip(name):
                        ## Append if not multiple
                        FILE_HISTORY.append(lenZip(name))
                    enc = file_go(outfile[0], rfile)
                    FILE_HISTORY.append(outfile[0])
                    if fdrop is True:
                        try:
                            dispatcher.send("TMP_PATH", message=outfile, msg=[rfile, enc, False])
                        except Exception as e:
                            logger.debug(f"dispatcher: {e} {outfile} {rfile}")
                elif len(outfile) > 1:
                    text_control.SetValue('Files List:\n\n')
                    for i in range(len(outfile)):
                        c += 1
                        fop = FileOpened(outfile[i], True)
                        enc = fop.findByteCode()
                        fop.addBytes(outfile[i], enc, fop.internal[i])
                        text = baseName(outfile[i])
                        text_control.AppendText(f"{c} - {text}\n")
                    if fdrop is True:
                        dispatcher.send("TMP_PATH", message=outfile, msg=[rfile, enc, True])
                    logger.debug('FileHandler: Ready for multiple files.')
        elif not zipfile.is_zipfile(name):
            ## Single file only
            ## name = real path
            BYTES_TEXT.clear()
            FILE_HISTORY.append(name)
            tmp_path = filePath('tmp', baseName(name))
            if os.path.isfile(tmp_path):
                if os.path.dirname(name) == "tmp":
                    text = open(tmp_path, "rb").read()
                os.remove(tmp_path)
            if os.path.isfile(name):
                shutil.copy(name, tmp_path)
            else: open(tmp_path, "wb").write(text)
            enc = file_go(tmp_path, name)
            if fdrop is True:
                dispatcher.send("TMP_PATH", message=tmp_path, msg=[name, enc, False])
                
class FileDrop(wx.FileDropTarget):
    '''Drop target functionality for files'''
    
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    def OnDropFiles(self, x, y, filenames):
        '''When files are dropped, handle them'''
        
        lfiles = [x for x in filenames]
        
        fileHandle(lfiles, self.window, fdrop=True)
        
        return True

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

def checkFile(path, newfile, text_s, multi=False):
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
            ).format(baseName(file1_name), n_sign)

            logger.debug(poruka)
            if multi is True:
                file1_name = newfile
            error_text = f"Greška:\n\n{baseName(file1_name)}\nBilo je neispravnih znakova u\
            tekstu\nkonvertovanih kao znak `?`\nUkupno: [{n_sign}]\nProverite tekst."
            if error_text:
                error_text = re.sub("(?: ){2,4}", " ", error_text)
            return error_text
    except UnboundLocalError as e:
        logger.debug(f"File_Check, error({e})")
    except Exception as e:
        logger.debug(f"File_Check, unexpected error: {e}")
        
def checkErrors(text_in):
    
    fpaterns =\
        '|'.join(['ï»¿Å','Ä','Å½','Ä','Ä','Å¡','Ä','Å¾','Ä','Ä',"ď»ż","Ĺ˝",'Ĺ',\
        'ĹĄ','Ĺž','Ä','Å','Ä‡','Ä¿','Ä²','Ä³','Å¿','Ã¢â',"�","Д†","Д‡","Ť","Lˇ","ï»¿","ð", "¿"])
    
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
    
def checkChars(text, path=None):
    def percentage(part, whole):
        try:
            return int(100 * part / whole)
        except ZeroDivisionError:
            logger.debug(f"File is empty: {baseName(path)}")
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

def displayError(text, tctrl, rdir, path, new_enc, multi=False):
    """"""
    nlist = w_position(r"\?", text)
    epath = baseName(path)
    
    if type(rdir) is list:
        rdir = [x for rdir[0] in rdir for x in rdir[0]]
        outf = os.path.join(rdir[0], os.path.splitext(epath)[0]+"_error.log")
    else:
        outf = os.path.join(rdir, os.path.splitext(epath)[0]+"_error.log")
    
    showMeError(path, text, outf, new_enc)
    text = text.replace('¬', '?')
    
    if multi is False:
        tctrl.SetValue(text)
        for i in nlist:
            if not len(nlist) > 300:
                tctrl.SetStyle(i[0], i[1], wx.TextAttr("YELLOW","GREEN"))
                tctrl.SetInsertionPoint(i[1])
                
    return text

def showMeError(infile, in_text, outfile, kode):

    try:
        cb3_s = FILE_SETTINGS["Preferences"]["ShowLog"]
    except:
        pass
    subs = list(srt.parse(in_text, ignore_errors=True))

    if len(subs) > 0:

        st = "LINIJE SA GREŠKAMA:\n\n"
        if kode == 'windows-1251':
            st = "ЛИНИЈЕ СА ГРЕШКАМА:\n\n"
            kode = "utf-8"
        FP = re.compile(r"\?")
        count = 0
        sl = []
        for i in subs:
            t = i.content
            FE = re.findall(FP, t)
            if FE:
                sub = srt.Subtitle(i.index, i.start, i.end, t.replace("¬", "?"))
                sl.append(sub)
                count += 1
        if count > 0:
            try:
                with open(outfile, "w", encoding=kode) as f:
                    subs_data = srt.compose(sl, reindex=False)
                    f.write(st + subs_data)
            except Exception as e:
                logger.debug(f"W_ErrorFile, unexpected error: {e}")

            if os.path.isfile(outfile):
                logger.debug(f": {outfile}")
            if cb3_s is True:
                webbrowser.open(outfile)
    else:
        logger.debug(f'showMeError: No subtitles found in {os.path.basename(infile)}')

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
        with open(
            text_in, 'w', encoding='utf-8', newline="\r\n"
        ) as text_file:
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
            key = x[0].strip()
            value = x[-1].strip()
            new_dict[key] = value
        return new_dict

def new_dict(indict, n=None):
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
                key = w[0] + ' ' + w[1] + '\n' + w[-1]
                value = x[-1]
                newDict[key] = value
        return newDict

fDict = os.path.join('dictionaries', 'Dictionary-1.txt')
fDict1 = os.path.join('dictionaries', 'Dictionary-2.txt')
fDict0 = os.path.join('dictionaries', 'Dictionary-0.txt')
fDict_special = os.path.join('dictionaries', 'Special-Replace.txt')

remBom(fDict)
remBom(fDict1)
remBom(fDict0)
remBom(fDict_special)

dictionary_1 = dict_fromFile(fDict, delim='=>')
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

rplSmap = drep ## LATIN_chars 

#########################

lat_cir_mapa = {
    'đ': 'ђ',
    'Đ': 'Ђ',
    'e': 'е',
    'r': 'р',
    't': 'т',
    'z': 'з',
    'u': 'у',
    'i': 'и',
    'o': 'о',
    'p': 'п',
    'a': 'а',
    's': 'с',
    'd': 'д',
    'f': 'ф',
    'g': 'г',
    'h': 'х',
    'j': 'ј',
    'k': 'к',
    'l': 'л',
    'c': 'ц',
    'v': 'в',
    'b': 'б',
    'n': 'н',
    'm': 'м',
    'š': 'ш',
    'ž': 'ж',
    'č': 'ч',
    'ć': 'ћ',
    'E': 'Е',
    'R': 'Р',
    'T': 'Т',
    'Z': 'З',
    'U': 'У',
    'I': 'И',
    'O': 'О',
    'P': 'П',
    'A': 'А',
    'S': 'С',
    'D': 'Д',
    'F': 'Ф',
    'G': 'Г',
    'H': 'Х',
    'J': 'Ј',
    'K': 'К',
    'L': 'Л',
    'C': 'Ц',
    'V': 'В',
    'B': 'Б',
    'N': 'Н',
    'M': 'М',
    'Š': 'Ш',
    'Ž': 'Ж',
    'Č': 'Ч',
    'Ć': 'Ћ',
}

#######################################################

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

pLatin_rpl = ln

pre_cyr = dict_fromFile(prelatCyr, delim='=')

conf_file = os.path.join("resources", "shortcut_keys.cfg")

_shortcutsKey = dict_fromFile(conf_file, delim="=")

shortcutsKey = defaultdict(str)
shortcutsKey.update(_shortcutsKey)
