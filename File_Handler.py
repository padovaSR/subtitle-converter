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
#

import os
from os.path import basename as baseName
import pickle
import shutil
import zipfile
from collections import namedtuple
from pydispatch import dispatcher
from errors_check import checkErrors
from File_processing import FileOpened
from text_processing import normalizeText, bufferText
from settings import WORK_TEXT, PREVIOUS, FILE_HISTORY, BYTES_TEXT, filePath, lenZip, droppedText
import logging.config

import wx

logger = logging.getLogger(__name__)


def addPrevious(action, enc=None, content=None, psuffix=None, tpath=None, rpath=None):
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
        text = normalizeText(enc, infile)
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
