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
import os
import srt
import webbrowser
import pickle
import logging.config

logger = logging.getLogger(__name__)


def showMeError(infile, in_text, outfile, kode):

    with open(os.path.join('resources', 'var', 'fixer_cb3.data'), 'rb') as f:
        cb3_s = pickle.load(f)

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
