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
import sys
import logging
import traceback
import pickle
import shelve
import zipfile

import codecs
import re
import unicodedata
import tempfile
import fnmatch
from io import StringIO
from textwrap import TextWrapper
import pysrt
import srt
from pydispatch import dispatcher

from zamenaImena import (
    dictionary_0,
    dictionary_1,
    dictionary_2,
    rplSmap,
    searchReplc,
    dict0_n,
    dict0_n2,
    dict1_n,
    dict1_n2,
    dict2_n,
    dict2_n2,
    lat_cir_mapa,
    pLatin_rpl,
    pre_cyr,
)

from settings import filePath

import wx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(
    filename=os.path.join("resources", "var", "FileProcessing.log"),
    mode="w",
    encoding="utf-8",
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def bufferCode(intext, outcode):

    codelist = [
        'utf-8',
        'utf-8-sig',
        'utf-16',
        'utf-32',
        'utf-16-be',
        'utf-16-le',
        'utf-32-be',
        'utf-32-le',
    ]
    if outcode in codelist:
        error = "surrogatepass"
    else:
        error = "replace"
    try:
        b_text = intext.encode(encoding=outcode, errors=error)
        s_text = b_text.decode(encoding=outcode, errors=error)
        logger.debug(f"bufferCode to encoding: {outcode}")
    except Exception as e:
        logger.debug(f"BufferCode error: {e}, intext: {type(intext)}")
        return intext
    else:
        return s_text


def writeTempStr(inFile, text, kode):
    _error = 'strict'
    codelist = [
        'utf-8',
        'utf-16',
        'utf-32',
        'utf-16-be',
        'utf-16-le',
        'utf-32-be',
        'utf-32-le',
    ]
    if kode in codelist:
        _error = 'surrogatepass'
    try:
        with tempfile.TemporaryFile() as tfile:
            tfile.write(text.encode(encoding=kode, errors=_error))
            tfile.seek(0)
            content = tfile.read()
            with open(inFile, 'wb') as out:
                out.write(content)
    except IOError as e:
        logger.debug("WriteTempStr, I/O error({0}): {1}".format(e.errno, e.strerror))
    except AttributeError as e:
        logger.debug(f"writeTempStr AttributeError: {e}")
    except UnicodeEncodeError as e:
        logger.debug(f"WriteTempStr, UnicodeEncodeError: {e}")
    except UnicodeDecodeError as e:
        logger.debug(f"WriteTempStr, UnicodeDecodeError: {e}")
    except Exception:
        logger.debug(f"WriteTempStr, unexpected error: {traceback.format_exc}")


class FileOpened:
    def __init__(self, path):

        self.putanja = path

    def isCompressed(self):

        basepath = 'tmp'
        imeFajla = os.path.basename(self.putanja)

        with zipfile.ZipFile(self.putanja, 'r') as zf:
            singlefajl = len(zf.namelist())
            if singlefajl == 1:
                jedanFajl = zf.namelist()[0]
                outfile = [os.path.join(basepath, jedanFajl)]
                with open(outfile[0], 'wb') as f:
                    f.write(zf.read(jedanFajl))
                outfile1 = os.path.join(os.path.dirname(self.putanja), jedanFajl)
                return outfile, outfile1
            elif singlefajl >= 2:
                izbor = [x for x in zf.namelist() if not x.endswith('/')]
                dlg = wx.MultiChoiceDialog(None, 'Pick files:', imeFajla, izbor)
                if dlg.ShowModal() == wx.ID_OK:
                    response = dlg.GetSelections()
                    files = [izbor[x] for x in response]
                    names = [os.path.basename(i) for i in files]
                    outfiles = [os.path.join(basepath, x) for x in names]
                    single = os.path.join(
                        os.path.dirname(self.putanja), os.path.basename(files[-1])
                    )
                    for i, x in zip(files, outfiles):
                        with open(x, 'wb') as f:
                            f.write(zf.read(i))
                    return outfiles, single
                else:
                    logger.debug(f'{self.putanja}: Canceled.')

    def findCode(self):

        with open(os.path.join('resources', 'var', 'obsE.pkl'), 'rb') as f:
            kodek = pickle.load(f).strip()
        if kodek != 'auto':
            ukode = kodek
        else:
            ukode = 'utf-8-sig'

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
                logger.debug(f' {os.path.basename(self.putanja)}, encoding: {enc}')
                break

        return enc


class FileProcessed:

    work_text = StringIO()

    def __init__(self, enc, path):
        self.kode = enc
        self.putanja = path

    @staticmethod
    def nameCheck(name_pattern, where, suffix):
        pattern = name_pattern + "*" + suffix
        files = os.listdir(where)
        n_names = len(fnmatch.filter(files, pattern))  # + 1
        return n_names

    @staticmethod
    def bufferText(intext, buffer):

        buffer.truncate(0)
        buffer.seek(0)
        buffer.write(intext)
        buffer.seek(0)

    def normalizeText(self):
        error = 'strict'
        codelist = [
            'utf-8',
            'utf-16',
            'utf-32',
            'utf-16-be',
            'utf-16-le',
            'utf-32-be',
            'utf-32-le',
        ]
        if self.kode in codelist:
            error = 'surrogatepass'
        try:
            with open(
                self.putanja, 'r', encoding=self.kode, errors=error
            ) as f:  # , encoding=enc) as f:
                ucitan = f.read()
                text_normalized = unicodedata.normalize('NFKC', ucitan)  # rw)
        except IOError as e:
            logger.exception(f"NormalizeText, I/O error: ({self.putanja}{e})")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))

        else:
            try:
                self.bufferText(text_normalized, self.work_text)
                text = self.work_text.getvalue()
                return text
            except Exception as e:
                logger.debug(f"NormalizeText Error: ({e})")
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                logger.debug(''.join('!' + line for line in lines))

    def getContent(self, in_buffer):
        if in_buffer == None:
            in_buffer = self.work_text
        try:
            text = in_buffer.getvalue()
            return text
        except IOError as e:
            logger.debug(f"GetContent IOError: {e}")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))

    @staticmethod
    def checkErrors(text_in):

        fpaterns = '|'.join(
            [
                'ï»¿Å',
                'Ä',
                'Å½',
                'Ä',
                'Ä',
                'Å¡',
                'Ä',
                'Å¾',
                'Ä',
                'Ä',
                "ď»ż",
                "Ĺ˝",
                'Ĺ ',
                'ĹĄ',
                'Ĺž',
                'Ä',
                'Å ',
                'Ä‡',
                'Ä¿',
                'Ä²',
                'Ä³',
                'Å¿',
                'Ã¢â',
                "�",
                "Д†",
                "Д‡",
                "Ť",
                "Lˇ",
                "ï»¿",
                "ð",
            ]
        )

        MOJIBAKE_SYMBOL_RE = re.compile(
            '[ÂÃĂ][\x80-\x9f€ƒ‚„†‡ˆ‰‹Œ“•˜œŸ¡¢£¤¥¦§¨ª«¬¯°±²³µ¶·¸¹º¼½¾¿ˇ˘˝]|'
            r'[ÂÃĂ][›»‘”©™]\w|'
            '[¬√][ÄÅÇÉÑÖÜáàâäãåçéèêëíìîïñúùûü†¢£§¶ß®©™≠ÆØ¥ªæø≤≥]|'
            r'\w√[±∂]\w|'
            '[ðđ][Ÿ\x9f]|'
            'â€|ï»|'
            'вЂ[љћ¦°№™ќ“”]' + fpaterns
        )

        text = text_in
        l1 = []
        l2 = []
        try:
            for match in re.finditer(MOJIBAKE_SYMBOL_RE, text):
                begin = match.start()
                end = match.end()
                l1.append(begin)
                l2.append(end)
            f_list = [(x, y) for x, y in zip(l1, l2)]
            return f_list
        except IOError as e:
            logger.debug("CheckErrors IOError({0}{1}):".format(self.putanja, e))
            return []
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
            return []

    @staticmethod
    def checkFile(file1, file2, text_s, multi):
        file1_name = file1
        try:
            n_sign = text_s.count("?")
            if n_sign > 0:
                poruka = u'!! Greška u tekstu !!\n{0}\nNeispravnih znakova\
                konvertovanih kao znak `?` ukupno: [{1} ]'.format(
                    os.path.basename(file1_name), n_sign
                )

                name = ''
                logger.debug(poruka)
                if multi == True:
                    name = file2
                error_text = "Greška:\n\n{0}\nBilo je neispravnih znakova u\
                tekstu\nkonvertovanih kao znak `?`\nUkupno: [{1}]\nProverite\
                tekst.".format(
                    os.path.basename(name), n_sign
                )

                return error_text
        except UnboundLocalError as e:
            logger.debug(f"File_Check, error({e})")
        except IOError as e:
            logger.debug(f"FileCheck IOError({e.errno} {e.strerror})")
        except Exception as e:  # handle other exceptions such as attribute errors
            logger.debug(f"File_Check, unexpected error: {e}")

    @staticmethod
    def checkChars(text):
        def percentage(part, whole):
            try:
                return int(100 * part / whole)
            except ZeroDivisionError:
                logger.debug('FileCheck Error, file is empty')
                return 0

        def chars(*args):
            return [chr(i) for a in args for i in range(ord(a[0]), ord(a[1]) + 1)]

        slova = "".join(chars("\u0400\u04ff"))

        x = text
        st_pattern = re.compile(r"[A-Za-z\u0400-\u04FF]", re.U)

        try:
            rx = "".join(re.findall(st_pattern, x))
        except IOError as e:
            logger.debug(f"CheckChars, I/O error ({e.errno}): {e.strerror}")

        im = []
        for i in rx:
            FP = re.compile(i)
            try:
                if re.search(FP, slova):
                    im.append(i)
            except ValueError as e:
                logger.debug(f"Value error: {e},{i}")

        statistic = {}
        for x in im:
            if x in rx:
                num = rx.count(x)
                statistic[x] = num

        all_values = sum(statistic.values())
        procenat = percentage(all_values, len(rx))

        return all_values, procenat, list(set(im))

    def newName(self, pre_suffix, multi):

        path = self.putanja
        presuffix_l = os.path.join("resources", "var", "presuffix_list.bak")

        with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
            ex = pickle.load(f)
            value2_s = ex['cyr_utf8_txt']
            value5_s = ex['lat_utf8_srt']

        with open(os.path.join("resources", "var", "m_extensions.pkl"), "rb") as f:
            value_m = pickle.load(f)  #  Merger suffix

        with open(os.path.join('resources', 'var', 'tcf.pkl'), 'rb') as tf:
            oformat = pickle.load(tf)  # TXT suffix

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
            sufix = os.path.splitext(path)[-1]  # srt,txt ili neki drugi koji je otvoren

        if not os.path.exists(presuffix_l):
            open(presuffix_l, "a").close()

        with open(presuffix_l, 'r', encoding='utf-8') as l_file:
            added = [line.strip("\n") for line in l_file if line]

        suffix_list = [
            "." + x if not x.startswith("_") else x for x in ex.values()
        ] + added
        suffix_list.append(value_m)
        suffix_list = [x.strip(".") if x.startswith(r".(") else x for x in suffix_list]

        _d = "." + pre_suffix  # pre_suffix je unet u funkciji koja poziva newName
        if pre_suffix.startswith("_") or pre_suffix.startswith(r"("):
            _d = pre_suffix

        if psufix in suffix_list:
            name1 = '{0}{1}'.format(os.path.splitext(n)[0], _d)  # fajl u tmp/ folderu
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

        return name1, sufix  # Vraca samo ime fajla bez putanje

    @staticmethod
    def nameDialog(name_entry, sufix_entry, dir_entry):

        with shelve.open(
            os.path.join("resources", "var", "dialog_settings.db"), flag='writeback'
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
            tmpnameO = os.path.join(real_dir, name)
            nameO = '{0}{1}'.format(os.path.join(real_dir, name), sufix)
            if nameO.endswith("."):
                nameO = nameO[:-1]
            if os.path.exists(nameO):
                nnm = FileProcessed.nameCheck(name, real_dir, sufix)
                nameO = '{0}_{1}{2}'.format(tmpnameO, nnm, sufix)
            dlg.Destroy()
            with open(presuffix_l, 'a', encoding='utf-8') as f:
                if not '' in list(ex.values()):
                    presuffix_x = (
                        os.path.splitext(os.path.splitext(nameO)[0])[-1] + "\n"
                    )
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

    def rplStr(self, in_text):

        # Rečnik je 'rplSmap'. Lista ključeva(keys) je 'rplsList'.
        p = in_text
        n_pattern = re.compile("|".join(list(rplSmap.keys())))
        nf = n_pattern.findall(p)

        logger.debug('\nSpecijalnih znakova ukupno: [{0}]'.format(len(nf)))
        if len(nf) > 0:
            logger.debug(f'SpecChars: {" ".join(nf)}\n')
            f_path = re.sub(r"\.TEMP_\w*", "", os.path.basename(self.putanja), re.I)
            msginfo = wx.MessageDialog(
                None,
                f'Specijalni znakovi:\n\n{os.path.basename(f_path)}\n\n{", ".join(set(nf))}.',
                'SubConverter',
                wx.OK | wx.ICON_INFORMATION,
            )
            msginfo.ShowModal()

        for key, value in rplSmap.items():
            p = p.replace(key, value)  # !!! Svuda treba da bude p "p=p.replace"!!!

        # Dodatni replace u binarnom formatu:
        # \xe2\x96\xa0 = ■, xc2\xad = SOFT HYPHEN, \xef\xbb\xbf = bom utf-8, \xe2\x80\x91 = NON-BREAKING HYPHEN

        try:
            p = p.encode(self.kode)
            logger.debug(f"■ rplStr, string encode to: {self.kode}")
        except Exception as e:
            logger.debug(f"rplStr encode error: {e}")

        mp = (
            p.replace(b'\xc2\xad', b'')
            .replace(b'\xd0\x94\xc4', b'D')
            .replace(b"\xc4\x8f\xc2\xbb\xc5\xbc", b"")
            .replace(b'\xe2\x80\x91', b'')
            .replace(b'\xc3\x83\xc2\xba', b'u')
            .replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94')
            .replace(b'\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94')
            .replace(b'\xef\xbb\xbf', b'')
            .replace(b'\xc5\xb8\xc5\x92', b'')
        )  # .replace(b'\x9e', b'\xc5\xbe')
        if mp:
            text = mp.decode(self.kode)
            return text

    def fixI(self, in_text):

        p = in_text
        try:
            p = in_text.encode(self.kode)
            # Slova č,ć,đ,Č,Ć,Đ se nalaze i u rplStr() fukciji takođe.
            # ligature: ǈ=b'\xc7\x88' ǋ=b'\xc7\x8b' ǉ=b'\xc7\x89' ǌ=b'\xc7\x8c' \xe2\x96\xa0 = ■
            # \xc2\xa0 = NO-BREAK SPACE, \xe2\x80\x94 = EM DASH
            fp = (
                p.replace(b'/ ', b'/')
                .replace(b' >', b'>')
                .replace(b'- <', b'-<')
                .replace(b'</i> \n<i>', b'\n')
                .replace(b'< ', b'<')
                .replace(b'<<i>', b'<i>')
                .replace(b'\xc3\x83\xc2\xba', b'\x75')
                .replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94')
                .replace(b' \n', b'\n')
                .replace(b'\xe2\x82\xac\xe2\x80\x9d', b'V')
                .replace(b'\xef\xbb\xbf', b'')
                .replace(b'\xc5\xb8\xc5\x92', b'')
                .replace(b'\xd0\x94\xa0', b'\x44')
                .replace(b'\xc2\xa0', b' ')
                .replace(b"\xc4\x8f\xc2\xbb\xc5\xbc", b"")
            )  # .replace(b'\xc7\x88', b'\x4c\x6a') \
            # .replace(b'\xc7\x8b', b'\x4e\x6a') .replace(b'\xc7\x89', b'\x6c\x6a') .replace(b'\xc7\x8c', b'\x6e\x6a')
            if fp:
                text = fp.decode(self.kode)

            return text
        except IOError as e:
            logger.debug("fixI IOError({0}{1}):".format(self.putanja, e))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))

    def writeToFile(self, text):

        codelist = [
            'utf-8',
            'utf-8-sig',
            'utf-16',
            'utf-32',
            'utf-16-be',
            'utf-16-le',
            'utf-32-be',
            'utf-32-le',
        ]
        if self.kode in codelist:
            error = 'surrogatepass'
        else:
            error = 'replace'
        # logger.debug(f"writeToFile, error type: {error}")
        try:
            with open(
                self.putanja, 'w', encoding=self.kode, errors=error, newline='\r\n'
            ) as n_File:
                n_File.write(text)
                logger.debug(
                    f"Write file: {os.path.basename(self.putanja)}, encoding: {self.kode}"
                )
        except IOError as e:
            logger.debug("changeEncoding IOError({0}{1}):".format(self.putanja, e))
        except AttributeError as e:
            logger.debug(f"changeEncoding, AttributeError: {e}")
        except UnicodeEncodeError as e:
            logger.debug(f"changeEncoding, UnicodeEncodeError: {e}")
        except UnicodeDecodeError as e:
            logger.debug(f"changeEncoding, UnicodeDecodeError: {e}")
        except LookupError as e:
            logger.debug(f"changeEncoding, LookupError: {e}")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
        # text = self.getContent()
        # if text:
        # logger.debug(f"{os.path.basename(self.putanja)}, to encoding: {self.kode}")
        # return text

    def remove_bom_inplace(self):
        """Removes BOM mark, if it exists, from a file and rewrites it in-place"""
        infile = self.putanja

        def find_bom(infile):
            buffer_size = 4096
            with open(infile, 'rb') as f:
                chunk = f.read(buffer_size)
                if chunk.startswith(codecs.BOM_UTF8):
                    return codecs.BOM_UTF8
                elif chunk.startswith(codecs.BOM_UTF16):
                    return codecs.BOM_UTF16
                elif chunk.startswith(codecs.BOM_UTF16_BE):
                    return codecs.BOM_UTF16_BE
                elif chunk.startswith(codecs.BOM_UTF16_LE):
                    return codecs.BOM_UTF16_LE
                elif chunk.startswith(codecs.BOM_UTF32):
                    return codecs.BOM_UTF32
                elif chunk.startswith(codecs.BOM_UTF32_BE):
                    return codecs.BOM_UTF32_BE
                elif chunk.startswith(codecs.BOM_UTF32_LE):
                    return codecs.BOM_UTF32_LE

        _BOM = find_bom(infile)
        if _BOM:
            buffer_size = 4096
            bom_length = len(_BOM)
            with open(infile, "r+b") as fp:
                chunk = fp.read(buffer_size)
                if chunk.startswith(_BOM):
                    i = 0
                    chunk = chunk[bom_length:]
                    while chunk:
                        fp.seek(i)
                        fp.write(chunk)
                        i += len(chunk)
                        fp.seek(bom_length, os.SEEK_CUR)
                        chunk = fp.read(buffer_size)
                    fp.seek(-bom_length, os.SEEK_CUR)
                    fp.truncate()

    def truncateBuffer(self, sio):
        sio.truncate(0)
        sio.seek(0)
        return sio

    def newBuffer(self, sio):
        return StringIO()


class Preslovljavanje(FileProcessed):
    def changeLetters(self, text_r, reversed_action):

        MAPA = lat_cir_mapa
        if reversed_action == True:
            cyr_lat_mapa = dict(map(reversed, lat_cir_mapa.items()))
            MAPA = cyr_lat_mapa
        try:
            text_changed = ""

            for c in text_r:
                if c in MAPA:
                    text_changed += MAPA[c]
                else:
                    text_changed += c
            return text_changed

        except IOError as e:
            logger.debug(
                "Preslovljavanje, I/O error({0}): {1}".format(e.errno, e.strerror)
            )
        except Exception as e:
            logger.debug(f"Preslovljavanje, unexpected error: {e}")

    def preLatin(self, text_r):

        robjLatin = re.compile(
            '(%s)' % '|'.join(map(re.escape, pLatin_rpl.keys()))
        )  # pLatin_rpl je rečnik iz cp1250.replace.cfg
        try:
            fp = robjLatin.sub(lambda m: pLatin_rpl[m.group(0)], text_r)
        except IOError as e:
            logger.debug("PreLatin, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e:
            logger.debug(f"PreLatin, unexpected error: {e}")

        else:
            return fp

    def preProc(self, text_r, reversed_action):

        try:
            if reversed_action == False:
                robjCyr = re.compile('(%s)' % '|'.join(map(re.escape, pre_cyr.keys())))
                t_out = robjCyr.sub(lambda m: pre_cyr[m.group(0)], text_r)
            elif reversed_action == True:
                pre_lat = dict(map(reversed, pre_cyr.items()))
                robjLat = re.compile('(%s)' % '|'.join(map(re.escape, pre_lat.keys())))
                t_out = robjLat.sub(lambda m: pre_lat[m.group(0)], text_r)
        except IOError as e:
            logger.debug(
                "Preprocessing, I/O error({0}): {1}".format(e.errno, e.strerror)
            )
        except Exception as e:
            logger.debug(f"Preprocessing, unexpected error: {e}")

        else:
            return t_out

    def fineTune(self, text_r):

        cir_lat = {
            'ЛЈ': 'Љ',
            'НЈ': 'Њ',
            'ДЖ': 'Џ',
        }

        try:
            robjCyr = re.compile('(%s)' % '|'.join(map(re.escape, cir_lat.keys())))
            c_out = robjCyr.sub(lambda m: cir_lat[m.group(0)], text_r)
        except IOError as e:
            logger.debug(
                "Preprocessing, I/O error({0}): {1}".format(e.errno, e.strerror)
            )
        except Exception as e:
            logger.debug(f"Preprocessing, unexpected error: {e}")

        else:
            return c_out

    def fontColor(self, text_r):

        intab = 'АБВГДЕЗИЈКЛМНОПРСТУФХЦабвгдезијклмнопрстуфхц'
        outab = 'ABVGDEZIJKLMNOPRSTUFHCabvgdezijklmnoprstufhc'
        transltab = str.maketrans(intab, outab)

        try:
            # "превео:* \w+|превод:* \w+"
            f_reg = re.compile("<.*?>|www\.\w+\.\w+\s*", re.I)

            cf = f_reg.findall(text_r)

            lj = [x.translate(transltab) for x in cf]

            dok = dict(zip(cf, lj))

            for key, value in dok.items():
                text_r = text_r.replace(key, value)
        except IOError as e:
            logger.debug(
                "Tag translate, I/O error({0}): {1}".format(e.errno, e.strerror)
            )
        except Exception as e:
            logger.debug(f"Tag translate, unexpected error: {e}")

        else:
            return text_r


########################################################################
class TextProcessing(FileProcessed):
    def zameniImena(self, text):

        infile = self.putanja
        kode = self.kode

        subs = pysrt.from_string(text)

        if len(subs) > 0:
            new_s = pysrt.SubRipFile()
            for i in subs:
                sub = pysrt.SubRipItem(i.index, i.start, i.end, i.text)
                new_s.append(sub)
            new_s.clean_indexes()
            new_s.save(infile, encoding=kode)
        else:
            logger.debug(f"Transkrib, No subtitles found.")

        robj1 = re.compile(
            r'\b(' + '|'.join(map(re.escape, dictionary_1.keys())) + r')\b'
        )
        robj2 = re.compile(
            r'\b(' + '|'.join(map(re.escape, dictionary_2.keys())) + r')\b'
        )
        robj3 = re.compile(
            r'\b(' + '|'.join(map(re.escape, dictionary_0.keys())) + r')\b'
        )

        robjN1 = re.compile(r'\b(' + '|'.join(map(re.escape, dict1_n.keys())) + r')\b')
        robjN2 = re.compile(r'\b(' + '|'.join(map(re.escape, dict2_n.keys())) + r')\b')
        robjN0 = re.compile(r'\b(' + '|'.join(map(re.escape, dict0_n.keys())) + r')\b')

        robjL0 = re.compile(r'\b(' + '|'.join(map(re.escape, dict0_n2.keys())) + r')\b')
        robjL1 = re.compile(r'\b(' + '|'.join(map(re.escape, dict1_n2.keys())) + r')\b')
        robjL2 = re.compile(r'\b(' + '|'.join(map(re.escape, dict2_n2.keys())) + r')\b')
        try:
            t_out1 = robj1.subn(lambda x: dictionary_1[x.group(0)], text)
            t_out2 = robj2.subn(lambda x: dictionary_2[x.group(0)], t_out1[0])
            t_out3 = robj3.subn(lambda x: dictionary_0[x.group(0)], t_out2[0])

            t_out4 = robjN1.subn(lambda x: dict1_n[x.group(0)], t_out3[0])
            t_out5 = robjN2.subn(lambda x: dict2_n[x.group(0)], t_out4[0])
            t_out6 = robjN0.subn(lambda x: dict0_n[x.group(0)], t_out5[0])
            with open(infile, 'w', encoding=kode) as f:
                f.write(t_out6[0])
        except IOError as e:
            logger.debug(
                "Transkripcija, I/O error({0}): {1}".format(e.errno, e.strerror)
            )
        except Exception as e:  # handle other exceptions such as attribute errors
            logger.debug(F"Transkripcija, unexpected error: {traceback.format_exc}")

        def doRepl(inobj, indict):
            try:
                with open(infile, 'r', encoding=kode) as f:
                    t = f.read()
                    out = inobj.subn(lambda x: indict[x.group(0)], t)
                with open(infile, 'w', encoding=kode) as f:
                    f.write(out[0])
                self.bufferText(out[0], self.work_text)
                return out[1]
            except IOError as e:
                logger.debug(
                    "Replace keys, I/O error({0}): {1}".format(e.errno, e.strerror)
                )
            except Exception as e:
                logger.debug(f"Replace keys, unexpected error: {traceback.format_exc}")

        if not len(dict1_n2) == 0:
            doRepl(robjL1, dict1_n2)
        if not len(dict2_n2) == 0:
            doRepl(robjL2, dict2_n2)
        if not len(dict0_n2) == 0:
            doRepl(robjL0, dict0_n2)

        much = t_out1[1] + t_out2[1] + t_out3[1] + t_out4[1] + t_out5[1] + t_out6[1]
        logger.debug('Transkripcija u toku.\n--------------------------------------')
        logger.debug(f'Zamenjeno ukupno {much} imena i pojmova')

        return much

    def doReplace(self, text):

        robj_r = re.compile('(%s)' % '|'.join(map(re.escape, searchReplc.keys())))
        try:
            t_out = robj_r.subn(lambda m: searchReplc[m.group(0)], text)
        except IOError as e:
            logger.debug("DoReplace, I/O error({0}): {1}".format(e.errno, e.strerror))
        except AttributeError as e:
            logger.debug(f"DoReplace AttributeError: {e}")
        except UnicodeEncodeError as e:
            logger.debug(f"DoReplace, UnicodeEncodeError: {e}")
        except UnicodeDecodeError as e:
            logger.debug(f"DoReplace, UnicodeDecodeError: {e}")
        except Exception as e:
            logger.debug(f"DoReplace, unexpected error: {traceback.format_exc}")
        else:
            self.bufferText(t_out[0], self.work_text)
            much = t_out[1]

            logger.debug(f'DoReplace, zamenjeno [{much}] objekata ')

            return much, self.work_text.getvalue()

    def cleanUp(self, text_in, parse):

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
            r"(\([^\)]*\))|(\[[^]]*\])|(\{[^}]*\})|(<i>\s*<\/i>)|^\s*?\-+\s*?(?<=$)",
            re.M,
        )
        reg4n = re.compile(r'([A-Z ]*) [0-3](?=\:)')  # MAN 1: broj 1-3
        reg_P8 = re.compile(
            r"(\s*?)$|(^\s*?\.+)$|(^\s*?,+)$|(^\s*?;+)$|(^\s*?!+\s*?)$|(^\s*?\?+\s*?)$",
            re.M,
        )
        reg_S9 = re.compile("(?<=,\d\d\d)\n\n(?=\w)|(?<=,\d\d\d)\n\n(?=\s*\S*?)", re.M)
        reg8a = re.compile(
            r'^\s*(?<=.)|^-(?<=$)', re.M
        )  # Spejs na pocetku linije, i crtica na početku prazne linije
        regN = re.compile(r'(?<=^-)\:\s*', re.M)  # dve tacke iza crtice

        def opFile(in_text):
            return (
                in_text.replace(']:', ']')
                .replace('):', ')')
                .replace('}:', '}')
                .replace('  ', ' ')
            )

        if parse == True:
            try:
                textis = srt.parse(text_in)
                outf = srt.compose(textis)
            except IOError as e:
                logger.debug(
                    "CleanSubtitle_srt, I/O error({0}): {1}".format(e.errno, e.strerror)
                )
            except Exception as e:
                logger.debug(f"CleanSubtitle_srt, unexpected error: {e}")
            else:
                if len(outf) > 0:
                    self.bufferText(outf, self.work_text)
        else:
            self.bufferText(text_in, self.work_text)

        try:
            text_subs = self.work_text.getvalue()
            fp3 = reg_4.sub("", text_subs)

            fp5 = reg_P6.sub("", fp3)

            rf1 = opFile(fp5)

            fp11 = reg_P8.sub("", rf1)
            fp13 = reg_S9.sub("\n", fp11)
            fp14 = regN.sub('', fp13)
            fp15 = reg8a.sub('', fp14)

            return fp15

        except IOError as e:
            logger.debug(f"CleanSubtitle proc, I/O error({e.errno}): {e.strerror}")
        except Exception as e:
            logger.debug(f"CleanSubtitle proc, unexpected error: {e}")

    def cleanLine(self, text_in):

        try:
            subs = list(srt.parse(text_in))
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
                    return 0, 0, srt.compose(subs)

                else:
                    logger.debug(
                        "Index of subtitles deleted: {0}".format(
                            [i + 1 for i in to_delete]
                        )
                    )
                    logger.debug(
                        "Index of subtitles trimmed: {0}".format(text_stripped)
                    )
                    logger.debug(
                        '{0} deleted, {1} trimmed'.format(
                            len(to_delete), len(text_stripped)
                        )
                    )
                    return len(to_delete), len(text_stripped), srt.compose(subs)
            else:
                logger.debug('No subtitles found.')
        except IOError as e:
            logger.debug("CleanSubtitle_CL, I/O error({0}): {1}".format(e))
        except Exception as e:
            logger.debug(f"CleanSubtitle_CL, unexpected error: {e}")

    def rm_dash(self, text_in):

        # fix settings ------------------------------------------------------------------------------
        try:
            with shelve.open(
                os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback'
            ) as sp:
                ex = sp['key1']
                cb1_s = ex['state1']
                cb2_s = ex['state2']
                cb3_s = ex['state3']
                cb4_s = ex['state4']
                cb5_s = ex['state5']
                cb6_s = ex['state6']
                cb7_s = ex['state7']
                cb8_s = ex['state8']
        except IOError as e:
            logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e:
            logger.debug(f"FixSubtitle, unexpected error: {e}")
        # ------------------------------------------------------------------------------------------ #
        #  cb1_s Popravi gapove, cb2_s Poravnaj linije, cb3_s Pokazi linije sa greskama,             #
        #  cb4_s Crtice na pocetku prvog reda, cb5_s Spejs iza crtice, cb6_s Vise spejseva u jedan   #
        # ------------------------------------------------------------------------------------------ #

        reg_0 = re.compile(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}")
        for_rpls = re.compile(r'(?<=\d,\d\d\d\n)-+\s*')
        _space_r = re.compile(r'^ +', re.M)
        f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
        spaceS_r = re.compile(r' {2,}')
        cs_r = re.compile(r'\B- +')
        cs_r1 = re.compile(r'\B-')
        sp_n = 0

        def remSel(text_in, rep, reple):
            s1 = rep.sub(reple, text_in)
            return s1

        text = remSel(text_in, _space_r, '')

        if cb4_s == True:
            text = remSel(text, for_rpls, '')

        if cb6_s == True:
            text = remSel(text, spaceS_r, ' ')

        if cb5_s == True:
            text = remSel(text, cs_r, '-')
        elif cb5_s == False:
            sp_n = text.count('- ')
            if sp_n >= 3:
                text = remSel(text, cs_r, '-')

        if cb7_s == True:
            if not cb8_s:
                subs = list(srt.parse(text))
                if len(subs) > 0:
                    new_f = []
                    for i in range(len(subs)):
                        t = subs[i].content
                        t = (
                            t.replace('</i><i>', '')
                            .replace('</i> <i>', ' ')
                            .replace('</i>\n<i>', '\n')
                            .replace('</i>-<i>', '-')
                            .replace('</i>\n-<i>', '-\n')
                        )
                        sub = srt.Subtitle(subs[i].index, subs[i].start, subs[i].end, t)
                        new_f.append(sub)
                    text = srt.compose(new_f)
                else:
                    logger.debug('Fixer: No subtitles found!')

        if cb2_s == True:
            if not cb8_s:
                subs = list(srt.parse(text))
                if len(subs) > 0:
                    new_s = []
                    for i in subs:
                        n = self.poravnLine(i.content)
                        if cb5_s == False and sp_n >= 3:
                            n = cs_r1.sub(r'- ', n)
                        sub = srt.Subtitle(i.index, i.start, i.end, n)
                        new_s.append(sub)
                    text = srt.compose(new_s)
                else:
                    if not len(subs) > 0:
                        logger.debug('Fixer: No subtitles found!')

        if cb8_s == True:
            if not cb1_s:
                try:
                    text = remSel(text, reg_0, "00:00:00,000 --> 00:00:00,000")
                except Exception as e:
                    logger.debug(f'Fixer: {e}')

        return text

    def poravnLine(self, intext):
        def proCent(percent, whole):
            return (percent * whole) // 100

        def myWrapper(intext):
            f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
            # n = len(intext) // 2
            n = proCent(51, len(intext))
            wrapper = TextWrapper(
                break_long_words=False, break_on_hyphens=False, width=n
            )
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
        f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
        s_rpl = re.compile(' +')
        tag_rpl = re.compile(r'<[^<]*>')
        new_s = pysrt.SubRipFile()
        n = n.replace('\r', '').replace('\n', ' ')
        n = s_rpl.sub(' ', n)  # vise spejseva u jedan
        ln = (
            n.replace(',', '')
            .replace('.', '')
            .replace('!', '')
            .replace("'", "")
            .replace('-', '')
        )
        ln = tag_rpl.sub(' ', ln)
        ln = s_rpl.sub(' ', ln)
        if len(ln) >= 30 and not n.startswith('<font'):
            s1 = myWrapper(n)
            prva = s1.split('\n')[0]
            druga = s1.split('\n')[-1]
            druga = (
                druga.replace('.', '')
                .replace(',', '')
                .replace('!', '')
                .replace("'", "")
                .replace('-', '')
            )
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
                    lw = [
                        i.replace('.', '')
                        .replace('!', '')
                        .replace(',', '')
                        .replace("'", "")
                        .replace('-', '')
                        .replace('i', '')
                        for i in lw
                    ]
                    dw = [len(x) for x in lw]  # duzine reci u listi
                    c1 = s1.split('\n')[0].count(' ') + 1
                    if len(lw) >= 1:
                        if (dw[0] + prvaS) <= (drugaS - dw[0]) + 2:
                            c = c1 + 1
                            s1 = movPos(s1, c)
                            c1 = s1.split('\n')[0].count(' ') + 1
                            fls1 = tag_rpl.sub(' ', s1)
                            fls1 = s_rpl.sub(' ', fls1)
                            drugaS = len("".join(s1.split('\n')[-1]))
                            prvaS = len("".join(s1.split('\n')[0]))
                            lw = s1.split('\n')[-1].split()
                            lw = [
                                i.replace('.', '')
                                .replace('!', '')
                                .replace(',', '')
                                .replace("'", "")
                                .replace('-', '')
                                .replace('i', '')
                                for i in lw
                            ]
                            dw = [len(x) for x in lw]
                            if len(lw) >= 1:
                                if (dw[0] + prvaS) <= (drugaS - dw[0]) + 1:
                                    c = c1 + 1
                                    s1 = movPos(s1, c)
                                    c1 = s1.split('\n')[0].count(' ') + 1
                                    fls1 = tag_rpl.sub(' ', s1)
                                    fls1 = s_rpl.sub(' ', fls1)
                                    drugaS = len("".join(fls1.split('\n')[-1]))
                                    prvaS = len("".join(fls1.split('\n')[0]))
                                    lw = s1.split('\n')[-1].split()
                                    lw = [
                                        i.replace('.', '')
                                        .replace('!', '')
                                        .replace(',', '')
                                        .replace("'", "")
                                        .replace('-', '')
                                        for i in lw
                                    ]
                                    dw = [len(x) for x in lw]
                sub = s1
            else:
                sub = s1
        else:
            sub = n
        return sub
