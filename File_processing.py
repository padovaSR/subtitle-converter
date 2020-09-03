#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import codecs
import re
import zipfile
import pickle
from collections import namedtuple 
from text_processing import codelist
from choice_dialog import MultiChoice
from settings import chreg, FILE_SETTINGS, BYTES_TEXT, name_data
import logging.config

from codecs import BOM_UTF8

import wx

logger = logging.getLogger(__name__)


class FileOpened:
    ''''''
    internal = []
    internPath = []
    internEnc = ""
    
    def __init__(self, path, multi=False):

        self.path = path
        self.multi = multi

    def isCompressed(self):

        basepath = 'tmp'
        # basepath = os.path.dirname(self.path)
        fileName = os.path.basename(self.path)
        
        with zipfile.ZipFile(self.path, 'r') as zf:
            if len(zf.namelist()) == 1:
                singleFile = zf.namelist()[0]
                outfile = [os.path.join(basepath, singleFile)]
                if self.multi == False:
                    with open(outfile[0], 'wb') as f:
                        f.write(zf.read(singleFile))     ## zf.read() => bytes  ##
                else: self.internal.append(zf.read(singleFile).replace(b"\r\n", b"\n"))
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
        return open(self.path, "rb").read().replace(b"\r\n", b"\n")
        
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
            self.internEnc = enc
            return enc
    
    def findByteCode(self, n=0):
        """"""
        dat = self.internal[n]
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
            self.internEnc = enc
            return enc
    
    @staticmethod
    def addBytes(path, enc, content):
        """"""
        multi = namedtuple("multi", ["path","enc", "content"])
        BYTES_TEXT.append(multi(path, enc, content))
        

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

    fprint = os.path.basename(path)

    n = os.path.splitext(fprint)[0]

    if not "" in list(ex.values()):
        psufix = os.path.splitext(n)[-1]  ## presufix ispred sufixa
    else:
        psufix = n

    if oformat == "txt" and pre_suffix == value5_s:
        sufix = ".txt"
    elif oformat == "txt" and pre_suffix == value2_s:
        sufix = ".txt"
    else:
        sufix = os.path.splitext(path)[-1]  ## srt,txt ili neki drugi otvoren

    suffix_list = ["." + x if not x.startswith("_") else x for x in ex.values()] + added
    suffix_list.append(value_m)
    suffix_list = [x.strip(".") if x.startswith(r".(") else x for x in suffix_list]

    _d = "." + pre_suffix  ## pre_suffix je unet u funkciji koja poziva newName
    if pre_suffix.startswith("_") or pre_suffix.startswith(r"("):
        _d = pre_suffix

    if psufix in suffix_list:
        name1 = '{0}{1}'.format(os.path.splitext(n)[0], _d)  ## fajl u tmp/ folderu
    else:
        name1 = '{0}{1}'.format(n, _d)

    if name1.endswith("."):
        name1 = name1[:-1]

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

    presuffix_l = os.path.join("resources", "var", "presuffix_list.bak")
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
        nameO = '{0}{1}'.format(os.path.join(real_dir, name), sufix)
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
    if multi == False:
        if os.path.isfile(path) and os.path.dirname(path) != "tmp" and ask == True:
            dlg = wx.MessageBox(
                f"{os.path.basename(path)}\nFile already exists! Proceed?",
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
