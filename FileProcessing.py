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
import pickle
import zipfile

import codecs
import re
import unicodedata
import tempfile
import fnmatch
from collections import OrderedDict
from io import StringIO, BytesIO
from textwrap import TextWrapper
import pysrt
import srt

from zamenaImena import dictionary_0, dictionary_1, dictionary_2, rplSmap,\
     searchReplc, dict0_n, dict0_n2, dict1_n, dict1_n2, dict2_n, dict2_n2,\
     lat_cir_mapa, pLatin_rpl, pre_cyr

# from showError import w_position

import wx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(filename=os.path.join("resources", "var", "FileProcessing.log"), mode="w", encoding="utf-8")
handler.setFormatter(formatter)
logger.addHandler(handler)

def writeTempStr(inFile, text, kode):
    _error = 'strict'
    codelist = ['utf-8', 'utf-16', 'utf-32', 'utf-16-be', 'utf-16-le', 'utf-32-be', 'utf-32-le']
    if kode in codelist:
        _error = 'surrogatepass'
    try:
        with tempfile.TemporaryFile() as tfile:
            tfile.write(text.encode(encoding=kode, errors=_error))
            tfile.seek(0)
            content = tfile.read()
            with open(inFile, 'wb') as  out:
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

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)



class FileOpened:
    
    def __init__(self, path):
        
        self.putanja = path    
    
    def isCompressed(self):
        # basepath = os.path.dirname(self.putanja)
        basepath = 'tmp'
        imeFajla = os.path.basename(self.putanja)
                  
        with zipfile.ZipFile(self.putanja, 'r') as zf:
            singlefajl = len(zf.namelist())
            if singlefajl == 1:
                jedanFajl = zf.namelist()[0]
                outfile = [os.path.join(basepath, jedanFajl)]
                with open(os.path.join('resources', 'var', 'path0.pkl'), 'wb') as f:    # path je u tmp/ folderu
                    pickle.dump(outfile, f)
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
                    single = os.path.join(os.path.dirname(self.putanja), os.path.basename(files[-1]))
                    with open(os.path.join('resources', 'var', 'path0.pkl'), 'wb') as f:    # path je u tmp/ folderu
                        pickle.dump(single, f)                    
                    for i, x in zip(files, outfiles):
                        with open(x, 'wb') as f:
                            f.write(zf.read(i))
                    with open(os.path.join('resources', 'var', 'path0.pkl'), 'wb') as f:    # path je u tmp/ folderu
                        pickle.dump(outfiles, f)
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
        
        kodiranja = [ukode, 'utf-8', 'windows-1250', 'windows-1251', 'windows-1252',
                 'UTF-16LE', "UTF-16BE", 'utf-8-sig', 'iso-8859-1', 'iso-8859-2', 'utf-16', 'ascii']
            
        for enc in kodiranja:              
            try:
                with codecs.open(self.putanja, 'r', encoding=enc) as fh:
                    fh.readlines()
                    fh.seek(0)
            except:
                logger.debug(f'FindCode: UnicodeDecodeError {enc},{os.path.basename(self.putanja)}')
            else:
                logger.debug(f'Opening the file with encoding: {enc}')
                break
        with open(os.path.join('resources', 'var', 'enc0.pkl'), 'wb') as f:      
            pickle.dump(enc, f)
        return enc
        

class FileProcessed:
    
    path0_p = os.path.join('resources', 'var', 'path0.pkl')
    enc0_p = os.path.join('resources', 'var', 'enc0.pkl')
    
    def __init__(self, enc, path):
        self.kode = enc
        self.putanja = path
        
    def nameCheck(self, name_pattern, where, suffix):
        pattern = name_pattern + "*" + suffix
        files = os.listdir(where)
        n_names = len(fnmatch.filter(files, pattern))  # + 1
        return n_names    
    
    def normalizeText(self):
        error = 'strict'
        codelist = ['utf-8', 'utf-16', 'utf-32', 'utf-16-be', 'utf-16-le', 'utf-32-be', 'utf-32-le']
        if self.kode in codelist:
            error = 'surrogatepass'        
        try:
            with open(self.putanja, 'r', encoding=self.kode, errors=error) as  f: #, encoding=enc) as f:
                ucitan = f.read()
                text_normalized = unicodedata.normalize('NFKC', ucitan)  # rw)
        except IOError as e:
            logger.exception(f"NormalizeText, I/O error: ({self.putanja}{e})")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
                        
        else:
            if text_normalized:
                try:
                    with tempfile.TemporaryFile() as tfile:
                        tfile.write(bytes(text_normalized, self.kode))
                        tfile.seek(0)
                        content = tfile.read()
                        with open(self.putanja, 'wb') as  out: #, encoding=enc) as out:
                            out.write(content)
                except IOError as e:
                    logger.debug(f"NormalizeText IOError: ({self.putanja}{e})")
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                    logger.debug(''.join('!' + line for line in lines))
                    
                    ErrorDlg = wx.MessageDialog(None, "DecodeError\n\n{0}.\nIzaberite drugo kodiranje.".format(self.kode), "SubConverter", wx.OK | wx.ICON_ERROR)
                    ErrorDlg.ShowModal()    
    
    def getContent(self):
        
        codelist = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-32', 'utf-16-be', 'utf-16-le', 'utf-32-be', 'utf-32-le']
        if self.kode in codelist:
            error = 'surrogatepass'
        else:
            error = 'strict'
        # logger.debug(f"GetContent error type: {error}")
        try:
            with open(self.putanja, 'r', encoding=self.kode, errors=error) as opened:
                content = opened.read()
            buffered_content = StringIO()
            buffered_content.write(content)
            buffered_content.seek(0)
            content = buffered_content.getvalue()
            return content
        except IOError as e:
            logger.debug("GetContent IOError({0}{1}):".format(self.putanja, e))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
    
    def regularFile(self, realFile):
        with shelve.open(os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback') as s:
            s['key3'] = {'tmPath': self.putanja, 'kode': self.kode, 'realPath': realFile}
        
        with open(self.path0_p, 'wb') as v:
            pickle.dump(self.putanja, v)
        with open(os.path.join('resources', 'var', 'rpath0.pkl'), 'wb') as f:
            pickle.dump(realFile, f)
        #with open(os.path.join('resources', 'var', 'obsE.pkl'), 'wb') as f:
            #pickle.dump(self.kode, f)
            
    def checkErrors(self):
        
        fpaterns = '|'.join(['ï»¿Å', 'Ä', 'Å½', 'Ä', 'Ä', 'Å¡', 'Ä', 'Å¾', 'Ä', 'Ä', "ď»ż", "Ĺ˝", 'Ĺ ', 'ĹĄ', 'Ĺž', 'Ä', 'Å ', 'Ä‡',\
                    'Ä¿', 'Ä²', 'Ä³', 'Å¿', 'Ã¢â', "�", "Д†", "Д‡", "Ť", "Lˇ", "ï»¿", "ð"])
        
        MOJIBAKE_SYMBOL_RE = re.compile(
            '[ÂÃĂ][\x80-\x9f€ƒ‚„†‡ˆ‰‹Œ“•˜œŸ¡¢£¤¥¦§¨ª«¬¯°±²³µ¶·¸¹º¼½¾¿ˇ˘˝]|'
            r'[ÂÃĂ][›»‘”©™]\w|'
            '[¬√][ÄÅÇÉÑÖÜáàâäãåçéèêëíìîïñúùûü†¢£§¶ß®©™≠ÆØ¥ªæø≤≥]|'
            r'\w√[±∂]\w|'
            '[ðđ][Ÿ\x9f]|'
            'â€|ï»|'
            'вЂ[љћ¦°№™ќ“”]'+
            fpaterns)                
        
        text = self.getContent()
        l1 = []; l2 = []
        try:
            for match in re.finditer(MOJIBAKE_SYMBOL_RE, text):
                begin = match.start()
                end = match.end()
                l1.append(begin)
                l2.append(end)
            f_list = [(x,y) for x, y in zip(l1, l2)]
            return f_list
        except IOError as e:
            logger.debug("CheckErrors IOError({0}{1}):".format(self.putanja, e))
            return []
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
            return []
            
    def checkFile(self, file1, file2, multi):
        file1_name = file1
        if file1.endswith('.orig'):
            file1_name = os.path.splitext(file1)[0]
        try:
            with open(file1, 'rb') as f0:#, encoding='utf-8', errors='surrogatepass') as f0:
                nu = f0.read()
                n1 = nu.count(b'?')
            with open(file2, 'rb') as  f1:#, encoding='windows-1251') as f1:
                nu1 = f1.read()
                n2 = nu1.count(b'?')
            if n1 < n2:
                chars = n2 - n1
                if chars > 0:
                    poruka = u'!! Greška u tekstu !!\n{0}\nNeispravnih znakova konvertovanih kao znak `?` ukupno: [ {1} ]'.format(os.path.basename(file1_name), chars)
                    name = ''
                    logger.debug(poruka)
                    if multi == True:
                        name = file2
                    error_text = \
                    "Greška:\n\n{0}\nBilo je neispravnih znakova u tekstu\nkonvertovanih kao znak `?`\nUkupno: [{1}]\nProverite tekst.".format(os.path.basename(name), chars)
                return error_text
        except UnboundLocalError as e:
            logger.debug(f"File_Check, error({e})")
        except IOError as e:
            logger.debug(f"FileCheck IOError({e.errno} {e.strerror})")
        except: #handle other exceptions such as attribute errors
            logger.debug("File_Check, unexpected error:", sys.exc_info()[0])
            
    def checkChars(self):
        
        path = self.putanja
        kode = self.kode
        
        def percentage(part, whole):
            try:
                return int(100 * part/whole)
            except ZeroDivisionError:
                logger.debug('FileCheck Error, file is empty')
                return 0
            
        def chars(*args):
            return [chr(i) for a in args for i in range(ord(a[0]), ord(a[1])+1)]
        
        slova = "".join(chars("\u0400\u04ff"))
        
        try:
            with  open(path, 'r', encoding=kode) as f:
                x = f.read()
        except IOError as e:
            logger.debug(f"CheckChar, I/O error({e.errno}): {e.strerror}")
        except:
            logger.debug(f"CheckChar, unexpected error: {sys.exc_info()[0]}")
            
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
                
        statistic = OrderedDict()
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
            value_m = pickle.load(f)        #  Merger suffix
        
        with open(os.path.join('resources', 'var', 'tcf.pkl'), 'rb') as tf:
            oformat = pickle.load(tf)  # TXT suffix

        spattern = re.compile(r"\.srt\.srt", re.I)
        tpattern = re.compile(r"\.txt\.txt", re.I)
        upattern = re.compile(r"\s*"+value_m+r"\d*", re.I)
        
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
            
        suffix_list = ["."+x if not x.startswith("_") else x for x in ex.values()] + added
        suffix_list.append(value_m)
        suffix_list = [x.strip(".") if x.startswith(r".(") else x for x in suffix_list]
        
        _d = "."+pre_suffix           # pre_suffix je unet u funkciji koja poziva newName
        if pre_suffix.startswith("_") or pre_suffix.startswith(r"("):
            _d = pre_suffix
        
        if psufix in suffix_list:
            name1 = '{0}{1}'.format(os.path.splitext(n)[0], _d)  # fajl u tmp/ folderu
        else:
            name1 = '{0}{1}'.format(n, _d)
        
        if name1.endswith("."):
            name1 = name1[:-1]
            
        for i in suffix_list:
            if i == ".":
                continue
            fpattern = re.compile(i , re.I)
            count_s = len(re.findall(fpattern, name1))
            if count_s >= 2:
                name1 = fpattern.sub("", name1, count_s-1)
                
        return name1, sufix    # Vraca samo ime fajla bez putanje
    
    def nameDialog(self, name_entry, sufix_entry, dir_entry):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            
        presuffix_l = os.path.join("resources", "var", "presuffix_list.bak")
        real_dir = dir_entry
        name1 = name_entry
        sufix = sufix_entry
        
        caption_str = '{}'.format(real_dir)
        dlg = wx.TextEntryDialog(None, 'Ime fajla:', caption= caption_str, value="", style=wx.OK | wx.CANCEL | wx.CENTER, pos=wx.DefaultPosition)
        dlg.SetValue(name1)
        
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue() # Get the file name
            tmpnameO = os.path.join(real_dir, name)
            nameO = '{0}{1}'.format(os.path.join(real_dir, name), sufix)
            if nameO.endswith("."):
                nameO = nameO[:-1]
            if os.path.exists(nameO):
                nnm = self.nameCheck(name, real_dir, sufix)
                nameO = '{0}_{1}{2}'.format(tmpnameO, nnm, sufix)
            dlg.Destroy()
            with open(presuffix_l, 'a', encoding='utf-8') as f:
                if not '' in list(ex.values()):
                    presuffix_x = os.path.splitext(os.path.splitext(nameO)[0])[-1]+"\n"
                    if "_" in presuffix_x:
                        presuffix_ = "_"+presuffix_x.split("_")[-1]+"\n"
                    else:
                        presuffix_ = ""
                else:
                    presuffix_x = ""
                    presuffix_ = os.path.splitext(os.path.splitext(nameO)[0])[-1]+"\n"
                f.write(presuffix_)
            return nameO
        else:
            dlg.Destroy()
            return None
        
    def rplStr(self, in_text):
        
        # Rečnik je 'rplSmap'. Lista ključeva(keys) je 'rplsList'.
        intext = StringIO()
        try:
            intext.write(in_text)
            intext.seek(0)
        except IOError as e:
            logger.debug("String replace IOError({0}{1}):".format(self.putanja, e))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
            
        p = intext.getvalue()
        n_pattern = re.compile("|".join(list(rplSmap.keys())))
        nf = n_pattern.findall(p) 
        
        logger.debug('\nSpecijalnih znakova ukupno: [{0}]'.format(len(nf)))
        if len(nf) > 0:
            logger.debug(f'SpecChars: {" ".join(nf)}\n')
            f_path = re.sub(r"\.TEMP_\w*", "", os.path.basename(self.putanja), re.I)
            msginfo = wx.MessageDialog(None, f'Specijalni znakovi u tekstu:\n\n{os.path.basename(f_path)}\n\n{", ".join(nf)}.',\
                                       'SubConverter', wx.OK | wx.ICON_INFORMATION)
            msginfo.ShowModal()
        
        for key, value in rplSmap.items():
            p = p.replace(key, value)   # !!! Svuda treba da bude p "p=p.replace"!!!
        if p:
            intext = self.truncateBuffer(intext)
            intext.write(p)
            intext.seek(0)
        # Dodatni replace u binarnom formatu:
        # \xe2\x96\xa0 = ■, xc2\xad = SOFT HYPHEN, \xef\xbb\xbf = bom utf-8, \xe2\x80\x91 = NON-BREAKING HYPHEN
        
        btext = BytesIO()
        p = intext.getvalue().encode(self.kode)
        
        mp = p.replace(b'\xc2\xad', b'') .replace(b'\xd0\x94\xc4', b'D').replace(b"\xc4\x8f\xc2\xbb\xc5\xbc", b"") \
            .replace(b'\xe2\x80\x91', b'') .replace(b'\xc3\x83\xc2\xba', b'u') \
            .replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94') .replace(b'\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94') \
            .replace(b'\xef\xbb\xbf', b'') .replace(b'\xc5\xb8\xc5\x92', b'')# .replace(b'\x9e', b'\xc5\xbe')
        if mp:
            btext.write(mp)
            btext.seek(0)
            text = btext.getvalue().decode(self.kode)
            intext.close()
            btext.close()
            return text
    
    def fixI(self, in_text):
        intext = StringIO()
        try:
            intext.write(in_text)
            intext.seek(0)
        except IOError as e:
            logger.debug("fixI IOError({0}{1}):".format(self.putanja, e))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
            
        btext = BytesIO()
        p = intext.getvalue()        
        try:
            p = intext.getvalue().encode(self.kode)
            # Slova č,ć,đ,Č,Ć,Đ se nalaze i u rplStr() fukciji takođe.
            #ligature: ǈ=b'\xc7\x88' ǋ=b'\xc7\x8b' ǉ=b'\xc7\x89' ǌ=b'\xc7\x8c' \xe2\x96\xa0 = ■
            # \xc2\xa0 = NO-BREAK SPACE, \xe2\x80\x94 = EM DASH
            fp = p.replace(b'/ ', b'/').replace(b' >', b'>').replace(b'- <', b'-<').replace(b'</i> \n<i>', b'\n') \
                .replace(b'< ', b'<').replace(b'<<i>', b'<i>').replace(b'\xc3\x83\xc2\xba', b'\x75') \
                .replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94').replace(b' \n', b'\n') \
                .replace(b'\xe2\x82\xac\xe2\x80\x9d', b'V') .replace(b'\xef\xbb\xbf', b'') \
                .replace(b'\xc5\xb8\xc5\x92', b'').replace(b'\xd0\x94\xa0', b'\x44') \
                .replace(b'\xc2\xa0', b' ').replace(b"\xc4\x8f\xc2\xbb\xc5\xbc", b"")   # .replace(b'\xc7\x88', b'\x4c\x6a') \
                #.replace(b'\xc7\x8b', b'\x4e\x6a') .replace(b'\xc7\x89', b'\x6c\x6a') .replace(b'\xc7\x8c', b'\x6e\x6a')
            if fp:
                btext.write(fp)
                btext.seek(0)
                text = btext.getvalue().decode(self.kode)
                btext.close()
                intext.close()
                # self.writeToFile(text)
            return text            
        except IOError as e:
            logger.debug("fixI IOError({0}{1}):".format(self.putanja, e))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.debug(''.join('!' + line for line in lines))
            
    def unix2DOS(self):
        try:
            fileContents = open(self.putanja,"r", encoding=self.kode, errors='replace').read()
            f = open(self.putanja,"w", encoding=self.kode, errors='replace', newline="\r\n")
            f.write(fileContents)
            f.close()
        except IOError as e:
            logger.debug(f"Unix2DOS, IOerror: {e}")
        except: #handle other exceptions such as attribute errors
            logger.debug("Unix2DOS, unexpected error:", sys.exc_info()[0])    
            
    def writeToFile(self, text):
        
        codelist = ['utf-8', 'utf-8-sig','utf-16', 'utf-32', 'utf-16-be', 'utf-16-le', 'utf-32-be', 'utf-32-le']
        if self.kode in codelist:
            error = 'surrogatepass'
        else:
            error = 'replace'
        # logger.debug(f"writeToFile, error type: {error}")
        try:
            with open(self.putanja, 'w', encoding=self.kode, errors=error, newline='\r\n') as n_File:
                n_File.write(text)
                logger.debug("Write to file, encoding: {}".format(self.kode))
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
        text = self.getContent()
        if text:
            logger.debug(f"{os.path.basename(self.putanja)}, to encoding: {self.kode}")
        return text
    
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
    
    def changeLetters(self, reversed_action):
        
        inkode = self.kode
        infile = self.putanja
        
        MAPA = lat_cir_mapa
        if reversed_action == True:
            cyr_lat_mapa = dict(map(reversed, lat_cir_mapa.items()))
            MAPA = cyr_lat_mapa        
        
        # preslovljavanje, prepise se utfFile:
        try:
            with open(infile, 'r', encoding=inkode) as f:
                text_read = f.read()
                
                text_changed = ""
                
                for c in text_read:
                    if c in MAPA:
                        text_changed += MAPA[c]
                    else:
                        text_changed += c
            self.writeToFile(text_changed)
        
        except IOError as e:
            logger.debug("Preslovljavanje, I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            logger.debug("Preslovljavanje, unexpected error:", sys.exc_info()[0])
        
    def preLatin(self):
        kode = self.kode
        infile = self.putanja        
        robjLatin = re.compile('(%s)' % '|'.join(map(re.escape, pLatin_rpl.keys()))) # pLatin_rpl je rečnik iz cp1250.replace.cfg
        try:
            with open(infile, 'r', encoding=kode) as f:
                p = f.read()
                fp = robjLatin.sub(lambda m: pLatin_rpl[m.group(0)], p)
        except IOError as e:
            logger.debug("PreLatin, I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            logger.debug("PreLatin, unexpected error:", sys.exc_info()[0])
        else:
            if fp:
                self.writeToFile(fp)
                
    def preProc(self, reversed_action):
        kode = self.kode
        infile = self.putanja        
        
        try:
            with open(infile, 'r', encoding=kode) as f:
                tNew = f.read()
                if reversed_action == False:
                    robjCyr = re.compile('(%s)' % '|'.join(map(re.escape, pre_cyr.keys())))
                    t_out = robjCyr.sub(lambda m: pre_cyr[m.group(0)], tNew)
                elif reversed_action == True:
                    pre_lat = dict(map(reversed, pre_cyr.items()))
                    robjLat = re.compile('(%s)' % '|'.join(map(re.escape, pre_lat.keys())))
                    t_out = robjLat.sub(lambda m: pre_lat[m.group(0)], tNew)
        except IOError as e:
            logger.debug("Preprocessing, I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            logger.debug("Preprocessing, unexpected error:", sys.exc_info()[0])
        else:
            if t_out:
                self.writeToFile(t_out)
                
    def fineTune(self):
        kode = self.kode
        Ufile = self.putanja        
        cir_lat = {
            'ЛЈ': 'Љ',
            'НЈ': 'Њ',
            'ДЖ': 'Џ',
        }
                
        BLOCK = 1048576
        try:
            with open(Ufile, 'r', encoding= kode) as f:
                tNew = f.read(BLOCK)
                robjCyr = re.compile('(%s)' % '|'.join(map(re.escape, cir_lat.keys())))
                c_out = robjCyr.sub(lambda m: cir_lat[m.group(0)], tNew)
        except IOError as e:
            logger.debug("Preprocessing, I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            logger.debug("Preprocessing, unexpected error:", sys.exc_info()[0])
        else:
            if c_out:
                self.writeToFile(c_out)
                
    def fontColor(self):
        inkode = self.kode
        intext = self.putanja        
        def preFc(inword):
            intab = 'АБВГДЕЗИЈКЛМНОПРСТУФХЦабвгдезијклмнопрстуфхц'
            outab = 'ABVGDEZIJKLMNOPRSTUFHCabvgdezijklmnoprstufhc'
            transltab = str.maketrans(intab, outab)
            ouword = inword.translate(transltab)
            return ouword
        try:
            with open(intext, 'r', encoding=inkode) as fin:
                
                fr = fin.read()
                
                freg = re.compile(r'<.*?>', re.I)
                wreg = re.compile(r'www\.\w+\.\w+\s*')
                # preg = re.compile(r"превео:* |превод:* \w+", re.I)
                
                cf = freg.findall(fr) + wreg.findall(fr)# + preg.findall(fr)
                
                lj = []
                for i in cf:
                    new = preFc(i)
                    lj.append(new)
                dok = dict(zip(cf, lj))
                for key, value in dok.items():
                    fr = fr.replace(key, value)
        except IOError as e:
            logger.debug("Tag translate, I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            logger.debug("Tag translate, unexpected error:", sys.exc_info()[0])
        else:
            if fr:
                self.writeToFile(fr)
                
########################################################################
class TextProcessing(FileProcessed):
    
    def zameniImena(self):
        
        infile = self.putanja
        kode = self.kode
        
        subs = pysrt.open(infile, encoding=kode)
        if len(subs) > 0:
            new_s = pysrt.SubRipFile()
            for i in subs:
                # i.text = i.text.strip()
                sub = pysrt.SubRipItem(i.index, i.start, i.end, i.text)
                new_s.append(sub)
            new_s.clean_indexes()
            new_s.save(infile, encoding=kode)
        else:
            logger.debug(f"Transkrib, No subtitles found.")
        
        robj1 = re.compile(r'\b(' + '|'.join(map(re.escape, dictionary_1.keys())) + r')\b')
        robj2 = re.compile(r'\b(' + '|'.join(map(re.escape, dictionary_2.keys())) + r')\b')
        robj3 = re.compile(r'\b(' + '|'.join(map(re.escape, dictionary_0.keys())) + r')\b')
        
        robjN1 = re.compile(r'\b(' + '|'.join(map(re.escape, dict1_n.keys())) + r')\b')
        robjN2 = re.compile(r'\b(' + '|'.join(map(re.escape, dict2_n.keys())) + r')\b')
        robjN0 = re.compile(r'\b(' + '|'.join(map(re.escape, dict0_n.keys())) + r')\b')
        
        robjL0 = re.compile(r'\b(' + '|'.join(map(re.escape, dict0_n2.keys())) + r')\b')
        robjL1 = re.compile(r'\b(' + '|'.join(map(re.escape, dict1_n2.keys())) + r')\b')
        robjL2 = re.compile(r'\b(' + '|'.join(map(re.escape, dict2_n2.keys())) + r')\b')
        try:
            with open(infile, 'r', encoding= kode) as f:
                tNew = f.read()
                t_out1 = robj1.subn(lambda x: dictionary_1[x.group(0)], tNew)
                t_out2 = robj2.subn(lambda x: dictionary_2[x.group(0)], t_out1[0])
                t_out3 = robj3.subn(lambda x: dictionary_0[x.group(0)], t_out2[0])
            with open(infile, 'w', encoding= kode) as f:
                f.write(t_out3[0])
            
            with open(infile, 'r', encoding= kode) as f:
                tNew1 = f.read()
                t_out4 = robjN1.subn(lambda x: dict1_n[x.group(0)], tNew1)
                t_out5 = robjN2.subn(lambda x: dict2_n[x.group(0)], t_out4[0])
                t_out6 = robjN0.subn(lambda x: dict0_n[x.group(0)], t_out5[0])
            with open(infile, 'w', encoding= kode) as f:
                f.write(t_out6[0])
        except IOError as e:
            logger.debug("Transkripcija, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e: #handle other exceptions such as attribute errors
            logger.debug(F"Transkripcija, unexpected error: {traceback.format_exc}")     
            
        def doRepl(inobj, indict):
            try:
                with open(infile, 'r', encoding= kode) as f:
                    t = f.read()          
                    out = inobj.subn(lambda x: indict[x.group(0)], t)
                with open(infile, 'w', encoding= kode) as f:
                    f.write(out[0])
                return out[1]
            except IOError as e:
                logger.debug("Replace keys, I/O error({0}): {1}".format(e.errno, e.strerror))
            except Exception as e: #handle other exceptions such as attribute errors
                logger.debug(f"Replace keys, unexpected error: {traceback.format_exc}")
                
        if not len(dict1_n2) == 0:
            n1 = doRepl(robjL1, dict1_n2)
        if not len(dict2_n2) == 0:
            n2 = doRepl(robjL2, dict2_n2)
        if not len(dict0_n2) == 0:
            n3 = doRepl(robjL0, dict0_n2)        
        
        much = t_out1[1] + t_out2[1] + t_out3[1] + t_out4[1] + t_out5[1] + t_out6[1]        
        logger.debug('Transkripcija u toku.\n--------------------------------------')
        logger.debug(f'Zamenjeno ukupno {much} imena i pojmova')
        
        return much
    
    def doReplace(self):
        
        infile = self.putanja
        inkode = self.kode
        
        robj_r = re.compile('(%s)' % '|'.join(map(re.escape, searchReplc.keys())))
        try:
            with open(infile, 'r', encoding=inkode) as f:
                tNew = f.read()
                t_out = robj_r.subn(lambda m: searchReplc[m.group(0)], tNew)
        except IOError as e:
            logger.debug("DoReplace, I/O error({0}): {1}".format(e.errno, e.strerror))
        except AttributeError as e:
            logger.debug(f"DoReplace AttributeError: {e}")
        except UnicodeEncodeError as e:
            logger.debug(f"DoReplace, UnicodeEncodeError: {e}")
        except UnicodeDecodeError as e:
            logger.debug(f"DoReplace, UnicodeDecodeError: {e}")
        except Exception as e: #handle other exceptions such as attribute errors
            logger.debug(f"DoReplace, unexpected error: {traceback.format_exc}")
        else:
            if t_out:
                writeTempStr(self.putanja, t_out[0], self.kode)
            much = t_out[1]
            logger.debug(f'DoReplace, zamenjeno [{much}] objekata ')
        
            return much
        
    def cleanUp(self):
        
        infile = self.putanja
        enkoding = self.kode
        
        u_okruglim = re.compile(r'(\([^\)]*\))', re.M)  # okrugle zagrade
        u_kockastim = re.compile(r'(\[[^]]*\])', re.M)     # kockaste zagrade
        u_viticastim = re.compile(r'(\{[^}]*\})', re.M)     #  vitičaste zagrade
        reg1 = re.compile(r'(^\s*?\.+)$', re.M)     # Tačka na kraju, prazna linija
        reg2 = re.compile(r'(^\s*?,+)$', re.M)      # Zarez na kraju, prazna linija 
        reg3 = re.compile(r'(^\s*?;+)$', re.M)      # Tačka zarez na kraju, prazna linija
        #reg4 = re.compile(r'((?!\n)([A-Z\s]*){1,3}(?=\:)(?<![0-9a-z])\:\s)')
        reg4 = re.compile(r'(([A-Z ]*){1,3}(?=\:)(?<![0-9a-z])\:\s)')
        reg4n = re.compile(r'([A-Z ]*) [0-3](?=\:)')  # MAN 1: broj 1-3
        reg4a = re.compile(r'^\s*\-\.+\s+', re.M)
        reg5 = re.compile(r'^[ \t]*', re.M)                   # Spejs Tab, Kompajlira se sa re.M da bi radilo za pocetak linije
        reg6 = re.compile(r'(<i>\s*<\/i>)')         
        reg7 = re.compile(r'(^\s*?\-+\s*?)$', re.M)         # Crtice
        reg8 = re.compile(r'(\s*?)$', re.M)                 # Spejs na kraju linije
        reg8a = re.compile(r'^\s*(?<=\w)', re.M)            # Spejs na pocetku linije
        reg9 = re.compile(r'(^\s*?!+\s*?)$', re.M)          # Uzvičnici
        reg10 = re.compile(r'(^\s*?\?+\s*?)$', re.M)        # Znak pitanja
        regS = re.compile(r'(?<=,\d\d\d)\n\n(?=\w)', re.M)   # Prva prazna linija
        regT = re.compile(r'(?<=,\d\d\d)\n\n(?=\s*\S*?)', re.M)
        regN = re.compile(r'(?<=^-)\:\s*', re.M)            # dve tacke iza crtice
        
        def opFile():
            with open(infile, 'r', encoding=enkoding) as f:
                of = f.read()
                ofout = of.replace(']:', ']').replace('):', ')').replace('}:', '}').replace('  ', ' ')
            return ofout         
        
        try:
            with open(infile, 'r', encoding=enkoding) as f:
                textis = srt.parse(f.read())
                outf = srt.compose(textis)
        except IOError as e:
            logger.debug("CleanSubtitle_srt, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e: #handle other exceptions such as attribute errors
            logger.debug(f"CleanSubtitle_srt, unexpected error: {traceback.format_exc}")
        else:
            if len(outf) > 0:
                writeTempStr(inFile=infile, text=outf, kode=enkoding)
                
        try:
            with open(infile, 'r', encoding= enkoding) as file_processed:
                of = file_processed.read()
                fp1 = reg4a.sub('', of)
                fp2 = reg4.sub('', fp1)
                fp3 = reg5.sub('', fp2)
                writeTempStr(infile, fp3, enkoding)
                
            with open(infile, 'r', encoding=enkoding) as file_processed:
                of = file_processed.read()
                fp1 = u_okruglim.sub('', of)
                fp2 = u_kockastim.sub('', fp1)
                fp3 = u_viticastim.sub('', fp2)
                fp4 = reg6.sub('', fp3)
                fp5 = reg7.sub('', fp4)
                writeTempStr(infile, fp5, enkoding)
            rf1 = opFile()
            writeTempStr(infile, rf1, enkoding)
            
            with open(infile, 'r', encoding=enkoding) as file_processed:
                fp5 = file_processed.read()
                fp6 = reg8.sub('', fp5)
                fp7 = reg1.sub('', fp6)
                fp8 = reg2.sub('', fp7)
                fp9 = reg3.sub('', fp8)
                fp10 = reg9.sub('', fp9)
                fp11 = reg10.sub('', fp10)
                fp12 = regS.sub('\n', fp11)
                fp13 = regT.sub('\n', fp12)
                fp14 = regN.sub('', fp13)
                fp15 = reg8a.sub('', fp14)            
                
                writeTempStr(infile, fp15, enkoding)
                
        except IOError as e:
            logger.debug(f"CleanSubtitle proc, I/O error({e.errno}): {e.strerror}")
        except Exception: #handle other exceptions such as attribute errors
            logger.debug(f"CleanSubtitle proc, unexpected error: {traceback.format_exc}")
            
    def cleanLine(self):
        filename = self.putanja
        enkoding = self.kode
        try:
            subs = pysrt.open(filename, encoding=enkoding)
            if len(subs) > 0:
                # Trim white spaces
                text_stripped = []
                for i in range(len(subs)):
                    orig_text = subs[i].text
                    stripped_text = subs[i].text.strip()
                    if orig_text != stripped_text:
                        text_stripped.append(subs[i].index)
                        subs[i].text = subs[i].text.strip()

                # Find the list index of the empty lines. This is different than the srt index!
                # The list index starts from 0, but the srt index starts from 1.
                count = 0
                to_delete = []
                for sub in subs:
                    if not sub.text:
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
                    logger.debug("Subtitle clean. No changes made.")
                    subs.save(filename, encoding=enkoding)
                
                else:
                    logger.debug("Index of subtitles deleted: {0}".format([i + 1 for i in to_delete]))
                    logger.debug("Index of subtitles trimmed: {0}".format(text_stripped))
                    logger.debug('{0} deleted, {1} trimmed'.format(len(to_delete), len(text_stripped)))
                    subs.save(filename, encoding= enkoding)
                    return len(to_delete), len(text_stripped)
            else:
                logger.debug('No subtitles found.')
        except IOError as e:
            logger.debug("CleanSubtitle_CL, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception:
            logger.debug(f"CleanSubtitle_CL, unexpected error: {traceback.format_exc}")
            
    def rm_dash(self):
        kode = self.kode
        intext = self.putanja
        # fix settings ------------------------------------------------------------------------------   
        try:
            with shelve.open(os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback') as  sp:
                ex = sp['key1']
                cb1_s = ex['state1']; cb2_s = ex['state2']; cb3_s = ex['state3']
                cb4_s = ex['state4']; cb5_s = ex['state5']; cb6_s = ex['state6']; cb7_s = ex['state7']; cb8_s = ex['state8']
        except IOError as e:
            logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
        except: #handle other exceptions such as attribute errors
            logger.debug("FixSubtitle, unexpected error:", sys.exc_info()[0:2])
        #  cb1_s Popravi gapove, cb2_s Poravnaj linije, cb3_s Pokazi linije sa greskama,
        #  cb4_s Crtice na pocetku prvog reda, cb5_s Spejs iza crtice, cb6_s Vise spejseva u jedan
        # -------------------------------------------------------------------------------------------        
        
        for_rpls = re.compile(r'(?<=\d,\d\d\d\n)-+\s*')
        _space_r = re.compile(r'^ +', re.M)
        f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
        spaceS_r = re.compile(r' {2,}')
        cs_r = re.compile(r'\B- +')
        cs_r1 = re.compile(r'\B-')
        sp_n = 0
        def remSel(intext, rep, reple, kode):
            s = self.getContent()
            s1 = rep.sub(reple, s)
            writeTempStr(intext, s1, kode)
                
        remSel(intext, _space_r, '', kode)
        
        if cb4_s == True:
            remSel(intext, for_rpls, '', kode)
            
        if cb6_s == True:
            remSel(intext, spaceS_r, ' ', kode)
            
        if cb5_s == True:
            remSel(intext, cs_r, '-', kode)
        elif cb5_s == False:
            with open(intext, 'r', encoding=kode) as f:
                sp_n = f.read().count('- ')
                if sp_n >= 3:
                    remSel(intext, cs_r, '-', kode)
            
        if cb7_s == True:
            subs = pysrt.open(intext, kode)
            if len(subs) > 0:
                new_f = pysrt.SubRipFile()
                for i in subs:
                    t = i.text
                    t = t.replace('</i><i>', '').replace('</i> <i>', ' ').replace('</i>\n<i>', '\n').replace('</i>-<i>', '-').replace('</i>\n-<i>', '-\n')
                    sub = pysrt.SubRipItem(i.index, i.start, i.end, t)
                    new_f.append(sub)
                new_f.clean_indexes()
                new_f.save(intext, kode)
            else:
                logger.debug('Fixer: No subtitles found!')
        if cb8_s == True:
            subs = pysrt.open(intext, kode)
            if len(subs) > 0:
                new_f = pysrt.SubRipFile()
                for i in subs:
                    i.start = i.end = pysrt.SubRipTime(0, 0, 0, 0)
                    sub = pysrt.SubRipItem(i.index, i.start, i.end, i.text)
                    new_f.append(sub)
                new_f.clean_indexes()
                new_f.save(intext, kode)
            else:
                logger.debug('Fixer: No subtitles found!')        
            
        # funkcija za zamenu spejsa na određenoj poziciji u stringu,------------------------------
        # nprimer treći spejs u prvoj liniji
        def replacenth(string, sub, wanted, n): 
            where = [m.start() for m in re.finditer(sub, string)][n-1]
            before = string[:where]
            after = string[where:]
            after = after.replace(sub, wanted, 1)
            newString = before + after
            return newString        
        #------------------------------------------------------------------------------------------        
        if cb2_s == True:
            subs = pysrt.open(intext, kode)
            if len(subs) > 0:            
                new_s = pysrt.SubRipFile()
                for i in subs:
                    n = self.poravnLine(i.text)
                    if cb5_s == False and sp_n >= 3:
                        n = cs_r1.sub(r'- ', n)                    
                    sub = pysrt.SubRipItem(i.index, i.start, i.end, n)
                    new_s.append(sub)
                new_s.clean_indexes()
                new_s.save(intext, encoding=kode)
            else:
                if not len(subs) > 0:
                    logger.debug('Fixer: No subtitles found!')
                    
    def poravnLine(self, intext):
        def proCent(percent, whole):
            return (percent * whole) // 100        
        def myWrapper(intext):
            f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
            # n = len(intext) // 2
            n = proCent(51, len(intext))
            wrapper = TextWrapper(break_long_words=False, break_on_hyphens=False, width=n)
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
            where = [m.start() for m in re.finditer(' ', text)][n-1]
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
        ln = n.replace(',', '').replace('.', '').replace('!', '').replace("'", "").replace('-', '')
        ln = tag_rpl.sub(' ', ln)
        ln = s_rpl.sub(' ', ln)
        if len(ln) >= 30 and not n.startswith('<font'):
            s1 = myWrapper(n)
            prva = s1.split('\n')[0]
            druga = s1.split('\n')[-1]
            druga = druga.replace('.', '').replace(',', '').replace('!', '').replace("'", "").replace('-', '')
            druga = tag_rpl.sub(' ', druga)
            druga = s_rpl.sub(' ', druga)                
            len_prva = len("".join(prva)); len_druga = len("".join(druga))
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
                    lw = [i.replace('.', '').replace('!', '').replace(',', '').replace("'", "").replace('-', '').replace('i', '') for i in lw]
                    dw = [len(x) for x in lw]           # duzine reci u listi
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
                            lw = [i.replace('.', '').replace('!', '').replace(',', '').replace("'", "").replace('-', '').replace('i', '') for i in lw]
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
                                    lw = [i.replace('.', '').replace('!', '').replace(',', '').replace("'", "").replace('-', '') for i in lw]
                                    dw = [len(x) for x in lw]                                    
                sub = s1
            else:
                sub = s1
        else:
            sub = n
        return sub    
    
    