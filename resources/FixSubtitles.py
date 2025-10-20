# -*- coding: UTF-8 -*-
#
import sys

sys.path.append("../")

from settings import MAIN_SETTINGS, WORK_TEXT
from merge import ShrinkGap, FixSubGaps
from resources.DictHandle import Dictionaries 

import srt
import re
from textwrap import TextWrapper

import wx

import logging.config
logger = logging.getLogger(__name__)


class SubtitleFixer:
    
    def __init__(self, text_in=None, multi=False):
        self.text_in = text_in
        self.multi = multi
        
    @staticmethod
    def rm_dash(text_in):
        
        # ------------------------------------------------------------------------------------------ #
        cb1_s = MAIN_SETTINGS['key1']["fixgap"]
        cb2_s = MAIN_SETTINGS['key1']["linije"]
        cb3_s = MAIN_SETTINGS['key1']["kolor"]
        cb4_s = MAIN_SETTINGS['key1']["crtice"]
        cb5_s = MAIN_SETTINGS['key1']["crtice_sp"]
        cb6_s = MAIN_SETTINGS['key1']["spejsevi"]
        cb7_s = MAIN_SETTINGS['key1']["italik"]
        cb_nl = MAIN_SETTINGS['key1']["breaks"]
        cb8_s = MAIN_SETTINGS['key1']["nuliranje"]
        # ------------------------------------------------------------------------------------------ #
        
        reg_0 = re.compile(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}")
        for_rpls = re.compile(r'(?<=\d,\d\d\d\n)-+\s*')
        _space_r = re.compile(r'^ +', re.M)
        f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
        spaceS_r = re.compile(r' {2,}')
        pe_r = re.compile(r"^\s*(?<=.)| +$", re.M)
        cs_r = re.compile(r"(?<=\W\s)- +\b|^\s*- +", re.M)
        ct_r = re.compile(r"</*font.*?>", re.I)
        commas = re.compile(r"(?<!www)(,|\.)(?!com|net|org|rs|info|io)([^\s\d<?.])")
        sp_n = 0

        def apply_regex(text_in, RP, replace_with):
            return RP.sub(replace_with, text_in)
            
        text = apply_regex(text_in, _space_r, '')

        if cb4_s is True:
            text = apply_regex(text, for_rpls, '')

        if cb5_s is True:
            text = apply_regex(text, cs_r, '-')
        elif cb5_s is False:
            sp_n = text.count('- ')
            if sp_n >= 3:
                text = apply_regex(text, cs_r, '-')

        if cb7_s is True:
            subs = list(srt.parse(text, ignore_errors=True))
            tag_pattern = re.compile(r"</i> *\r?\n *<i>")
            tag_pattern1 = re.compile(r"</i>\s*\s*<i>")
            tag_pattern2 = re.compile(r"</i> *\- *<i>")
            if len(subs) > 0:
                new_f = []
                for i in range(len(subs)):
                    line = subs[i].content
                    line = tag_pattern.sub("\n", line)
                    line = tag_pattern1.sub(r" ", line)
                    line = tag_pattern2.sub(r"-", line)
                    new_f.append(srt.Subtitle(subs[i].index, subs[i].start, subs[i].end, line))
                text = srt.compose(new_f)
            else:
                logger.debug('Fixer: No subtitles found!')

        if cb6_s is True:
            text = commas.sub(r"\1 \2", text)
            text = apply_regex(text, spaceS_r, " ")
            text = apply_regex(text, pe_r, "")

        if cb2_s is True:
            subs = list(srt.parse(text, ignore_errors=True))
            if len(subs) > 0:
                new_s = []
                for i in subs:
                    n = SubtitleFixer.poravnLine(i.content)
                    if cb5_s is False and sp_n >= 3:
                        n = cs_r.sub(r'- ', n)
                    new_s.append(srt.Subtitle(i.index, i.start, i.end, n))
                text = srt.compose(new_s)
            else:
                if not len(subs) > 0:
                    logger.debug('Fixer: No subtitles found!')

        if cb3_s is True:
            text = apply_regex(text, ct_r, "")

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
                    text = apply_regex(text, reg_0, "00:00:00,000 --> 00:00:00,000")
                except Exception as e:
                    logger.debug(f'Fixer: {e}')
        return text
    
    @staticmethod
    def doReplace(text_in):
        dict_handler = Dictionaries()
        searchReplc = dict_handler.searchReplc
        robj_r = re.compile("(%s)" % "|".join(map(re.escape, searchReplc.keys())))
        try:
            t_out = robj_r.subn(lambda m: searchReplc[m.group(0)], text_in)
        except (IOError, AttributeError, UnicodeDecodeError, Exception) as e:
            logger.debug(f"DoReplace, error: {e}")
        else:
            much = t_out[1]
            logger.debug(f'DoReplace, zamenjeno [{much}] objekata')
            return much, t_out[0]    
 
    def FixSubtileText(self):

        cb1_s = MAIN_SETTINGS['key1']['fixgap']
        cb_sh = MAIN_SETTINGS['key1']["shrinkgap"]
        cb8_s = MAIN_SETTINGS['key1']['nuliranje']
        _gap = MAIN_SETTINGS['key1']["mingap"]
        mgap = MAIN_SETTINGS['key1']["maxgap"]

        subs = list(srt.parse(self.text_in, ignore_errors=True))
        if len(subs) == 0:
            logger.debug("Fixer: No subtitles found.")
        else:
            text = ""
            if cb1_s is True:
                if cb8_s != True:
                    m = 0
                    s1 = 0
                    subs = list(srt.parse(self.text_in, ignore_errors=True))
                    x, y = FixSubGaps(inlist=subs, mingap=_gap)  # Expand gaps
                    m += x
                    s1 += y
                else:
                    logger.debug("Fixer: Remove gaps not enabled.")
            if cb_sh is True:
                subs = list(srt.parse(WORK_TEXT.getvalue(), True))
                g = ShrinkGap(inlist=subs, maxgap=mgap, mingap=_gap)
                m += g
            try:
                if cb8_s is False:
                    text = srt.compose(srt.parse(WORK_TEXT.getvalue(), True))
                else:
                    text = WORK_TEXT.getvalue()
            except Exception as e:
                logger.debug(f"FixSubtitle, unexpected error: {e}")

            text_fixed = self.rm_dash(text)
            if cb1_s is True:
                if cb8_s != True:
                    if s1 > 1:
                        m1 = f'\nPreklopljenih linija: [ {s1} ]'
                        logger.debug(m1)
                    else:
                        m1 = ''
                    logger.debug(f'Fixer: Popravljenih gapova: {m}')
                    if m >= 0:
                        if self.multi is False:
                            wx.MessageBox(
                                f"Subtitle fixer\n\n"
                                f"Popravljenih gapova: [ {m} ]\n{m1}\n",
                                "SubtitleConverter",
                            )
            return text_fixed
                        
    @staticmethod
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
        reg_S9 = re.compile(r"(?<=,\d\d\d)\n\n(?=\w)|(?<=,\d\d\d)\n\n(?=\s*\S*?)", re.M)
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
    
    @staticmethod
    def cleanLine(text_in):
        """"""
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
            
    @staticmethod
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



