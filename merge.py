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
from itertools import zip_longest
from srt import Subtitle
import logging.config

from settings import WORK_TEXT

logger = logging.getLogger(__name__)

# Taken from srt_tools
def mTime(delta):
    return delta.days*86400000+delta.seconds*1000+delta.microseconds/1000

def myMerger(subs_in, max_time, max_char, _gap):

    subs = subs_in

    dsub = Subtitle(
        subs[-1].index + 1,
        DT.timedelta(milliseconds=(mTime(subs[-1].start) + 6000)),
        DT.timedelta(milliseconds=(mTime(subs[-1].end) + 11000)),
        'Darkstar test appliance',
    )
    
    parni = subs[1::2]
    neparni = subs[0::2]
    
    def merge_lines(inPar, inNepar):
        re_pattern = re.compile(r'<[^<]*>')
        new_j = []
        for (first, second,) in zip_longest(inNepar, inPar, fillvalue=dsub):
            
            gap = mTime(second.start) - mTime(first.end)
            trajanje = mTime(second.end) - mTime(first.start)
            tekst1 = re.sub(re_pattern, '', first.content)
            tekst2 = re.sub(re_pattern, '', second.content)
            text_len = len(tekst1) + len(tekst2)
            if gap <= _gap and trajanje <= max_time and text_len <= max_char:
                if (
                    first.content == second.content
                    and first.start == second.start
                    and first.end == second.end
                ):
                    new_j.append(Subtitle(first.index, first.start, second.end, first.content))
                else:
                    new_j.append(Subtitle(first.index, first.start, second.end, f"{first.content} {second.content}"))
            else:
                new_j.append(Subtitle(first.index, first.start, first.end, first.content))
                new_j.append(Subtitle(second.index, second.start, second.end, second.content))

        parni = new_j[1::2]
        neparni = new_j[0::2]

        return new_j, parni, neparni
    
    out_f, par1, nep1 = merge_lines(parni, neparni)
    out_f, par2, nep2 = merge_lines(par1, nep1)
    out_f, par3, nep3 = merge_lines(par2, nep2)
    out_f, par4, nep4 = merge_lines(par3, nep3)
    
    for i in out_f[-4:]:
        if i.content == "Darkstar test appliance": out_f.remove(i)    
    
    WORK_TEXT.truncate(0)
    WORK_TEXT.write(srt.compose(out_f))
    WORK_TEXT.seek(0)

def FixSubGaps(inlist, mingap):
    """Optimize the gap between subtitles, including fixing overlaps."""
    
    gaps = 0
    overlaps = 0
    new_subtitles = []

    def adjust_subtitle_pair(sub1, sub2):
        """Adjust a pair of subtitles to optimize gaps and fix overlaps."""
        nonlocal gaps
        nonlocal overlaps

        end_1 = mTime(sub1.end)
        start_2 = mTime(sub2.start)
        gap = start_2 - end_1

        # Handle overlap by adjusting start_2
        if start_2 < end_1:
            overlaps += 1
            # Adjust start of the second subtitle to halfway through the overlap
            start_2 = end_1 + (end_1 - start_2) / 2
            sub2 = Subtitle(sub2.index, DT.timedelta(milliseconds=start_2), sub2.end, sub2.content)
        
        # Handle small gaps
        if gap < mingap:
            gaps += 1
            # Calculate adjustments to fill the gap
            adjust_end_1 = end_1 + (gap * 0.7)  # 70% adjustment to sub1 end time
            adjust_start_2 = start_2 - (gap * 0.3)  # 30% adjustment to sub2 start time

            # Ensure adjusted times do not cause overlaps
            if adjust_end_1 >= adjust_start_2:
                adjust_end_1 = (end_1 + start_2) / 2  # Split the difference
                adjust_start_2 = adjust_end_1 + mingap

            # Update subtitle timings
            sub1 = Subtitle(sub1.index, sub1.start, DT.timedelta(milliseconds=adjust_end_1), sub1.content)
            sub2 = Subtitle(sub2.index, DT.timedelta(milliseconds=adjust_start_2), sub2.end, sub2.content)

        return sub1, sub2

    try:
        # Iterate over subtitle pairs
        for i in range(len(inlist) - 1):
            sub1 = inlist[i]
            sub2 = inlist[i + 1]

            # Adjust the pair
            adjusted_sub1, adjusted_sub2 = adjust_subtitle_pair(sub1, sub2)

            # Add the adjusted first subtitle
            if i == 0 or new_subtitles[-1].index != adjusted_sub1.index:  # Avoid duplicates
                new_subtitles.append(adjusted_sub1)
            
            # Update the inlist for the next iteration
            inlist[i + 1] = adjusted_sub2
        
        # Add the last subtitle if not already added
        if new_subtitles[-1].index != inlist[-1].index:
            new_subtitles.append(inlist[-1])

        # Write or return the adjusted subtitles
        WORK_TEXT.truncate(0)
        WORK_TEXT.write(srt.compose(new_subtitles))
        WORK_TEXT.seek(0)

    except Exception as e:
        logger.debug(f"FixGaps: {e}")

    return gaps, overlaps
    
def ShrinkGap(inlist, maxgap, mingap=1):
    """Optimize the gap between subtitles in an .srt file."""

    gaps = 0
    new_subtitles = []

    def adjust_subtitle_pair(sub1, sub2):
        """Adjust a pair of subtitles if they are within the gap limit."""
        nonlocal gaps
        end_1 = mTime(sub1.end)
        start_1 = mTime(sub2.start)
        gap = start_1 - end_1
        difference = gap - mingap

        # Only adjust if the difference is within limits and won't cause overlap
        if 0 < difference <= maxgap:
            gaps += 1

            # Adjust end time of sub1 by 70% of the difference
            new_end_1 = end_1 + 0.7 * difference

            # Adjust start time of sub2 by 30% of the difference
            new_start_2 = start_1 - 0.3 * difference

            # Ensure adjusted times do not cause overlaps
            if new_end_1 >= new_start_2:
                return sub1, sub2  # Skip adjustment if it causes overlap

            sub1 = Subtitle(
                sub1.index,
                sub1.start,
                DT.timedelta(milliseconds=new_end_1),
                sub1.content,
            )
            sub2 = Subtitle(
                sub2.index,
                DT.timedelta(milliseconds=new_start_2),
                sub2.end,
                sub2.content,
            )

        return sub1, sub2

    try:
        # Start with the first subtitle
        i = 0
        while i < len(inlist) - 1:
            sub1 = inlist[i]
            sub2 = inlist[i + 1]

            # Adjust the pair
            adjusted_sub1, adjusted_sub2 = adjust_subtitle_pair(sub1, sub2)

            # Add the adjusted first subtitle
            if i == 0 or new_subtitles[-1] != adjusted_sub1:  # Avoid duplicates
                new_subtitles.append(adjusted_sub1)

            # Update for the next loop iteration
            inlist[i + 1] = adjusted_sub2  # Update the inlist to keep changes

            i += 1

        # Ensure the last subtitle is included
        if len(inlist) > 1:
            new_subtitles.append(inlist[-1])

        # Write the results to the work text
        WORK_TEXT.truncate(0)
        WORK_TEXT.write(srt.compose(new_subtitles))
        WORK_TEXT.seek(0)

    except Exception as e:
        logger.debug(f"ShrinkGap: {e}")

    return gaps
