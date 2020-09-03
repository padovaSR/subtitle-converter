#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
import os
import re
import unicodedata
import tempfile
import srt
import pysrt
import pickle
from textwrap import TextWrapper
from zamenaImena import (
    lat_cir_mapa,
    pLatin_rpl,
    pre_cyr,
    rplSmap,
    dict0_n,
    dict0_n2,
    dict1_n,
    dict1_n2,
    dict2_n,
    dict2_n2,
    dictionary_0,
    dictionary_1,
    dictionary_2,
    searchReplc,
)
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
            if reversed_action == False:
                robjCyr = re.compile('(%s)' % '|'.join(map(re.escape, pre_cyr.keys())))
                text = robjCyr.sub(lambda m: pre_cyr[m.group(0)], text)
            elif reversed_action == True:
                pre_lat = dict(map(reversed, pre_cyr.items()))
                robjLat = re.compile('(%s)' % '|'.join(map(re.escape, pre_lat.keys())))
                text = robjLat.sub(lambda m: pre_lat[m.group(0)], text)
        except Exception as e:
            logger.debug(f"Preprocessing, unexpected error: {e}")
        ############################################################################
        MAPA = lat_cir_mapa
        if reversed_action == True:
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
                if preProc == True:
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
            
def writeTempStr(inFile, text, kode):

    _error = 'strict'
    if kode in codelist:
        _error = 'surrogatepass'
    try:
        with tempfile.TemporaryFile() as tfile:
            tfile.write(text.encode(encoding=kode, errors=_error))
            tfile.seek(0)
            content = tfile.read()
            with open(inFile, 'wb') as out:
                out.write(content)
    except IOError as e:
        logger.debug("WriteTempStr, I/O error({0}): {1}".format(e.errno, e.strerror))
    except AttributeError as e:
        logger.debug(f"writeTempStr AttributeError: {e}")
    except UnicodeEncodeError as e:
        logger.debug(f"WriteTempStr, UnicodeEncodeError: {e}")
    except UnicodeDecodeError as e:
        logger.debug(f"WriteTempStr, UnicodeDecodeError: {e}")
    except Exception as e:
        logger.debug(f"WriteTempStr, unexpected error: {e}")


def bufferText(intext, buffer):

    buffer.truncate(0)
    buffer.seek(0)
    buffer.write(intext)
    buffer.seek(0)

def normalizeText(code_in, path, data=None):
    '''text normalization'''
    error = 'strict'
    # error="surogateescape"
    if code_in in codelist:
        error = 'surrogatepass'
    try:
        if path:
            text = open(path, 'r', encoding=code_in, errors=error).read()
        else:
            text = data.decode(encoding=code_in, errors=error)
        text_normalized = unicodedata.normalize('NFKC', text)
        return text_normalized
    except Exception as e:
        logger.exception(f"NormalizeText error: {e})")
    
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
            .replace(b"\xc4\x8f\xc2\xbb\xc5\xbc", b"")
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

    if len(pysrt.from_string(text_in)) == 0:
        logger.debug(f"Transkrib, No subtitles found.")
    else:
        subs = srt.parse(text_in)
        text_in = srt.compose(subs)

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

    robj_r = re.compile('(%s)' % '|'.join(map(re.escape, searchReplc.keys())))
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

    # def opFile(in_text):
    # return in_text.replace(']:', ']').replace('):', ')').replace('}:', '}').replace('  ', ' ')

    textis = srt.parse(text_in)
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
        fp15 = reg8a.sub('', fp14)

        return fp15

    except Exception as e:
        logger.debug(f"CleanSubtitle proc, unexpected error: {e}")


def cleanLine(text_in):

    try:
        subs = list(srt.parse(text_in))
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
        with open(
            os.path.join('resources', 'var', 'dialog_settings.db.dat'), "rb"
        ) as sp:
            data = pickle.load(sp)
            ex = data['key1']
            cb1_s = ex['state1']
            cb2_s = ex['state2']
            cb3_s = ex['state3']
            cb4_s = ex['state4']
            cb5_s = ex['state5']
            cb6_s = ex['state6']
            cb7_s = ex['state7']
            cb8_s = ex['state8']
    except IOError as e:
        logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
    except Exception as e:
        logger.debug(f"FixSubtitle, unexpected error: {e}")
    # ------------------------------------------------------------------------------------------ #
    #  cb1_s Popravi gapove, cb2_s Poravnaj linije, cb3_s Pokazi linije sa greskama,             #
    #  cb4_s Crtice na pocetku prvog reda, cb5_s Spejs iza crtice, cb6_s Vise spejseva u jedan   #
    # ------------------------------------------------------------------------------------------ #

    reg_0 = re.compile(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}")
    for_rpls = re.compile(r'(?<=\d,\d\d\d\n)-+\s*')
    _space_r = re.compile(r'^ +', re.M)
    f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
    spaceS_r = re.compile(r' {2,}')
    pe_r = re.compile(r"^\s*(?<=.)| +$", re.M)
    cs_r = re.compile(r'\B- +')
    cs_r1 = re.compile(r'\B-')
    ct_r = re.compile(r"</*font.*?>", re.I)
    sp_n = 0

    def remSel(text_in, rep, reple):
        s1 = rep.sub(reple, text_in)
        return s1

    text = remSel(text_in, _space_r, '')

    if cb4_s == True:
        text = remSel(text, for_rpls, '')

    if cb6_s == True:
        text = remSel(text, spaceS_r, ' ')
        text = remSel(text, pe_r, "")

    if cb5_s == True:
        text = remSel(text, cs_r, '-')
    elif cb5_s == False:
        sp_n = text.count('- ')
        if sp_n >= 3:
            text = remSel(text, cs_r, '-')

    if cb7_s == True:
        if not cb8_s:
            subs = list(srt.parse(text))
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
                    sub = srt.Subtitle(subs[i].index, subs[i].start, subs[i].end, t)
                    new_f.append(sub)
                text = srt.compose(new_f)
            else:
                logger.debug('Fixer: No subtitles found!')

    if cb2_s == True:
        if not cb8_s:
            subs = list(srt.parse(text))
            if len(subs) > 0:
                new_s = []
                for i in subs:
                    n = poravnLine(i.content)
                    if cb5_s == False and sp_n >= 3:
                        n = cs_r1.sub(r'- ', n)
                    sub = srt.Subtitle(i.index, i.start, i.end, n)
                    new_s.append(sub)
                text = srt.compose(new_s)
            else:
                if not len(subs) > 0:
                    logger.debug('Fixer: No subtitles found!')

    if cb3_s == True:
        text = remSel(text, ct_r, "")

    if cb8_s == True:
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
        n = proCent(50, len(intext))
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
                else:
                    sub = s1
            else:
                sub = s1
        else:
            sub = s1
    else:
        sub = n

    return sub

