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
import zipfile
import pickle
import shutil
from collections import namedtuple
from pydispatch import dispatcher
from errors_check import checkErrors
from File_processing import FileOpened
from text_processing import normalizeText, bufferText
from settings import WORK_TEXT, PREVIOUS, FILE_HISTORY, filePath, lenZip, droppedText

import logging.config

import wx

logger = logging.getLogger(__name__)


def addPrevious(action, enc=None, content=None, psuffix=None, tpath=None, rpath=None):
    '''This function creates namedtuple'''
    prev = namedtuple("prev", ["action", "enc", "content", "psuffix", "tpath", "rpath"])
    PREVIOUS.append(prev(action, enc, content, psuffix, tpath, rpath))


def fileHandle(infiles, text_control, fdrop=False):
    """"""

    if type(infiles) != list:
        infiles = [infiles]

    def file_go(infile, rfile):
        fop = FileOpened(infile)
        enc = fop.findCode()
        text = normalizeText(enc, infile)
        text = text.replace("\r\n", "\n")
        bufferText(text, WORK_TEXT)
        text = WORK_TEXT.getvalue()
        nlist = checkErrors(text)
        text_control.SetValue(text)
        text_control.SetInsertionPoint(0)
        if fdrop == False:
            if nlist:
                for i in nlist:
                    text_control.SetStyle(i[0], i[1], wx.TextAttr("BLUE", "YELLOW"))
                    text_control.SetInsertionPoint(i[1])
        PREVIOUS.clear()
        addPrevious("Open", enc, text, "", infile, rfile)
        logger.debug(f"Opened: {os.path.basename(infile)}, {enc}")
        if os.path.exists(droppedText):
            os.remove(droppedText)
        d_text = {text: enc}
        with open(filePath('resources', 'var', 'r_text0.pkl'), 'wb') as t:
            pickle.dump(d_text, t)

        return enc

    if len(infiles) > 1:
        new_d = {}
        rpath = [infiles[-1]]
        text_control.SetValue('Files List:\n')
        if fdrop == True:
            dispatcher.send("TMP_PATH", message=infiles, msg=[rpath, "", True])
        for i in range(len(infiles)):
            if not zipfile.is_zipfile(infiles[i]):
                try:
                    name, suffix = os.path.splitext(infiles[i])
                    tmp_path = filePath('tmp', os.path.basename(name) + suffix.lower())
                    if tmp_path.endswith(
                        (
                            'zip',
                            'srt',
                            'txt',
                            'log',
                            'sub',
                            'dll',
                        )
                    ):
                        shutil.copy(infiles[i], tmp_path)
                except Exception as e:
                    logger.debug(f'FileHandler: {e}')
                else:
                    if not os.path.exists(tmp_path):
                        logger.debug(
                            f"FileHandler: Skipping {os.path.basename(tmp_path)}"
                        )
                        text_control.AppendText(
                            f"\n_SKIPP_:{os.path.basename(tmp_path)}"
                        )
                        continue
                    fop = FileOpened(tmp_path)
                    enc = fop.findCode()
                    normalizeText(enc, tmp_path)
                    new_d[tmp_path] = enc
                    name = os.path.basename(tmp_path)
                    text_control.AppendText("\n")
                    text_control.AppendText(name)
            else:
                try:
                    fop = FileOpened(infiles[i])
                    outfile, rfile = fop.isCompressed()
                except:
                    logger.debug('FileHandler: No files selected.')
                else:
                    if len(outfile) == 1:
                        fop = FileOpened(outfile[0])
                        enc = fop.findCode()
                        normalizeText(enc, outfile[0])
                        nam = outfile[0]
                        new_d[nam] = enc
                        text = os.path.basename(nam)
                        text_control.AppendText("\n")
                        text_control.AppendText(text)
                    elif len(outfile) > 1:
                        for i in range(len(outfile)):
                            fop = FileOpened(outfile[i])
                            enc = fop.findCode()
                            normalizeText(enc, outfile[i])
                            new_d[outfile[i]] = enc
                            text = os.path.basename(outfile[i])
                            text_control.AppendText("\n")
                            text_control.AppendText(text)
        logger.debug('FileHandler: Ready for multiple files.')
        PREVIOUS.append(new_d)
        if fdrop == True:
            dispatcher.send("droped", msg=new_d)
    else:
        name = "".join(infiles)
        if zipfile.is_zipfile(name):
            logger.debug(f'ZIP archive: {os.path.basename(name)}')
            try:
                fop = FileOpened(name)
                outfile, rfile = fop.isCompressed()  ## outfile in tmp
            except Exception as e:
                logger.debug(f'ZIP; {e}.')
            else:
                if len(outfile) == 1:
                    if lenZip(name):
                        ## Append if not multiple
                        FILE_HISTORY.append(lenZip(name))
                    enc = file_go(outfile[0], rfile)
                    nam = [outfile[0]]
                    empty = {}
                    if fdrop == True:
                        dispatcher.send(
                            "TMP_PATH", message=outfile, msg=[rfile, enc, False]
                        )
                        dispatcher.send("droped", msg=empty)
                elif len(outfile) > 1:
                    text_control.SetValue('Files List:\n')
                    new_d = {}
                    for i in range(len(outfile)):
                        fop = FileOpened(outfile[i])
                        enc = fop.findCode()
                        normalizeText(enc, outfile[i])
                        new_d[outfile[i]] = enc
                        text = os.path.basename(outfile[i])
                        text_control.AppendText("\n")
                        text_control.AppendText(text)
                    PREVIOUS.append(new_d)
                    if fdrop == True:
                        dispatcher.send(
                            "TMP_PATH", message=outfile, msg=[rfile, enc, True]
                        )
                        dispatcher.send("droped", msg=new_d)
                    logger.debug('FileHandler: Ready for multiple files.')
        elif not zipfile.is_zipfile(name):
            ## name = real path
            FILE_HISTORY.append(name)
            tmp_path = filePath('tmp', os.path.basename(name))
            if os.path.isfile(tmp_path):
                os.remove(tmp_path)
            shutil.copy(name, tmp_path)
            enc = file_go(tmp_path, name)
            empty = {}
            if fdrop == True:
                dispatcher.send("droped", msg=empty)
                dispatcher.send("TMP_PATH", message=tmp_path, msg=[name, enc, False])
