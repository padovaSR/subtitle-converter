#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import codecs
import re
import zipfile
import pickle
import shelve
import logging
from text_processing import codelist
from settings import chreg, preSuffix
from choice_dialog import MultiChoice
from codecs import BOM_UTF8

import wx


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(
    filename=os.path.join("resources", "var", "log","FileProcessing.log"),
    mode="a",
    encoding="utf-8",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

class FileOpened:
    ''''''
    def __init__(self, path):

        self.putanja = path

    def isCompressed(self):

        basepath = 'tmp'
        imeFajla = os.path.basename(self.putanja)

        with zipfile.ZipFile(self.putanja, 'r') as zf:
            if len(zf.namelist()) == 1:
                jedanFajl = zf.namelist()[0]
                outfile = [os.path.join(basepath, jedanFajl)]
                with open(outfile[0], 'wb') as f:
                    f.write(zf.read(jedanFajl))
                outfile1 = os.path.join(
                    os.path.dirname(self.putanja), jedanFajl
                )
                return outfile, outfile1
            elif not zf.namelist():
                logger.debug(f"{imeFajla} is empty")
            elif len(zf.namelist()) >= 2:
                izbor = [x for x in zf.namelist() if not x.endswith('/')]
                if len(zf.namelist()) > 9:
                    dlg = MultiChoice(None, "Pick files:", imeFajla, choices=izbor)
                else:
                    dlg = wx.MultiChoiceDialog(None, 'Pick files:', imeFajla, izbor)
                try:
                    if dlg.ShowModal() == wx.ID_OK:
                        response = dlg.GetSelections()
                        files = [izbor[x] for x in response]
                        names = [os.path.basename(i) for i in files]
                        outfiles = [os.path.join(basepath, x) for x in names]
                        single = os.path.join(
                            os.path.dirname(self.putanja),
                            os.path.basename(files[-1]),
                        )
                        for i, x in zip(files, outfiles):
                            with open(x, 'wb') as f:
                                f.write(zf.read(i))
                        return outfiles, single
                    else:
                        logger.debug(f'{self.putanja}: Canceled.')
                        dlg.Destroy()
                finally:
                    dlg.Destroy()

    def findCode(self):
        ''''''
        with open(os.path.join('resources', 'var', 'obsE.pkl'), 'rb') as f:
            kodek = pickle.load(f).strip()        
        
        f = open(self.putanja, "rb")
        data = f.read(4)
        f.close()
        if data.startswith(BOM_UTF8):
            return "utf-8-sig"
        else:        
            if kodek != 'auto':
                ukode = kodek
            else:
                ukode = 'utf-8'
    
            kodiranja = [
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
            for enc in kodiranja:
                try:
                    with codecs.open(self.putanja, 'r', encoding=enc) as fh:
                        fh.readlines()
                        fh.seek(0)
                except:
                    pass
                else:
                    logger.debug(
                        f' {os.path.basename(self.putanja)}, encoding: {enc}'
                    )
                    break
    
            return enc

def newName(path, pre_suffix, multi):
    ''''''
    added, ex, value2_s, value5_s, value_m, oformat = preSuffix()
    
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
        psufix = os.path.splitext(n)[-1]  # presufix ispred sufixa
    else:
        psufix = n

    if oformat == "txt" and pre_suffix == value5_s:
        sufix = ".txt"
    elif oformat == "txt" and pre_suffix == value2_s:
        sufix = ".txt"
    else:
        sufix = os.path.splitext(path)[
            -1
        ]  # srt,txt ili neki drugi koji je otvoren

    suffix_list = [
        "." + x if not x.startswith("_") else x for x in ex.values()
    ] + added
    suffix_list.append(value_m)
    suffix_list = [
        x.strip(".") if x.startswith(r".(") else x for x in suffix_list
    ]

    _d = (
        "." + pre_suffix
    )  # pre_suffix je unet u funkciji koja poziva newName
    if pre_suffix.startswith("_") or pre_suffix.startswith(r"("):
        _d = pre_suffix

    if psufix in suffix_list:
        name1 = '{0}{1}'.format(
            os.path.splitext(n)[0], _d
        )  # fajl u tmp/ folderu
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
    # print(name1, sufix)
    return name1, sufix  # Vraca samo ime fajla bez putanje

def nameDialog(name_entry, sufix_entry, dir_entry):

    with shelve.open(
        os.path.join("resources", "var", "dialog_settings.db"),
        flag='writeback',
    ) as sp:
        ex = sp['key5']

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
                presuffix_x = (
                    os.path.splitext(os.path.splitext(nameO)[0])[-1]
                    + "\n"
                )
                if "_" in presuffix_x:
                    presuffix_ = "_" + presuffix_x.split("_")[-1] + "\n"
                else:
                    presuffix_ = ""
            else:
                presuffix_x = ""
                presuffix_ = (
                    os.path.splitext(os.path.splitext(nameO)[0])[-1]
                    + "\n"
                )
            f.write(presuffix_)
        return nameO
    else:
        dlg.Destroy()
        return None

def writeToFile(text, path, enc, multi):
    
    if enc in codelist:
        error = 'surrogatepass'
    else:
        error = 'replace'
    if multi ==False:
        if os.path.isfile(path) and os.path.dirname(path) != "tmp":
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
            logger.debug(f"Write file: {path}; {enc}")
        return True
    except IOError as e:
        logger.debug(f"changeEncoding IOError: {e}")
    except AttributeError as e:
        logger.debug(f"changeEncoding, AttributeError: {e}")
    except UnicodeEncodeError as e:
        logger.debug(f"changeEncoding, UnicodeEncodeError: {e}")
    except UnicodeDecodeError as e:
        logger.debug(f"changeEncoding, UnicodeDecodeError: {e}")
    except LookupError as e:
        logger.debug(f"changeEncoding, LookupError: {e}")
    except Exception as e:
        logger.debug(f"changeEncoding, Unexpected error: {e}")
