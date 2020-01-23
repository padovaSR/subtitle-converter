#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  Copyright (C) 2019  padovaSR
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

import os
import pickle
import shelve
import zipfile
import shutil
import logging
from pydispatch import dispatcher

from settings import filePath, WORK_TEXT, WORK_SUBS, ENT_ENCODING
from FileProcessing import FileProcessed, FileOpened

import wx


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(
    filename=filePath("resources", "var", "file_drop.log"), mode="w", encoding="utf-8"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        lfiles = [x for x in filenames]
        rpath = ''
        enc = ''
        droped = 0

        def file_go(infile, rfile):
            fop = FileOpened(infile)
            enc = fop.findCode()
            fproc = FileProcessed(enc, infile)
            text = fproc.normalizeText()
            fproc.bufferText(text, WORK_TEXT)
            fproc.bufferText(text, WORK_SUBS)
            logger.debug(f"FileDrop: {os.path.basename(infile)}")
            self.window.SetValue(text)
            return enc, text

        if len(lfiles) > 1:
            new_d = {}
            rpath = [lfiles[-1]]
            self.window.SetValue('Files List:\n')
            dispatcher.send("TMP_PATH", message=lfiles, msg=[rpath, enc, True])
            for i in range(len(lfiles)):
                if not zipfile.is_zipfile(lfiles[i]):
                    try:
                        tmp_path = filePath('tmp', os.path.basename(lfiles[i]))
                        if lfiles[i].endswith(
                            ('zip', 'srt', 'txt', 'ZIP', 'SRT', 'TXT')
                        ):
                            shutil.copy(lfiles[i], tmp_path)
                    except:
                        logger.debug('FileDrop: Unexpected file type.')
                    else:
                        fop = FileOpened(tmp_path)
                        enc = fop.findCode()
                        fproc = FileProcessed(enc, tmp_path)
                        fproc.normalizeText()
                        new_d[tmp_path] = enc
                        name = os.path.basename(tmp_path)
                        self.window.AppendText("\n")
                        self.window.AppendText(name)
                else:
                    try:
                        fop = FileOpened(lfiles[i])
                        outfile, rfile = fop.isCompressed()
                        rpath = rfile
                    except:
                        logger.debug('FileDrop: No files selected.')
                    else:
                        if len(outfile) == 1:
                            fop = FileOpened(outfile[0])
                            enc = fop.findCode()
                            fproc = FileProcessed(enc, outfile[0])
                            fproc.normalizeText()
                            nam = outfile[0]
                            droped += 1
                            new_d[nam] = enc
                            text = os.path.basename(nam)
                            self.window.AppendText("\n")
                            self.window.AppendText(text)
                        elif len(outfile) > 1:
                            droped += 1
                            for i in range(len(outfile)):
                                fop = FileOpened(outfile[i])
                                enc = fop.findCode()
                                fproc = FileProcessed(enc, outfile[i])
                                fproc.normalizeText()
                                new_d[outfile[i]] = enc
                                text = os.path.basename(outfile[i])
                                self.window.AppendText("\n")
                                self.window.AppendText(text)
            logger.debug('FileDrop: Ready for multiple files.')
            dispatcher.send("droped", msg=new_d)
        else:
            name = "".join(lfiles)
            if zipfile.is_zipfile(name) == True:
                logger.debug(f'ZIP archive: {os.path.basename(name)}')
                try:
                    fop = FileOpened(name)
                    outfile, rfile = fop.isCompressed()
                    rpath = [rfile]
                except:
                    logger.debug('No files selected.')

                else:
                    if len(outfile) == 1:
                        enc, t = file_go(outfile[0], rfile)
                        nam = [outfile[0]]
                        droped += 1
                        empty = {}
                        self.window.SetValue(t)
                        dispatcher.send(
                            "TMP_PATH", message=outfile, msg=[rpath, enc, False]
                        )
                        dispatcher.send("droped", msg=empty)
                    elif len(outfile) > 1:
                        droped += 1
                        self.window.SetValue('Files List:\n')
                        new_d = {}
                        for i in range(len(outfile)):
                            fop = FileOpened(outfile[i])
                            enc = fop.findCode()
                            fproc = FileProcessed(enc, outfile[i])
                            fproc.normalizeText()
                            new_d[outfile[i]] = enc
                            text = os.path.basename(outfile[i])
                            self.window.AppendText("\n")
                            self.window.AppendText(text)
                        dispatcher.send(
                            "TMP_PATH", message=outfile, msg=[rpath, enc, True]
                        )
                        dispatcher.send("droped", msg=new_d)
                        logger.debug('FileDrop: Ready for multiple files.')
            elif zipfile.is_zipfile(name) == False:
                tmp_path = [filePath('tmp', os.path.basename(name))]
                shutil.copy(name, tmp_path[-1])
                enc, txt1 = file_go(tmp_path[-1], name)
                rpath = [name]
                droped += 1
                empty = {}
                self.window.SetValue(txt1)
                dispatcher.send("droped", msg=empty)
                dispatcher.send("TMP_PATH", message=tmp_path, msg=[rpath, enc, False])

        return True
