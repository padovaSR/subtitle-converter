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
from collections import namedtuple
from pydispatch import dispatcher
from choice_dialog import MultiChoice
from errors_check import checkErrors
from File_processing import FileOpened
from text_processing import normalizeText, bufferText
from settings import WORK_TEXT, BYTES_TEXT, PREVIOUS, FILE_HISTORY, filePath, lenZip, droppedText

import codecs
from codecs import BOM_UTF8 

import logging.config

import wx

logger = logging.getLogger(__name__)



def addPrevious(action, enc=None, content=None, psuffix=None, tpath=None, rpath=None):
    '''This function creates namedtuple'''
    prev = namedtuple("prev", ["action", "enc", "content", "psuffix", "tpath", "rpath"])
    PREVIOUS.append(prev(action, enc, content, psuffix, tpath, rpath))


class FileOpened:
    ''''''
    def __init__(self, path, data=None):

        self.path = path
        self.data = data

    def isCompressed(self):

        fileName = os.path.basename(self.path)
        basepath = os.path.dirname(self.path)
        with zipfile.ZipFile(self.path, 'r') as zf:
            if len(zf.namelist()) == 1:
                singleFile = zf.namelist()[0]
                outfile = [os.path.join(basepath, singleFile)]
                with open(outfile[0], 'wb') as f:
                    f.write(zf.read(singleFile))     ## zf.read() returns bytes  ########
                outfile1 = os.path.join(
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
                        names = [os.path.basename(i) for i in files]
                        outfiles = [os.path.join(basepath, x) for x in names]
                        single = os.path.join(
                            os.path.dirname(self.path),
                            os.path.basename(files[-1]),
                        )
                        
                        # for i in files: BYTES_TEXT.append(zf.read(i))
                        return outfiles, [zf.read(x) for x in files]
                    else:
                        logger.debug(f'{self.path}: Canceled.')
                        dlg.Destroy()
                finally:
                    dlg.Destroy()

    @staticmethod
    def fCodeList():
        """"""
        with open(os.path.join('resources', 'var', 'obsE.pkl'), 'rb') as f:
            kodek = pickle.load(f).strip()
                
            if kodek != 'auto':
                ukode = kodek
            else:
                ukode = 'utf-8'

            return [
                ukode,
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
    
    def getByteText(self):
        """"""
        return open(self.path, "rb").read()
        
    
    def findCode(self):
        ''''''
        f = open(self.path, "rb")
        data = f.read(4)
        f.close()
        if data.startswith(BOM_UTF8):
            return "utf-8-sig"
        else:
            for enc in self.fCodeList():
                try:
                    with codecs.open(self.path, 'r', encoding=enc) as fh:
                        fh.readlines()
                        fh.seek(0)
                except:
                    pass
                else:
                    logger.debug(f'{os.path.basename(self.path)}: {enc}')
                    break
            return enc
    
    def findByteCode(self):
        """"""
        dat = self.data
        if dat[:4].startswith(BOM_UTF8):
            return "utf-8-sig"
        else:
            for enc in self.fCodeList():
                try:
                    dat.decode(enc)
                except:
                    pass
                else:
                    logger.debug(f"{os.path.basename(self.path)}: {enc}")
                    break        
            return enc
        
    
class FileHandler(FileOpened):
    def __init__(self, infiles, text_control, fdrop=False):
        FileOpened.__init__(self, path="", data=False)
        
        self.infiles = infiles
        self.text_control = text_control
        self.fdrop = fdrop
        
        
    def fileHandle(self):
        """"""
        infiles = self.infiles
        text_control = self.text_control
        fdrop = self.fdrop
        
        if type(infiles) != list:
            infiles = [infiles]
    
        def file_go(infile):
            self.path = infile
            enc = self.findCode()
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
                        text_control.SetStyle(i[0], i[1], wx.TextAttr("BLUE", "YELLOW"))
                        text_control.SetInsertionPoint(i[1])
            PREVIOUS.clear()
            addPrevious("Open", enc, text, "", infile, infile)
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
            if fdrop is True:
                dispatcher.send("TMP_PATH", message=infiles, msg=[rpath, "", True])
            for i in range(len(infiles)):
                if not zipfile.is_zipfile(infiles[i]):
                    try:
                        if not os.path.exists(infiles[i]):
                            logger.debug(
                                f"FileHandler: Skipping {os.path.basename(infiles[i])}"
                            )
                            text_control.AppendText(
                                f"\n_SKIPP_:{os.path.basename(infiles[i])}"
                            )
                            continue
                        fop = FileOpened(infiles[i])
                        enc = fop.findCode()
                        BYTES_TEXT.append(fop.getByteText())
                        new_d[infiles[i]] = enc
                        name = os.path.basename(infiles[i])
                        text_control.AppendText("\n")
                        text_control.AppendText(name)
                    except Exception as e:
                        logger.debug(f'FileHandler: {e}')                
                else:
                    try:
                        fop = FileOpened(infiles[i])
                        outfile, rfile = fop.isCompressed()
                    except:
                        logger.debug('FileHandler: No files selected.')
                    else:
                        if len(outfile) == 1:
                            fop = FileOpened(outfile[0], BYTES_TEXT[0])
                            print(outfile[0])
                            enc = fop.findByteCode()
                            nam = outfile[0]
                            new_d[nam] = enc
                            text = os.path.basename(nam)
                            text_control.AppendText("\n")
                            text_control.AppendText(text)
                        elif len(outfile) > 1:
                            for i in range(len(outfile)):
                                fop = FileOpened(outfile[i], BYTES_TEXT[i])
                                enc = fop.findByteCode()
                                new_d[outfile[i]] = enc
                                text = os.path.basename(outfile[i])
                                text_control.AppendText("\n")
                                text_control.AppendText(text)
            logger.debug('FileHandler: Ready for multiple files.')
            PREVIOUS.append(new_d)
            if fdrop is True:
                dispatcher.send("droped", msg=new_d)
        else:
            name = "".join(infiles)
            if zipfile.is_zipfile(name):
                logger.debug(f'ZIP archive: {os.path.basename(name)}')
                try:
                    self.path = name
                    outfile, byteList = self.isCompressed()  ## outfile in tmp
                except Exception as e:
                    logger.debug(f'ZIP; {e}.')
                else:
                    if len(outfile) == 1:
                        if lenZip(name):
                            ## Append if not multiple
                            FILE_HISTORY.append(lenZip(name))
                        enc = file_go(outfile[0])
                        nam = [outfile[0]]
                        empty = {}
                        if fdrop is True:
                            dispatcher.send(
                                "TMP_PATH", message=outfile, msg=[rfile, enc, False]
                            )
                            dispatcher.send("droped", msg=empty)
                    elif len(outfile) > 1:
                        text_control.SetValue('Files List:\n')
                        new_d = {}
                        for i in range(len(outfile)):
                            # fop = FileOpened(outfile[i])
                            self.path = outfile[i]
                            self.data = byteList[i]
                            enc = self.findByteCode()
                            new_d[outfile[i]] = enc
                            text = os.path.basename(outfile[i])
                            text_control.AppendText("\n")
                            text_control.AppendText(text)
                        PREVIOUS.append(new_d)
                        if fdrop is True:
                            dispatcher.send(
                                "TMP_PATH", message=outfile, msg=[rfile, enc, True]
                            )
                            dispatcher.send("droped", msg=new_d)
                        logger.debug('FileHandler: Ready for multiple files.')
            elif not zipfile.is_zipfile(name):
                ## name = real path
                FILE_HISTORY.append(name)
                #tmp_path = filePath('tmp', os.path.basename(name))
                #if os.path.isfile(tmp_path):
                    #os.remove(tmp_path)
                #shutil.copy(name, tmp_path)
                enc = file_go(name, name)
                empty = {}
                if fdrop is True:
                    dispatcher.send("droped", msg=empty)
                    dispatcher.send("TMP_PATH", message=tmp_path, msg=[name, enc, False])    





