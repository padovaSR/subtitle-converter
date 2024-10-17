# -*- coding: utf-8 -*-

from os.path import basename, splitext, exists, join
import os
from itertools import chain 
import zipfile
import re

import logging.config
logger = logging.getLogger(__name__)


class ExportZip:
    
    def __init__(self, input_1=None, input_2=None, input_3=None, utf8_ext=None):
        """input_1 is cyrillic file created, or other converted;
            input_2 is cyrillic_utf8 created;
            input_3 is original file, from cyrillic action;
        """
        self.input_1 = input_1
        self.input_2 = input_2
        self.input_3 = input_3
        self.utf8_ext = utf8_ext
        
    def WriteZipFile(self, file_name, selections=[], folders=False):
        """"""
        try:
            files,zdata = self.collectAllData(selections, folders)
            with zipfile.ZipFile(file_name, 'w') as fzip:
                for i, x in zip(files, zdata):
                    if not i:
                        continue
                    if len(x) == 0:
                        continue
                    fzip.writestr(i, x, zipfile.ZIP_DEFLATED)
            if self.testZipFile(file_name) is True:
                if len(self.input_1) > 1:
                    self.removeFiles(self.input_1, self.input_2)
                return True
            else:
                return False
        except Exception as e:
            logger.debug(f" Export ZIP error: {e}")
    
    def removeFiles(self, input_1, input_2):
        """"""
        inputs = input_1 + (input_2 or [])
        for i in inputs:
            if exists(i):
                os.remove(i)
                logger.debug(f"Delete {i}")        
    
    def testZipFile(self, file_created):
        the_zip_file = zipfile.ZipFile(file_created)
        ret = the_zip_file.testzip()
        if ret is not None:
            logger.debug(f"First bad file in zip: {ret}")
            return False
        else:
            return True
    
    def collectInfoData(self):
        return list(chain.from_iterable(self.CreateInfo()))
    
    def collectAllData(self, selection, folders):
        z_data = self.CreateData()
        i_data = self.CreateInfo()
        if len(z_data) > 1 and len(i_data) > 1:
            files_info = list(chain.from_iterable([i_data[x] for x in selection]))
            zip_data = list(chain.from_iterable([z_data[x] for x in selection]))
        else:
            files_info = i_data[0]
            zip_data = z_data[0]
        if folders:
            files_info = []
            for folder, files_group in zip(folders, i_data):
                files_info.append([join(folder, file) for file in files_group])                        
            files_info = list(chain.from_iterable([files_info[x] for x in selection]))
        return files_info, zip_data
        
    def CreateData(self):
        data_1 = [self.getData(file_path) for file_path in self.input_1]
        if not self.input_2 and not self.input_3:
            return [data_1]
        else:
            data_2 = [self.getData(file_path) for file_path in self.input_2]
            data_3 = [self.getData(file_path) for file_path in self.input_3]
            data_4 = [self.createLatin_UTF8(path) for path in self.input_3]
            return [data_1, data_2, data_3, data_4]

    def CreateInfo(self):
        info_1 = [self.makeInfo(file_path) for file_path in self.input_1]
        if not self.input_2 and not self.input_3:
            return [info_1]
        else:
            info_2 = [self.makeInfo(file_path) for file_path in self.input_2]
            info_3 = [self.makeInfo(file_path) for file_path in self.input_3]
            info_4 = [
                self.makeInfo(file_path, index=index+1, pre_ext=self.utf8_ext)
                for index, file_path in enumerate(self.input_3)
            ]
            return [info_1, info_2, info_3, info_4]
        
    @staticmethod
    def createLatin_UTF8(input_file):
        """"""
        text = ""
        for enc in ["utf-8", "cp1250"]:
            try:
                with open(input_file, "r", encoding=enc) as f:
                    text = f.read()
            except:
                logger.debug(f"createLatin_UTF8: trying {enc}")
            else:
                logger.debug(f"createLatin_UTF8: opened {enc}")
            if not text:
                text = f"{basename(input_file)}\n\nError reading from file.\nPlease fix the file."            
        return text.encode("utf-8", errors="surrogatepass")

    @staticmethod
    def getData(input_file):
        """"""
        with open(input_file, "rb") as  data_file:
            return data_file.read()
    
    @staticmethod
    def makeInfo(input_file, index=None, pre_ext=None):
        """"""
        if not pre_ext:
            return basename(input_file)
        elif pre_ext:
            name, ext = splitext(basename(input_file))
            file_name, pre_extension = splitext(name)
            if pre_extension.strip(".") == pre_ext:
                pre_ext = f"{pre_ext}_{index}_"
            if pre_extension.find("ION") or len(pre_extension) > 6:
                file_name = name
                pre_extension = ""
            return f"{file_name}.{pre_ext}{ext}"

    @staticmethod
    def file_name(input_file):
        epattern = re.compile(r"episode\s*-*\d*", re.I)
        input_file,ext = splitext(input_file)
        file_name = epattern.sub("", input_file)
        file_name = re.sub(r"(?<=s\d\d)e\d{1,2}", "", file_name, count=1, flags=re.I)
        return file_name.replace(" 1 ", "").replace("x01", "").replace("  ", " ")+".zip"