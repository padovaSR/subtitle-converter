#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  Copyright (C) 2020  padovaSR
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

import re
import srt
import datetime as DT
from srt import Subtitle
from pysrt import SubRipFile, SubRipItem
import logging.config

from settings import WORK_TEXT

logger = logging.getLogger(__name__)

def myMerger(subs_in, max_time, max_char, _gap):

    subs = subs_in

    dsub = SubRipItem(
        subs[-1].index + 1,
        subs[-1].start + 6000,
        subs[-1].end + 11000,
        'Darkstar test appliance',
    )
    if len(subs)-1 % 2 != 0: subs.append(dsub)
    
    parni = [x for x in subs[2::2]]
    neparni = [x for x in subs[1::2]]
    first = subs[0]

    def merge_lines(inPar, inNepar):
        re_pattern = re.compile(r'<[^<]*>')
        new_j = SubRipFile()
        for first, second, in zip(
            inNepar, inPar
        ):
            ## ordinal je vreme u milisekundama
            gap = second.start.ordinal - first.end.ordinal
            trajanje = second.end.ordinal - first.start.ordinal
            tekst1 = re.sub(re_pattern, '', first.text)
            tekst2 = re.sub(re_pattern, '', second.text)
            text_len = len(tekst1) + len(tekst2)
            if gap <= _gap and trajanje <= max_time and text_len <= max_char:
                if (
                    first.text == second.text
                    and first.start == second.start
                    and first.end == second.end
                ):
                    sub = SubRipItem(first.index, first.start, second.end, first.text)
                    new_j.append(sub)
                else:
                    sub = SubRipItem(
                        first.index,
                        first.start,
                        second.end,
                        first.text + " " + second.text,
                    )
                    new_j.append(sub)
            else:
                ## dodaj originalne linije
                sub1 = SubRipItem(first.index, first.start, first.end, first.text)
                sub2 = SubRipItem(second.index, second.start, second.end, second.text)
                new_j.append(sub1)
                new_j.append(sub2)

        if dsub in new_j:
            new_j.remove(dsub)
        new_j.clean_indexes()

        parni = [x for x in new_j[1::2]]
        neparni = [x for x in new_j[0::2]]

        return new_j, parni, neparni
    
    out_f, par1, nep1 = merge_lines(parni, neparni)
    out_f, par2, nep2 = merge_lines(par1, nep1)
    out_f, par3, nep3 = merge_lines(par2, nep2)
    out_f, par4, nep4 = merge_lines(par3, nep3)
    
    out_f.insert(0, first)
    
    for i in out_f:
        if i.text == "Darkstar test appliance":
            out_f.remove(i)
            out_f.clean_indexes()    
    
    WORK_TEXT.truncate(0)
    WORK_TEXT.seek(0)
    SubRipFile(out_f).write_into(WORK_TEXT)
    WORK_TEXT.seek(0)


class FixSubGaps:
    """"""
    def __init__(self, inlist=[], mingap=0):
        """"""
        self.inlist = inlist
        self.mingap = mingap
        self.Left = self.mingap*70/100
        self.Right = self.mingap*30/100
        
    # taken from srt_tools
    @staticmethod
    def mTime(delta):
            return delta.days*86400000+delta.seconds*1000+delta.microseconds/1000
    
    def powerSubs(self):
        ''''''
        gaps, overlap, new_list = self.leftGap()
        new_subs_list = self.rightGap(new_list)
            
        WORK_TEXT.truncate(0)
        WORK_TEXT.write(srt.compose(new_subs_list))
        WORK_TEXT.seek(0)        
        return gaps, overlap
    
    def leftGap(self):
        """"""
        inlist = self.inlist
        mingap = self.mingap
        Left = self.Left
        gaps = 0
        overlap = 0
        new_s = []
        
        for FSUB in zip(inlist, inlist[1:]):
            end_1 = self.mTime(FSUB[0].end)
            start_1 = self.mTime(FSUB[1].start)
            if start_1 < end_1: overlap += 1
            gap = start_1 - end_1
            if gap < mingap:
                gaps += 1            
                new_end = DT.timedelta(milliseconds=(start_1-Left))
                new_s.append(Subtitle(FSUB[0].index, FSUB[0].start, new_end, FSUB[0].content))
            else: new_s.append(FSUB[0])
        new_s.append(inlist[len(inlist)-1])
        
        return gaps, overlap, new_s
        
    def rightGap(self, in_list):
        """"""
        inlist = in_list
        mingap = self.mingap
        Right = self.Right
        new_f = []
        
        new_f.append(inlist[0])
        for FSUB in zip(inlist, inlist[1:]):
            end_1 = self.mTime(FSUB[0].end)
            start_1 = self.mTime(FSUB[1].start)
            gap = start_1 - end_1
            if gap < mingap:
                new_start = DT.timedelta(milliseconds=(start_1+Right))
                new_f.append(Subtitle(FSUB[1].index, new_start, FSUB[1].end, FSUB[1].content))
            else: new_f.append(FSUB[1])
                
        return new_f

