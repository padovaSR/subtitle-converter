#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#
import os
import sys
import re
import shelve
import zipfile
import shutil
import pickle
import pysrt
import srt
from more_itertools import unique_everseen
from pydispatch import dispatcher
from operator import itemgetter
import glob
from collections import namedtuple 
from io import StringIO, BytesIO
from file_dnd import FileDrop 
from settings import (
    filePath,
    WORK_TEXT,
    PREVIOUS,
    FILE_HISTORY,
    log_file_history,
    printEncoding,
)
from errors_check import checkErrors, checkChars, displayError, checkFile
from merge import myMerger,fixGaps
from fixer_settings import FixerSettings
from file_settings import FileSettings 
from zamenaImena import shortcutsKey
from merger_settings import Settings
from Manual import MyManual 
from text_processing import (
    changeLetters,
    normalizeText,
    bufferText,
    bufferCode,
    rplStr,
    fixI,
    codelist,
    zameniImena,
    doReplace,
    cleanUp,
    cleanLine,
    rm_dash,
    writeTempStr,
    preLatin,
    remTag, 
)
import logging
from File_processing import FileOpened, newName, nameDialog, writeToFile

import wx.lib.agw.shortcuteditor as SE
import wx

from subtitle_converter_gui import ConverterFrame

VERSION = "v0.5.8_test4"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message).200s')
handler = logging.FileHandler(
    filename=filePath("resources", "var", "log", "subtitle_converter.log"),
    mode="a",
    encoding="utf-8",
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class MyFrame(ConverterFrame):
    def __init__(self, *args, **kwds):
        # ConverterFrame.__init__(self, *args, **kwds)
        super(MyFrame, self).__init__(*args, **kwds)
        
        self.SetTitle(f"SubtitleConverter {VERSION}")

        self.wildcard = "SubRip (*.zip; *.srt;\
        *.txt)|*.zip;*.srt;*.txt|MicroDVD (*.sub)|*.sub|Text File\
        (*.txt)|*.txt|All Files (*.*)|*.*"
        
        with shelve.open(
            filePath('resources', 'var', 'dialog_settings.db'),
            flag='writeback',
        ) as s:
            ex = s['key4']
            new_font = ex['new_font']
            fontSize = int(ex['fontSize'])
            fC = ex['fontColour']
            bl = ex['weight']

        if bl == 92:
            weight = wx.FONTWEIGHT_BOLD
        else:
            weight = wx.FONTWEIGHT_NORMAL

        self.text_1.SetFont(
            wx.Font(
                fontSize,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                weight,
                0,
                new_font,
            )
        )
        self.curFont = self.text_1.GetFont()
        self.curClr = wx.Colour((fC[0], fC[1], fC[2], fC[3]))
        self.text_1.SetForegroundColour(self.curClr)
        self.text_1.SetFont(self.curFont)
        # self.curClr = self.text_1.GetForegroundColour()
        self.updateUI()
        
        self.dont_show = False
        
        self.workText = StringIO()
        self.bytesText = BytesIO()
        
        self.utf8_latText = ""
        
        self.location = "tmp"
        self.cyrUTF = r""        
        self.pre_suffix = r""
        self.newEnc = ""
        self.multiFile = {}
        self.previous_action= {}
        
        self.enchistory = {}
        
        self.saved_file = {}
        self.droped = {}
        self.tmpPath = []
        self.real_path = []
        self.real_dir = r""
        self.cyrUTFmulti = []
        
        self.reloadText = {}
        self.reloaded = 0
        
        ## Undo-Redo ######################
        self.UNDO = []
        self.REDO = []
        ###################################
        
        self.findData = wx.FindReplaceData()
        self.pos = []
        
        self.sc = {}
        self.fsize = {}        
        
        self.filehistory = wx.FileHistory()
        self.filehistory.UseMenu(self.file_sub)
        self.filehistory.AddFilesToMenu()
        
        self.menu_items = [
            self.cleaner,
            self.cyr_to_ansi,
            self.cyr_to_utf,
            self.export_zip,
            self.fixer,
            self.merger,
            self._regex,
            self.specials,
            self.to_ansi,
            self.to_cyrillic,
            self.to_utf8,
            self.transcrib,
        ]

        ## MENU EVENTS ##############################################################################
        self.Bind(wx.EVT_MENU, self.onOpen, id=self.fopen.GetId())
        self.Bind(wx.EVT_MENU, self.onReload, id=self.reload.GetId())
        self.Bind(wx.EVT_MENU, self.onSave, id=self.save.GetId())
        self.Bind(wx.EVT_MENU, self.onSaveAs, id=self.save_as.GetId())
        self.Bind(wx.EVT_MENU, self.exportZIP, id=self.export_zip.GetId())
        self.Bind(wx.EVT_MENU, self.onCloseFile, id=self.close.GetId())
        self.Bind(wx.EVT_MENU, self.onQuit, id=self.quit_program.GetId())
        #############################################################################################
        self.Bind(wx.EVT_MENU, self.clearUndoRedo, id=self.clear.GetId())
        self.Bind(wx.EVT_MENU, self.onReloadText, id=self.reloadtext.GetId())
        self.Bind(wx.EVT_MENU, self.undoAction, id=self.undo.GetId())
        self.Bind(wx.EVT_MENU, self.redoAction, id=self.redo.GetId())
        #############################################################################################
        self.Bind(wx.EVT_MENU, self.toCyrillic, id=self.to_cyrillic.GetId())
        self.Bind(wx.EVT_MENU, self.toANSI, id=self.to_ansi.GetId())
        self.Bind(wx.EVT_MENU, self.toUTF, id=self.to_utf8.GetId())
        self.Bind(wx.EVT_MENU, self.onTranscribe, id=self.transcrib.GetId())
        self.Bind(wx.EVT_MENU, self.onRepSpecial, id=self.specials.GetId())
        self.Bind(wx.EVT_MENU, self.onCleanup, id=self.cleaner.GetId())
        self.Bind(wx.EVT_MENU, self.applyRegex, id=self._regex.GetId())
        self.Bind(wx.EVT_MENU, self.onCyrToANSI, id=self.cyr_to_ansi.GetId())
        self.Bind(wx.EVT_MENU, self.onCyrToUTF, id=self.cyr_to_utf.GetId())
        self.Bind(wx.EVT_MENU, self.onMergeLines, id=self.merger.GetId())
        #############################################################################################
        self.Bind(wx.EVT_MENU, self.onSelectFont, id=self.fonts.GetId())
        self.Bind(wx.EVT_MENU, self.utfSetting, id=-1)
        self.Bind(wx.EVT_MENU, self.showLog, id=-1)
        self.Bind(wx.EVT_MENU, self.onFixerSettings, id=self.fixer.GetId())
        self.Bind(wx.EVT_MENU, self.editShortcuts, id=self.shortcuts.GetId())
        self.Bind(wx.EVT_MENU, self.onMergerSettings, id=self.merger_pref.GetId())
        self.Bind(wx.EVT_MENU, self.onAbout, id = self.about.GetId())
        self.Bind(wx.EVT_MENU, self.onManual, id=self.manual.GetId())
        ## TOOLBAR EVENTS ###########################################################################
        self.Bind(wx.EVT_TOOL, self.onOpen, id=1001)
        self.Bind(wx.EVT_TOOL, self.onSave, id=1010)
        self.Bind(wx.EVT_TOOL, self.toCyrillic, id=1002)
        self.Bind(wx.EVT_TOOL, self.toANSI, id=1003)
        self.Bind(wx.EVT_TOOL, self.toUTF, id=1004)
        self.Bind(wx.EVT_TOOL, self.onTranscribe, id=1005)
        self.Bind(wx.EVT_TOOL, self.onRepSpecial, id=1006)
        self.Bind(wx.EVT_TOOL, self.onCleanup, id=1007)
        self.Bind(wx.EVT_TOOL, self.onQuit, id=1008)
        ## Events other #############################################################################
        self.text_1.Bind(wx.EVT_TEXT, self.removeFiles, id=-1, id2=wx.ID_ANY)
        self.Bind(
            wx.EVT_MENU_RANGE,
            self.onFileHistory,
            id=wx.ID_FILE1,
            id2=wx.ID_FILE9,
        )
        self.comboBox1.Bind(wx.EVT_COMBOBOX, self.onChoice, id=-1, id2=wx.ID_ANY)
        self.Bind(wx.EVT_MENU, self.toCyrUTF8, id=82)
        self.Bind(wx.EVT_MENU, self.onFileSettings, id=83)
        # self.Bind(wx.EVT_MENU, self.ShowDialog, id=84)
        self.Bind(wx.EVT_SIZE, self.size_frame, id=-1)
        self.Bind(wx.EVT_CLOSE, self.onClose, id=wx.ID_ANY)
        #############################################################################################
        entries = [wx.AcceleratorEntry() for i in range(2)]
        entries[0].Set(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('Y'), 82)
        entries[1].Set(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('F'), 83)

        accel_tbl = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel_tbl)
        #############################################################################################
        # drop target
        dt = FileDrop(self.text_1)
        self.text_1.SetDropTarget(dt)
        
        for i in FILE_HISTORY:
            self.filehistory.AddFileToHistory(i)        
        # self.rwFileHistory(FILE_HISTORY)
        
        self.disableTool()

        dispatcher.connect(self.updateStatus, "TMP_PATH", sender=dispatcher.Any)
        dispatcher.connect(self.enKode, "TMP_PATH", sender=dispatcher.Any)
        dispatcher.connect(self.dropedFiles, "droped", sender=dispatcher.Any)
        
    def updateStatus(self, message, msg):
        ''''''
        nlist = FileDrop.nlist
        if nlist:
            for i in nlist:
                self.text_1.SetStyle(i[0], i[1], wx.TextAttr("YELLOW", "BLUE"))
                self.text_1.SetInsertionPoint(i[1])

        if msg[2] == True:
            self.SetStatusText('Multiple files ready for processing')
            self.SetStatusText("", 1)
        else:
            path = message
            enc = printEncoding(msg[1])
            if type(path) == list:
                path = path[-1]
            self.filehistory.AddFileToHistory(FILE_HISTORY[len(FILE_HISTORY) - 1])
            self.SetStatusText(os.path.basename(path))
            self.SetStatusText(enc, 1)
            self.tmpPath = [path]
            self.real_dir = os.path.dirname(msg[0][0])
            
    def enKode(self, message, msg):
            
        self.enableTool()
        
        rlPath = msg[0]
        tpath = message
        if type(tpath) == list: tpath = tpath[-1]
        enc = msg[1]
            
        self.real_dir = os.path.dirname(rlPath[-1])
        
        self.addHistory(self.enchistory, tpath, enc)
        self.real_path = [rlPath]
        if enc == "windows-1251":
            self.to_ansi.Enable(False)
            self.frame_toolbar.EnableTool(1003, False)        
        
    def dropedFiles(self, msg):
        self.droped = msg
        if not self.droped:
            self.multiFile.clear()

    def updateUI(self):
        self.curClr = wx.BLACK
        with shelve.open(filePath('resources', 'var', 'dialog_settings.db'), flag='writeback') as s:
            ex = s['key4']
            new_font = ex['new_font']; fontSize = int(ex['fontSize']); fC = ex['fontColour']; bl = ex['weight']
        
        if bl == 92:
            weight = wx.FONTWEIGHT_BOLD
        else:
            weight = wx.FONTWEIGHT_NORMAL
            
        self.text_1.SetFont(wx.Font(fontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight, 0, new_font))
        
        self.curClr = wx.Colour((fC[0], fC[1], fC[2], fC[3]))   
        self.text_1.SetFont(self.curFont)
        self.text_1.SetForegroundColour(self.curClr)    
        
    def enableTool(self):
                    
        self.frame_toolbar.EnableTool(wx.ID_CLOSE, True)
        self.frame_toolbar.EnableTool(1002, True)   # toCyrillic
        self.frame_toolbar.EnableTool(1003, True)   # toANSI
        self.frame_toolbar.EnableTool(1004, True)   # toUTF
        self.frame_toolbar.EnableTool(1005, True)   # Transcribe
        self.frame_toolbar.EnableTool(1006, True)   # Special
        self.frame_toolbar.EnableTool(1007, True)   # Cleanup
        
        for i in self.menu_items: i.Enable(True)
        
        if PREVIOUS and PREVIOUS[0].enc == "windows-1251":
            self.to_ansi.Enable(False)
            self.frame_toolbar.EnableTool(1003, False)        
    
    def disableTool(self):
        
        self.frame_toolbar.EnableTool(wx.ID_CLOSE, False)
        self.frame_toolbar.EnableTool(1010, False)   # Save
        self.frame_toolbar.EnableTool(1002, False)   # toCyrillic
        self.frame_toolbar.EnableTool(1003, False)   # toANSI
        self.frame_toolbar.EnableTool(1004, False)   # toUTF
        self.frame_toolbar.EnableTool(1005, False)   # Transcribe
        self.frame_toolbar.EnableTool(1006, False)   # Special
        self.frame_toolbar.EnableTool(1007, False)   # Cleanup
        
        new_items = [self.save, self.save_as, self.reload, self.clear, self.undo, self.redo, self.reloadtext]
        
        for i in new_items: i.Enable(False)
        for t in self.menu_items: t.Enable(False)
        
    def multipleTools(self):
        
        self.disableTool()
        self.frame_toolbar.EnableTool(1002, True)   # toCyrillic
        self.frame_toolbar.EnableTool(1003, True)   # toANSI
        self.frame_toolbar.EnableTool(1004, True)   # toUTF
        
        self.to_cyrillic.Enable(True)
        self.to_utf8.Enable(True)
        self.cyr_to_ansi.Enable(True)
        self.cyr_to_utf.Enable(True)
        self.export_zip.Enable(True)

    def postAction(self, path):
        
        path = self.fStatus(path)
        self.SetStatusText(path)
        
        self.menubar1.Enable(wx.ID_SAVE, True)
        self.menubar1.Enable(wx.ID_SAVEAS, True)
        self.menubar1.Enable(wx.ID_CLOSE, True)
        self.reload.Enable(True)
        self.undo.Enable(True)
        self.redo.Enable(True)
        self.reloadtext.Enable(True)
        self.frame_toolbar.EnableTool(1010, True)  # Save
        self.clear.Enable(True)
        if not self.REDO:
            self.redo.Enable(False)
        if not self.UNDO and not self.REDO:
            self.clear.Enable(False)
        
        self.reloaded = 0
        
    def handleFile(self, filepaths):
        
        def file_go(infile, realF):
            fop = FileOpened(infile)
            enc = fop.findCode()
            text = normalizeText(enc, infile)
            text = text.replace("\r\n", "\n")
            bufferText(text, WORK_TEXT)
            nlist = checkErrors(text)
            self.text_1.SetValue("")
            self.text_1.WriteText(text)
            self.text_1.SetInsertionPoint(0)
            if nlist:
                for i in nlist:
                    self.text_1.SetStyle(
                        i[0], i[1], wx.TextAttr("YELLOW", "BLUE")
                    )
                    self.text_1.SetInsertionPoint(i[1])
            logger.debug(f'File opened: {os.path.basename(infile)}')
            self.addHistory(self.enchistory, infile, enc)
            try:
                self.reloadText[text] = enc
            except Exception as e:
                logger.debug(f"file_go: {e}")
            bufferText(text, self.workText)
            
            undo_redo = [self.UNDO, self.REDO, PREVIOUS]
            for i in undo_redo:
                i.clear()
            
            self.addPrevious("Open", enc, text, self.pre_suffix)
            enc =printEncoding(enc)
            return enc

        def multiple(self, inpath, tmppath):
            path = []
            n_path = []
            for i, x in zip(inpath, tmppath):
                path.append(i)
                n_path.append(x)
                if os.path.isfile(i):
                    shutil.copy(i, x)
            return path, n_path

        inpaths = [x for x in filepaths]
        
        tmp_path = [
            os.path.join(self.location, os.path.basename(item))
            for item in inpaths
        ]  # sef.locatin is tmp/
        if len(inpaths) == 1:  # Jedan ulazni fajl, ZIP ili TXT,SRT
            path = inpaths[0]
            tpath = tmp_path[0]
            self.tmpPath.append(tpath)
            FILE_HISTORY.append(path)
            self.filehistory.AddFileToHistory(path)
            if not zipfile.is_zipfile(path):
                shutil.copy(path, tpath)
                self.tmpPath.clear()
                self.real_path.clear()                
                enc = file_go(tpath, path)  # U tmp/ folderu
                self.real_path.append(path)
                self.tmpPath.append(tpath)
                self.SetStatusText(os.path.basename(tpath))
                self.SetStatusText(enc, 1)
            elif zipfile.is_zipfile(path):

                fop = FileOpened(path)
                try:
                    outfile, rfile = fop.isCompressed()  # U tmp/ folderu
                except:
                    logger.debug(f'{path}: No files selected.')
                    if not PREVIOUS:
                        return
                    FILE_HISTORY.pop()
                    self.real_path.clear()
                    self.tmpPath.clear()
                    FH = FILE_HISTORY[-1]
                    fop = FileOpened(FH)
                    if zipfile.is_zipfile(FH):
                        o, u = fop.isCompressed()
                        file_go(o[0], u[0])
                        self.tmpPath.append(o[0])
                    else:
                        file_go(os.path.join(self.location, FH), FH)
                        self.tmpPath.append(os.path.join(self.location, FH))
                    self.real_path.append(FH)
                    self.reloadtext.Enable(False)
                    return
                else:
                    if len(outfile) == 1:  # Jedan fajl u ZIP-u
                        self.real_path.clear()
                        self.tmpPath.clear()
                        enc = file_go(outfile[0], rfile)
                        self.real_path.append(path)
                        self.tmpPath.append(outfile[0])
                        self.SetStatusText(os.path.basename(outfile[0]))
                        self.SetStatusText(enc, 1)
                    elif len(outfile) > 1:  # Više fajlova u ZIP-u
                        self.text_1.SetValue('Files List:\n')
                        for i in range(len(outfile)):
                            name = os.path.basename(outfile[i])
                            fop = FileOpened(path=outfile[i])
                            enc = fop.findCode()
                            normalizeText(enc, outfile[i])
                            self.enchistory[outfile[i]] = enc
                            self.text_1.AppendText('\n')
                            self.text_1.AppendText(name)
                            self.multiFile[outfile[i]] = enc
                        logger.debug(
                            'FileHandler: Ready for multiple files.'
                        )
                        self.enableTool()
                        self.tmpPath.clear()
                        self.real_path.clear()
                        self.SetStatusText('Files ready for processing')

        elif len(inpaths) > 1:  # Više selektovanih ulaznih fajlova
            paths_in, paths_out = multiple(self, inpaths, tmp_path)
            self.real_path = paths_in[-1]
            # if not any(zipfile.is_zipfile(x) for x in paths_in):
            self.text_1.SetValue('Files List:\n')
            self.multipleTools()

            for i in range(len(paths_in)):

                fpath = paths_out[i]

                if zipfile.is_zipfile(fpath):
                    fop = FileOpened(fpath)
                    try:
                        outfile, rfile = fop.isCompressed()
                    except TypeError as e:
                        logger.debug(f'[{e}]({fpath}): None selected.')
                    except Exception as e:
                        logger.error(f"({fpath} [{e}])")
                    except:
                        logger.debug(f'{fpath}: No files selected.')
                    else:
                        if len(outfile) == 1:  # Jedan fajl
                            fop = FileOpened(path=outfile[0])
                            enc = fop.findCode()
                            normalizeText(enc, outfile[0])
                            self.enchistory[outfile[0]] = enc
                            self.text_1.AppendText('\n')
                            self.text_1.AppendText(
                                os.path.basename(outfile[0])
                            )
                            self.multiFile[outfile[0]] = enc
                        elif len(outfile) > 1:  # Više fajlova
                            for i in range(len(outfile)):
                                fpath = outfile[i]
                                fop = FileOpened(fpath)
                                enc = fop.findCode()
                                normalizeText(enc, fpath)
                                self.enchistory[fpath] = enc
                                self.text_1.AppendText('\n')
                                self.text_1.AppendText(
                                    os.path.basename(fpath)
                                )
                                self.multiFile[fpath] = enc
                else:  # Nije ZIP
                    name = os.path.basename(fpath)
                    fop = FileOpened(fpath)
                    enc = fop.findCode()
                    normalizeText(enc, fpath)
                    self.text_1.AppendText("\n")
                    self.text_1.AppendText(name)
                    self.enchistory[fpath] = enc
                    self.multiFile[fpath] = enc
                    self.reloadText[name] = enc

            self.multipleTools()
            logger.debug('FileHandler: Ready for multiple files')
            self.SetStatusText('Files ready for processing')
    

    def onOpen(self, event):
        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and not self.previous_action
        ):
            dl1 = wx.MessageBox(
                "Current content has not been saved! Proceed?",
                "Please confirm",
                wx.ICON_QUESTION | wx.YES_NO,
                self,
            )
            if dl1 == wx.NO:
                return

        dlgOpen = wx.FileDialog(
            self,
            "Otvori novi fajl",
            style=wx.FD_OPEN | wx.FD_MULTIPLE,
            wildcard=self.wildcard,
        )
        if dlgOpen.ShowModal() == wx.ID_OK:
            self.tmpPath.clear()
            if len(self.multiFile) >= 1:
                self.multiFile.clear()
                self.previous_action.clear()
                self.enchistory.clear()
            filepath = dlgOpen.GetPaths()  # Get the file location
            if len(filepath) == 1:
                real_path = filepath[-1]
                self.real_path = [real_path]
                self.real_dir = os.path.dirname(real_path)
            else:
                for fpath in filepath:
                    self.real_path.append(fpath)
                self.real_dir = os.path.dirname(self.real_path[-1])
            self.handleFile(filepath)
            self.enableTool()
            dlgOpen.Destroy()

        event.Skip()
        
    def onReload(self, event):
        
        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
        ):
            if self.ShowDialog() == False:
                return
        if zipfile.is_zipfile(self.real_path[0]):
            with zipfile.ZipFile(self.real_path[0], 'r') as zf:
                if len(zf.namelist()) >= 2:
                    self.clearUndoRedo()
                    self.reload.Enable(False)
                    self.reloadtext.Enable(False)
                    return
        if self.real_path:
            self.handleFile(self.real_path)
        else:
            self.reload.Enable(False)
            return
        path = self.tmpPath[-1]
        enc = self.enchistory[path]            
                
        logger.debug(f'Reloaded {os.path.basename(path)}, encoding: {enc}')
        self.clearUndoRedo()
        enc = printEncoding(enc)
        self.SetStatusText(enc, 1)

        event.Skip()
        
    def onReloadText(self, event):
        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
        ):
            if self.ShowDialog() == False:
                return
        path = self.tmpPath[-1]
        if PREVIOUS:
            enc = PREVIOUS[0].enc
            self.pre_suffix = PREVIOUS[0].psuffix
                
        if os.path.isfile(os.path.join('resources', 'var', 'r_text0.pkl')):
            with open(
                os.path.join('resources', 'var', 'r_text0.pkl'), 'rb'
            ) as f:
                d = pickle.load(f)
            text = list(d.items())[0][0]
            enc = list(d.items())[0][1]
            self.text_1.SetValue(text)
            writeTempStr(path, text, enc)
            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)
            self.reloaded += 1
        else:
            text = list(self.reloadText.items())[0][0]
            enc = list(self.reloadText.items())[0][1]            
            self.text_1.SetValue(text)
            writeTempStr(path, text, enc)
            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)
            self.reloaded += 1
        
        self.REDO.clear() 
        logger.debug(f'Reloaded {os.path.basename(path)}, encoding: {enc}')
        
        self.SetStatusText(printEncoding(enc), 1)
        self.clearUndoRedo()
        self.addHistory(self.enchistory, path, enc)
        self.addPrevious("Open", enc, text, self.pre_suffix)
        self.enableTool()
        event.Skip()

    def onSave(self, event):
        
        tpath, enc = self.PathEnc()
        if tpath and enc:
            enc = self.enchistory[tpath]
        
            fname, nsuffix = newName(tpath, self.pre_suffix, multi=False)
            # Puna putanja sa imenom novog fajla
            outpath = nameDialog(fname, nsuffix, self.real_dir)
            if outpath:
                text = self.workText.getvalue()
                writeToFile(text, outpath, enc, multi=False)
                self.reloadText[text] = enc
                if os.path.isfile(outpath):
                    logger.debug(f"File saved: {outpath}")
                    fpath = os.path.basename(outpath)
                    sDlg = wx.MessageDialog(
                        self,
                        "Fajl je uspešno sačuvan\n{}".format(fpath),
                        'SubtitleConverter',
                        wx.OK | wx.ICON_INFORMATION
                    )
                    sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[outpath] = self.newEnc
                self.MenuBar.Enable(wx.ID_SAVE, False)
                self.MenuBar.Enable(wx.ID_SAVEAS, False)
                self.frame_toolbar.EnableTool(1010, False)
                self.reload.Enable(True)
                self.reloadtext.Enable(True)
                
        event.Skip()

    def onSaveAs(self, event):
        
        sas_wildcard = "SubRip (*.srt)|*.srt|MicroDVD (*.sub)|*.sub|Text File\
        (*.txt)|*.txt|All Files (*.*)|*.*"
        real_dir = self.real_dir
        dlg = wx.FileDialog(
            self,
            message="Save file as ...",
            defaultDir=real_dir,
            defaultFile="",
            wildcard=sas_wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )
        try:
            if self.real_path:
                name = os.path.basename(self.real_path[-1])
                fname, nsuffix = newName(name, self.pre_suffix, multi=False)
                fname = fname + nsuffix
            else:
                fname = 'Untitled.txt'
        except IOError as e:
            logger.debug("On save as IOError({0}):".format(e))
        except IndexError as e:
            logger.debug("On save as IndexError({0}):".format(e))
        dlg.SetFilename(fname)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                text = self.workText.getvalue()
            else:
                text = self.text_1.GetValue()
            writeToFile(text, path, self.newEnc, multi=False)
            self.reloadText[text] = self.newEnc
            if os.path.isfile(path):
                logger.debug(f"File saved sucessfully. {path}")
                sDlg = wx.MessageDialog(
                    self,
                    'Fajl je uspešno sačuvan\n{}'.format(
                        os.path.basename(path)
                    ),
                    'SubtitleConverter',
                    wx.OK | wx.ICON_INFORMATION,
                )
                sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[path] = self.newEnc
                self.MenuBar.Enable(wx.ID_SAVE, False)
                self.MenuBar.Enable(wx.ID_SAVEAS, False)
                self.frame_toolbar.EnableTool(1010, False)
                self.reload.Enable(True)
                # self.saved += 1
                # self.resetTool()
        else:
            dlg.Destroy()
        event.Skip()

    def onClose(self, event):  
        ''''''
        with open(filePath("resources", "var", "set_size.pkl"), "wb") as wf:
            pickle.dump(self.fsize, wf)
        self.rwFileHistory(FILE_HISTORY)
        
        self.Destroy()

    def onQuit(self, event):
        ''''''
        with open(filePath("resources", "var", "set_size.pkl"), "wb") as wf:
            pickle.dump(self.fsize, wf)
        self.rwFileHistory(FILE_HISTORY)
        
        tval = self.text_1.GetValue()
        
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and not PREVIOUS[-1].action == "toCyrUTF8"
        ):
            dl1 = wx.MessageBox(
                "Current content has not been saved! Proceed?",
                "Please confirm",
                wx.ICON_QUESTION | wx.YES_NO,
                self,
            )
            if dl1 == wx.NO:
                return
            else:
                self.Destroy()
        else:
            self.Destroy()
        event.Skip()

    def clearUndoRedo(self):
        '''CLear Undo-Redo history'''
        self.UNDO.clear()
        self.REDO.clear()
        # PREVIOUS.clear()
        self.undo.Enable(False)
        self.redo.Enable(False)
        self.clear.Enable(False)
        
    def toANSI(self, event):
        
        with shelve.open(
            os.path.join("resources", "var", "dialog_settings.db"),
            flag='writeback',
        ) as sp:
            ex = sp['key5']
            value4_s = ex['lat_ansi_srt']

        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toANSI_multiple()
        else:
            self.newEnc = 'windows-1250'
            self.pre_suffix = value4_s

            if entered_enc == self.newEnc:
                logger.debug(f"toANSI, ecoding is already: {entered_enc}")
                InfoDlg = wx.MessageDialog(
                    self,
                    f"Tekst je već enkoding {entered_enc.upper()}.\nNastavljate?",
                    "SubtitleConverter",
                    style=wx.OK
                    | wx.CANCEL
                    | wx.CANCEL_DEFAULT
                    | wx.ICON_INFORMATION,
                )
                if InfoDlg.ShowModal() == wx.ID_CANCEL:
                    return
                else:
                    InfoDlg.Destroy()

            def ansiAction(inpath):
                
                if not entered_enc == 'windows-1251':
                    logger.debug(
                        f'toANSI: {os.path.basename(inpath)}, {entered_enc}'
                    )

                text = WORK_TEXT.getvalue()
                
                text,msg = rplStr(text, entered_enc)
                text = text.replace('?', '¬')
                text = bufferCode(text, self.newEnc)
                text = fixI(text, self.newEnc)
                error_text = checkFile(
                    inpath, inpath, text, multi=False
                )
                text = displayError(
                    text,
                    self.text_1,
                    self.real_dir,
                    inpath,
                    self.newEnc,
                    multi=False,
                )

                self.bytesToBuffer(text, self.newEnc)
                self.tmpPath.append(inpath)
                if text:
                    msginfo = wx.MessageDialog(
                        self,
                        f'Tekst će biti sačuvan kao: {self.newEnc.upper()}.',
                        'SubtitleConverter',
                        wx.OK | wx.ICON_INFORMATION,
                    )
                    msginfo.ShowModal()
                    bufferText(text, self.workText)
                    bufferText(text, WORK_TEXT)
                    
                return text, error_text

            def postAnsi():
                p = self.fStatus(path)
                self.SetStatusText(p)
                self.SetStatusText(self.newEnc, 1)
                self.menubar1.Enable(wx.ID_SAVE, True)
                self.menubar1.Enable(wx.ID_SAVEAS, True)
                self.menubar1.Enable(wx.ID_CLOSE, True)
                self.reload.Enable(True)
                self.frame_toolbar.EnableTool(1010, True)  # Save
                self.frame_toolbar.EnableTool(101, True)
                self.undo.Enable(True)
                self.redo.Enable(True)
                self.reloadtext.Enable(True)
                self.reload.Enable(True)
                self.addPrevious("toANSI", self.newEnc, text, self.pre_suffix)
                self.addHistory(self.enchistory, path, self.newEnc)
                self.reloaded = 0
                
            def dialog1(text_1):
                ErrorDlg = wx.MessageDialog(
                    self,
                    text_1,
                    "SubtitleConverter",
                    style=wx.OK
                    | wx.CANCEL
                    | wx.CANCEL_DEFAULT
                    | wx.ICON_INFORMATION,
                )
                if ErrorDlg.ShowModal() == wx.ID_OK:
                    return True

            text = self.workText.getvalue()
            zbir_slova, procent, chars = checkChars(text)

            # ---------------------------------------------------------------------------------------#
            if zbir_slova == 0 and procent == 0:
                text, error_text = ansiAction(path)
                if error_text:
                    ErrorDlg = wx.MessageDialog(
                        self,
                        error_text,
                        "SubtitleConverter",
                        wx.OK | wx.ICON_ERROR,
                    )
                    ErrorDlg.ShowModal()
                    self.Error_Text = error_text
                postAnsi()
            # ---------------------------------------------------------------------------------------#
            elif procent > 0:
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                f_procent = f'Najmanje {procent} % teksta.\nIli najmanje [ {zbir_slova} ] znakova.'
                ErrorText = "Greška:\n\nUlazni fajl sadrži ćiriliči alfabet.\n\n{}\n{}\n\nNastavljate?\n".format(
                    f_procent, ",".join(chars)
                )
                dlg = dialog1(ErrorText)
                if dlg == True:
                    if procent >= 50:
                        ErrorDlg = wx.MessageDialog(
                            self,
                            "Too many errors!\n\nAre you sure you want to proceed?\n",
                            "SubtitleConverter",
                            style=wx.CANCEL
                            | wx.CANCEL_DEFAULT
                            | wx.OK
                            | wx.ICON_ERROR,
                        )
                        if ErrorDlg.ShowModal() == wx.ID_CANCEL:
                            return
                    text, error_text = ansiAction(path)
                    if error_text:
                        ErrorDlg = wx.MessageDialog(
                            self,
                            error_text,
                            "SubtitleConverter",
                            wx.OK | wx.ICON_ERROR,
                        )
                        ErrorDlg.ShowModal()
                        self.Error_Text = error_text
                    postAnsi()
            # ---------------------------------------------------------------------------------------#
            elif zbir_slova > 0:
                f_zbir = 'Najmanje [ {} ] znakova.'.format(zbir_slova)
                ErrorText = "Greška:\n\nUlazni fajl sadrži ćiriliči alfabet.\n{}\n{}\n\nNastavljate?\n".format(
                    f_zbir, ",".join(chars)
                )
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                dlg = dialog1(ErrorText)
                if dlg == True:
                    text, error_text = ansiAction(path)
                    if error_text:
                        ErrorDlg = wx.MessageDialog(
                            self,
                            error_text,
                            "SubtitleConverter",
                            wx.OK | wx.ICON_ERROR,
                        )
                        ErrorDlg.ShowModal()
                        self.Error_Text = error_text
                    postAnsi()
        event.Skip()

    def toANSI_multiple(self):

        with open(
            os.path.join("resources", "var", "file_ext.pkl"), "rb"
        ) as f:
            ex = pickle.load(f)  # ["key5"]
            value4_s = ex['lat_ansi_srt']

        self.text_1.SetValue("")
        f_text = ["Files Processed:\n"]
        self.PathEnc()

        self.newEnc = 'windows-1250'
        self.pre_suffix = value4_s
        self.tmpPath.clear()

        for key, value in self.multiFile.items():

            path = key
            fpath = os.path.basename(path)
            entered_enc = value

            if entered_enc == 'windows-1251':
                logger.debug(
                    f"------------------------------------------------------\n\
                Encoding is windows-1251! {fpath}"
                )
                self.text_1.AppendText("\n")
                self.text_1.AppendText(fpath + " __skipped_")
                continue

            text = normalizeText(entered_enc, path)
            zbir_slova, procent, chars = checkChars(text)

            def ansiAction(path, text_in):
                if not entered_enc == 'windows-1251':
                    logger.debug(
                        'ToANSI, next input encoding: {}'.format(entered_enc)
                    )
                text,msg = rplStr(text_in, entered_enc)
                text = text.replace('?', '¬')
                text = bufferCode(text, self.newEnc)
                nam, b = newName(path, self.pre_suffix, multi=True)
                newF = os.path.join(self.real_dir, nam + b)
                self.tmpPath.append(newF)
                text = fixI(text, self.newEnc)
                return newF, text

            def postAnsi():
                self.SetStatusText(os.path.basename(newF))
                
            def dialog1(text_1):
                ErrorDlg = wx.MessageDialog(
                    self,
                    text_1,
                    "SubtitleConverter",
                    style=wx.OK
                    | wx.CANCEL
                    | wx.CANCEL_DEFAULT
                    | wx.ICON_INFORMATION,
                )
                if ErrorDlg.ShowModal() == wx.ID_OK:
                    return True

            if zbir_slova == 0 and procent == 0:
                newF, text = ansiAction(path, text)

                error_text = checkFile(path, newF, text, multi=True)

                text = displayError(
                    text,
                    self.text_1,
                    self.real_dir,
                    path,
                    self.newEnc,
                    multi=True,
                )
                writeToFile(text, newF, self.newEnc, multi=True)
                
                f_text.append('\n')
                f_text.append(os.path.basename(newF))
                if error_text:
                    ErrorDlg = wx.MessageDialog(
                        self,
                        error_text,
                        "SubtitleConverter",
                        wx.OK | wx.ICON_ERROR,
                    )
                    ErrorDlg.ShowModal()
                postAnsi()

            elif procent > 0:
                logger.debug(
                    f'ToANSI: Cyrillic alfabet u tekstu: {entered_enc} cyrillic'
                )
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                f_procent = 'Najmanje {} % teksta.\nIli najmanje [ {} ] znakova.'.format(
                    procent, zbir_slova
                )
                ErTxt = "Greška:\n\n{0}\nsadrži ćiriliči alfabet.\n{1}\n{2}\n\nNastavljate?\n".format(
                    os.path.basename(path), f_procent, ",".join(chars)
                )

                dlg = dialog1(ErTxt)

                if dlg == True:
                    if procent >= 50:
                        ErrorDlg = wx.MessageDialog(
                            self,
                            "Too many errors!\n\nAre you sure you want to proceed?\n",
                            "SubtitleConverter",
                            style=wx.CANCEL
                            | wx.CANCEL_DEFAULT
                            | wx.OK
                            | wx.ICON_ERROR,
                        )
                        if ErrorDlg.ShowModal() == wx.ID_CANCEL:
                            continue
                    newF, text = ansiAction(path, text)
                    error_text = checkFile(path, newF, text, multi=True)

                    text = displayError(
                        text,
                        self.text_1,
                        self.real_dir,
                        path,
                        self.newEnc,
                        multi=True,
                    )
                    writeToFile(text, newF, self.newEnc, multi=True)

                    f_text.append('\n')
                    f_text.append(os.path.basename(newF))
                    if error_text:
                        ErrorDlg = wx.MessageDialog(
                            self,
                            error_text,
                            "SubtitleConverter",
                            wx.OK | wx.ICON_ERROR,
                        )
                        ErrorDlg.ShowModal()
                    postAnsi()

            elif zbir_slova > 0:
                logger.debug(
                    f'ToANSI: Cyrillic alfabet u tekstu: {entered_enc} cyrillic'
                )
                f_zbir = 'Najmanje [ {} ] znakova.'.format(zbir_slova)
                ErTxt = "Greška:\n\n{0}\nsadrži ćiriliči alfabet.\n{1}\n{2}\n\nNastavljate?\n".format(
                    os.path.basename(path), f_zbir, ",".join(chars)
                )

                dlg = dialog1(ErTxt)

                if dlg == True:
                    newF, text = ansiAction(path, text)
                    error_text = checkFile(path, path, text, multi=True)

                    f_text.append('\n')
                    f_text.append(os.path.basename(newF))

                    text = displayError(
                        text,
                        self.text_1,
                        self.real_dir,
                        path,
                        self.newEnc,
                        multi=True,
                    )
                    writeToFile(text, newF, self.newEnc, multi=True)

                    if error_text:
                        ErrorDlg = wx.MessageDialog(
                            self,
                            error_text,
                            "SubtitleConverter",
                            wx.OK | wx.ICON_ERROR,
                        )
                        ErrorDlg.ShowModal()
                    postAnsi()
        for item in f_text:
            self.text_1.WriteText(item)
        self.addPrevious("toANSI_multiple", self.newEnc, "", self.pre_suffix)
        self.SetStatusText('Multiple files done.')
        self.multipleTools()
        
    def toCyrillic(self, event):

        with shelve.open(
            os.path.join("resources", "var", "dialog_settings.db"),
            flag='writeback',
        ) as sp:
            ex = sp['key5']
            value1_s = ex['cyr_ansi_srt']
            value2_s = ex['cyr_utf8_txt']

        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()
        
        if self.preferences.IsChecked(1011):  
            utf8_enc = 'utf-8-sig'
        else:
            utf8_enc = 'utf-8'        
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toCyrillic_multiple()

        else:
            text = WORK_TEXT.getvalue()
            
            self.newEnc = 'windows-1251'
            self.pre_suffix = value1_s
            
            utf8_text = remTag(text)
            self.utf8_latText = utf8_text.encode(
                encoding="utf-8", errors="surrogatepass"
            ).replace(b"\n", b"\r\n")
            
            if text:
                text = text.replace('?', '¬')

            utf_name, suffix = newName(path, value2_s, multi=False)
            utf_path = os.path.join(self.real_dir, (utf_name + suffix))
            
            if self.preferences.IsChecked(1014):
                text = preLatin(text_in=text)
            
            text, msg = changeLetters(text, utf8_enc, reversed_action=False)
            cyr_path = path
            self.cyrUTF = utf_path
            
            writeToFile(text, utf_path, utf8_enc, multi=False)
            
            text = bufferCode(text, self.newEnc)
            
            error_text = checkFile(path, cyr_path, text, multi=False)
            text = displayError(
                text,
                self.text_1,
                self.real_dir,
                path,
                self.newEnc,
                multi=False
            )
            
            bufferText(text, self.workText)
            bufferText(text, WORK_TEXT)
            
            self.bytesToBuffer(text, self.newEnc)
            
            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
                
            self.SetStatusText(os.path.basename(path))
            self.SetStatusText(self.newEnc, 1)
            
            self.postAction(path)
            self.frame_toolbar.EnableTool(1003, False)   # toANSI
            self.to_ansi.Enable(False)
            
            self.addHistory(self.enchistory, path, self.newEnc)
            self.addPrevious("toCYR", self.newEnc, text, self.pre_suffix)
            self.reloaded = 0            
                
        event.Skip()
        
    def toCyrillic_multiple(self):

        with open(
            os.path.join("resources", "var", "file_ext.pkl"), "rb"
        ) as f:
            ex = pickle.load(f)  # ["key5"]
            value1_s = ex['cyr_ansi_srt']
            value2_s = ex['cyr_utf8_txt']

        self.text_1.SetValue("")
        
        if self.preferences.IsChecked(1011):
            utf8_enc = 'utf-8-sig'
        else:
            utf8_enc = 'utf-8'        
        
        self.newEnc = 'windows-1251'
        self.pre_suffix = value1_s
        f_text = ["Files Processed:\n"]

        self.PathEnc()

        self.tmpPath.clear()
        self.cyrUTFmulti.clear()
        
        for key, value in self.multiFile.items():

            path = key
            entered_enc = value

            file_suffix = os.path.splitext(path)[-1]

            text = normalizeText(entered_enc, path)
            if text:
                text = text.replace('?', '¬')

            utfText, suffix = newName(path, value2_s, multi=True)

            utf_path = os.path.join(self.real_dir, utfText + suffix)
            self.cyrUTFmulti.append(utf_path)

            # if os.path.exists(utf_path):
            # nnm = fproc.nameCheck(os.path.basename(utf_path), self.real_dir, suffix)
            # utf_path = '{0}_{1}{2}'.format(utf_path, nnm, suffix)

            text,msg = changeLetters(text, utf8_enc, reversed_action=False)
            
            writeToFile(text, utf_path, utf8_enc, multi=True)
            
            cyr_name, cyr_suffix = newName(path, value1_s, multi=True)
            cyr_path = os.path.join(self.real_dir, cyr_name + file_suffix)

            self.tmpPath.append(cyr_path)
            
            text_ansi = bufferCode(text, self.newEnc)
            
            error_text = checkFile(utf_path, cyr_path, text_ansi, multi=True)
            text = displayError(
                text_ansi,
                self.text_1,
                self.real_path,
                cyr_path,
                self.newEnc,
                multi=True,
            )
            
            writeToFile(text_ansi, cyr_path, self.newEnc, multi=True)
            
            f_text.append("\n")
            f_text.append(os.path.basename(cyr_path))

            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
                self.Error_Text = error_text

            self.enc = self.newEnc
            self.SetStatusText(os.path.basename(cyr_path))
            
        for item in f_text:
            self.text_1.WriteText(item)
    
        self.addPrevious("toCYR_multiple", self.newEnc, "", file_suffix)
        self.reloaded = 0
        self.SetStatusText('Multiple files done.')
        self.multipleTools()
        self.frame_toolbar.EnableTool(1003, False)
        self.to_ansi.Enable(False)
    
    def toCyrUTF8(self, event):
        ''''''
        with shelve.open(
            os.path.join("resources", "var", "dialog_settings.db"),
            flag='writeback',
        ) as sp:
            ex = sp['key5']
            value_s = ex["cyr_utf8_srt"]

        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()
        
        if self.preferences.IsChecked(1011):  
            utf8_enc = 'utf-8-sig'
        else:
            utf8_enc = 'utf-8'        
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toCyrUTF8_multiple()

        else:
            text = WORK_TEXT.getvalue()
            
            self.newEnc = utf8_enc
            self.pre_suffix = value_s
            
            utf8_text = remTag(text)
            self.utf8_latText = utf8_text.encode(
                encoding="utf-8", errors="surrogatepass"
            ).replace(b"\n", b"\r\n")
            
            if text:
                text = text.replace('?', '¬')

            utf_name, suffix = newName(path, value_s, multi=False)
            utf_path = os.path.join(self.real_dir, (utf_name + suffix))
            
            if self.preferences.IsChecked(1014):
                text = preLatin(text_in=text)
            
            text, msg = changeLetters(text, self.newEnc, reversed_action=False)
            cyr_path = path
            self.cyrUTF = utf_path
            
            text = bufferCode(text, self.newEnc)
            
            error_text = checkFile(path, cyr_path, text, multi=False)
            text = displayError(
                text,
                self.text_1,
                self.real_dir,
                path,
                self.newEnc,
                multi=False
            )
            
            bufferText(text, self.workText)
            bufferText(text, WORK_TEXT)
            
            self.bytesToBuffer(text, self.newEnc)

            writeToFile(text, utf_path, utf8_enc, multi=False)
            
            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
                
            self.SetStatusText(os.path.basename(path))
            enc = printEncoding(self.newEnc)
            self.SetStatusText(enc, 1)
            
            self.postAction(path)
            self.frame_toolbar.EnableTool(1003, False)   # toANSI
            self.to_ansi.Enable(False)
            
            self.addHistory(self.enchistory, path, self.newEnc)
            self.addPrevious("toCyrUTF8", self.newEnc, text, self.pre_suffix)
            self.reloaded = 0            
                
        event.Skip()
        
    def toCyrUTF8_multiple(self):
        """"""
        with open(
            os.path.join("resources", "var", "file_ext.pkl"), "rb"
        ) as f:
            ex = pickle.load(f)  # ["key5"]
            value_s = ex["cyr_utf8_srt"]

        self.text_1.SetValue("")
        
        if self.preferences.IsChecked(1011):  
            utf8_enc = 'utf-8-sig'
        else:
            utf8_enc = 'utf-8'        
        
        self.newEnc = utf8_enc
        self.pre_suffix = value_s
        f_text = ["Files Processed:\n"]

        self.PathEnc()

        self.tmpPath.clear()
        self.cyrUTFmulti.clear()
        
        for key, value in self.multiFile.items():

            path = key
            entered_enc = value

            file_suffix = os.path.splitext(path)[-1]

            text = normalizeText(entered_enc, path)
            
            if text:
                text = text.replace('?', '¬')

            utfText, suffix = newName(path, value_s, multi=True)

            utf_path = os.path.join(self.real_dir, utfText + suffix)
            self.cyrUTFmulti.append(utf_path)

            text,msg = changeLetters(text, self.newEnc, reversed_action=False)
            
            text = bufferCode(text, self.newEnc)
            
            cyr_name, cyr_suffix = newName(path, value_s, multi=True)
            cyr_path = os.path.join(self.real_dir, cyr_name + file_suffix)

            self.tmpPath.append(cyr_path)
            
            error_text = checkFile(utf_path, cyr_path, text, multi=True)
            text = displayError(
                text,
                self.text_1,
                self.real_path,
                cyr_path,
                self.newEnc,
                multi=True,
            )
            
            writeToFile(text, utf_path, self.newEnc, multi=True)
            
            f_text.append("\n")
            f_text.append(os.path.basename(cyr_path))

            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
                self.Error_Text = error_text

            self.enc = self.newEnc
            self.SetStatusText(os.path.basename(cyr_path))
        
        for item in f_text:
            self.text_1.WriteText(item)
        
        self.SetStatusText(printEncoding(self.newEnc), 1)
        self.addPrevious("toCyrUTF8_multiple", self.newEnc, "", file_suffix)
        self.reloaded = 0
        self.SetStatusText('Multiple files done.')
        self.multipleTools()
        self.frame_toolbar.EnableTool(1003, False)
        self.to_ansi.Enable(False)        
        
        
    def toUTF(self, event):

        with shelve.open(
            filePath("resources", "var", "dialog_settings.db"),
            flag='writeback',
        ) as sp:
            ex = sp['key5']
            value1_s = ex['lat_utf8_srt']

        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and self.reloaded == 0
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toUTF_multiple()
        else:
            cyr_utf = ""
            if PREVIOUS:
                cyr_utf = PREVIOUS[len(PREVIOUS)-2].action
            
            self.pre_suffix = value1_s
            
            if self.preferences.IsChecked(1011):
                self.newEnc = 'utf-8-sig'
            else:
                self.newEnc = 'utf-8'

            if (
                entered_enc == "utf-8"
                or entered_enc == "utf-8-sig"
                and cyr_utf != "toCYR"
            ):
                code = printEncoding(entered_enc)
                logger.debug(f"toUTF: Encoding is {entered_enc}.")
                
            text = WORK_TEXT.getvalue()
            
            text = bufferCode(text, self.newEnc)  # change to newEnc
            text = fixI(text, self.newEnc)
            bufferText(text, self.workText)
            self.text_1.SetValue(text)
            
            if text:
                code = printEncoding(self.newEnc)
                
                bufferText(text, WORK_TEXT)
                self.bytesToBuffer(text, self.newEnc)
                
                msginfo = wx.MessageDialog(
                    self,
                    f'Tekst će biti sačuvan kao: {code}.',
                    'SubtitleConverter',
                    wx.OK | wx.ICON_INFORMATION,
                )
                msginfo.ShowModal()

            self.SetStatusText(code, 1)
            self.addPrevious("toUTF", self.newEnc, text, self.pre_suffix)
            self.addHistory(self.enchistory, path, self.newEnc)
            self.postAction(path)
            
        event.Skip()
        
    def toUTF_multiple(self):
        
        with open(
            os.path.join("resources", "var", "file_ext.pkl"), "rb"
        ) as f:
            ex = pickle.load(f)  # ["key5"]
            value1_s = ex["lat_utf8_srt"]

        self.text_1.SetValue("")
        
        self.PathEnc()

        self.tmpPath.clear()
        self.pre_suffix = value1_s

        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'
        entered_enc = ""
        f_text = ["Files Processed:\n"]
        for key, value in self.multiFile.items():

            path = key
            entered_enc = value

            text = normalizeText(entered_enc, path)
            if text:
                text = text.replace('?', '¬')

            nam, b = newName(path, self.pre_suffix, multi=True)
            newF = '{0}{1}'.format(filePath(self.real_dir, nam), b)

            text = bufferCode(text, self.newEnc)
            self.tmpPath.append(newF)  # VAZNO
            text = fixI(text, self.newEnc)
            
            error_text = checkFile(path, newF, text, multi=True)

            text = displayError(
                text,
                self.text_1,
                self.real_dir,
                newF,
                self.newEnc,
                multi=True,
            )

            writeToFile(text, newF, self.newEnc, multi=True)

            f_text.append('\n')
            f_text.append(os.path.basename(newF))
            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
            self.SetStatusText(os.path.basename(newF))
        
        for item in f_text:
            self.text_1.WriteText(item)
        self.multipleTools()
        if entered_enc == "windows-1251":
            self.frame_toolbar.EnableTool(1003, False)
            self.to_ansi.Enable(False)
            msginfo = wx.MessageDialog(
                self,
                f'Novi enkoding: {self.newEnc} Ćirilica.',
                'SubtitleConverter',
                wx.OK | wx.ICON_INFORMATION,
            )
            msginfo.ShowModal()
        self.reloaded = 0
        self.SetStatusText(printEncoding(self.newEnc), 1)
        self.addPrevious("toUTF_multiple", self.newEnc, "", self.pre_suffix)
        self.SetStatusText('Multiple files done.')
        
    def onTranscribe(self, event):
        
        with shelve.open(
            os.path.join("resources", "var", "dialog_settings.db"),
            flag='writeback',
        ) as sp:
            ex = sp['key5']
            value1_s = ex['transcribe']

        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and self.reloaded == 0
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1:
            return

        self.pre_suffix = value1_s

        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'

        text = WORK_TEXT.getvalue()
        # text = self.text_1.GetValue()

        # text = bufferCode(text, self.newEnc)
        text = fixI(text, self.newEnc)

        num, text = zameniImena(text)

        if num > 28 or num < 28 and num > 2:
            msginfo = wx.MessageDialog(
                self,
                f'Zamenjenih objekata\nukupno [ {num} ]',
                'SubtitleConverter',
                wx.OK | wx.ICON_INFORMATION,
            )
            msginfo.ShowModal()

        text,msg = rplStr(text, self.newEnc)

        self.text_1.SetValue(text)
        bufferText(text, WORK_TEXT)
        bufferText(text, self.workText)
        self.bytesToBuffer(text, self.newEnc)
        
        self.SetStatusText(printEncoding(self.newEnc), 1)

        self.postAction(path)

        self.addPrevious("Transcribe", self.newEnc, text, self.pre_suffix)
        self.addHistory(self.enchistory, path, self.newEnc)
        
        event.Skip()
        
    def onRepSpecial(self, event):
        
        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and self.reloaded == 0
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1:
            return

        self.newEnc = entered_enc
        self.pre_suffix = 'rpl'

        text = WORK_TEXT.getvalue()
        # text = self.text_1.GetValue()

        text = text.replace('?', '¬')

        num, text_o = doReplace(text)
        bufferText(text_o, self.workText)

        error_text = checkFile(path, path, text_o, multi=False)
        text_s = displayError(
            text_o,
            self.text_1,
            self.real_dir,
            path,
            entered_enc,
            multi=False,
        )

        bufferText(text_s, WORK_TEXT)
        bufferText(text_s, self.workText)

        self.bytesToBuffer(text_s, entered_enc)
        
        msginfo = wx.MessageDialog(
            self,
            'Zamenjenih objekata\nukupno [ {} ]'.format(num),
            'SubtitleConverter',
            wx.OK | wx.ICON_INFORMATION,
        )
        msginfo.ShowModal()
        if error_text:
            ErrorDlg = wx.MessageDialog(
                self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR
            )
            ErrorDlg.ShowModal()
            self.Error_Text = error_text
        
        self.SetStatusText(printEncoding(entered_enc), 1)

        self.postAction(path)
        self.addPrevious("repSpec", self.newEnc, text_s, self.pre_suffix)
        self.addHistory(self.enchistory, path, self.newEnc)
        
        event.Skip()
        
    def applyRegex(self, event):
        
        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and self.reloaded == 0
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1:
            return

        self.pre_suffix = "reg"

        text = WORK_TEXT.getvalue()

        d_file = os.path.join("resources", "Regex_def.config")

        with open(d_file, "r", encoding="utf-8") as f_open:

            reg_1 = re.compile('find=|\'|"', re.I)
            cn = 0

            for line in f_open:

                cn += 1
                if line.startswith("#"):
                    continue
                if not line:
                    continue

                line = line.strip().lower()

                if line and not "replace=" in line:
                    logger.debug(
                        f"Apply Regex, missing argument, line {cn}; {d_file}"
                    )

                x = line.split("replace=")

                finds = re.sub(reg_1, '', x[0]).strip()
                reps = re.sub(reg_1, '', x[-1]).strip()

                if reps:
                    x = reps.split("#")
                    if x[-1]:
                        reps = x[0].strip()

                try:
                    if "ignorecase" in reps:
                        reps = reps.replace("ignorecase", "").strip()
                        rflags = (re.M | re.I)
                        reg_def = re.compile(finds, rflags)
                    else:
                        reg_def = re.compile(finds, re.M)

                    text = reg_def.sub(reps, text)

                except Exception as e:
                    error_text = f"Regex error\n\n{d_file}\n{line}: {cn}\n{e}"
                    logger.debug(error_text)
                    ErrorDlg = wx.MessageDialog(
                        None, error_text, "SubConverter", wx.OK | wx.ICON_ERROR
                    )
                    ErrorDlg.ShowModal()
                    
        self.text_1.SetValue(text)
        bufferText(text, WORK_TEXT)
        bufferText(text, self.workText)

        self.bytesToBuffer(text, entered_enc)
        
        self.SetStatusText(os.path.basename(path))
        self.SetStatusText(printEncoding(entered_enc), 1)

        self.postAction(path)

        self.addPrevious("CustomRegex", entered_enc, text, self.pre_suffix)
        self.addHistory(self.enchistory, path, entered_enc)
        
        event.Skip()
        
    def PathEnc(self):
        '''This function returns path and entered_enc'''
        if self.droped:
            self.multiFile.clear()
            self.multiFile.update(self.droped)
            
        path = ""; entered_enc = ""
        if self.tmpPath and not self.multiFile:
            path = self.tmpPath[0]
            entered_enc = self.enchistory[path]
        return path, entered_enc
    
    def fStatus(self, path):
        if type(path) == list:
            path = path[-1]
        p, s = os.path.splitext(path)
        if type(self.real_path[0]) == list:
            self.real_path = self.real_path[0]
        suffix = os.path.splitext(self.real_path[0])[-1]
        if s != suffix and not suffix == ".zip":
            return f"{os.path.basename(p)}{suffix}"
        else: return os.path.basename(path)    
    
    def addHistory(self, hist, path, enc):
        hist[path] = enc
        
    def textToBuffer(self, path, enc):
        
        if enc in codelist:
            error = "surrogatepass"
        else:
            error = "strict"
        try:
            with open(path, mode="r", encoding=enc, errors=error) as f:
                text = f.read()
                self.workText.truncate(0)
                self.workText.seek(0)
                self.workText.write(text)
                self.workText.seek(0)
                text = self.workText.getvalue()
                if text:
                    logger.debug(
                        f"TextToBuffer content: {os.path.basename(path)}"
                    )
            return text
        except Exception as e:
            logger.debug(f"textToBuffer error: {e}")
            
    def bytesToBuffer(self, text, enc):
        '''Returns byte'''
        
        if enc in codelist:
            error = 'surrogatepass'
        else:
            error = 'replace'            
        try:
            self.bytesText.truncate(0)
            self.bytesText.seek(0)
            self.bytesText.write(text.encode(enc, errors=error))
            self.bytesText.seek(0)
        
            return self.bytesText.getvalue()
        
        except Exception as e:
            logger.debug(f"bytesToBuffer error: {e}")
            print("BtB error enc=", enc)
            
    def onCleanup(self, event):
        
        with shelve.open(
            os.path.join("resources", "var", "dialog_settings.db"),
            flag='writeback',
        ) as sp:
            ex = sp['key5']
            ef = sp['key1']
            cb8_s = ef["state8"]
            value1_s = ex['cleanup']

        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and self.reloaded == 0
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1:
            return

        self.newEnc = entered_enc
        self.pre_suffix = value1_s

        text = WORK_TEXT.getvalue()
        # text = self.text_1.GetValue()

        try:
            subs = list(srt.parse(text))

            subs = srt.compose(subs)

            if "repSpec" or "Cleanup" in self.previous_action.keys():
                arg1 = False
            else:
                arg1 = True

            text = cleanUp(subs, arg1)

            deleted, trimmed, text_s = cleanLine(text)

            bufferText(text_s, WORK_TEXT)
            bufferText(text_s, self.workText)
            self.text_1.SetValue(text_s)
            logger.debug(f"CleanUp _1: {sys.exc_info()}")

            self.bytesToBuffer(text_s, entered_enc)
            
            if (deleted + trimmed) == 0:
                msginfo = wx.MessageDialog(
                    self,
                    'Subtitle clean\nno changes made.',
                    'SubtitleConverter',
                    wx.OK | wx.ICON_INFORMATION,
                )
                msginfo.ShowModal()
            else:
                msginfo = wx.MessageDialog(
                    self,
                    f'Subtitles deleted: [{deleted} ]\nSubtitles trimmed: [{trimmed} ]',
                    'SubtitleConverter',
                    wx.OK | wx.ICON_INFORMATION,
                )
                msginfo.ShowModal()
            
            self.SetStatusText(printEncoding(self.newEnc), 1)
            self.addPrevious("Cleanup", self.newEnc, text_s, self.pre_suffix)
            self.addHistory(self.enchistory, path, self.newEnc)
            self.postAction(path)

        except Exception as e:
            logger.debug(f"Cleanup: {e}")
            return
        
        event.Skip()
    
    def onMergeLines(self, event):
        
        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and self.reloaded == 0
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1:
            return

        self.addHistory(self.enchistory, path, entered_enc)
        self.newEnc = entered_enc  # path je u tmp/ folderu

        try:
            with shelve.open(
                filePath('resources', 'var', 'dialog_settings.db'),
                flag='writeback',
            ) as sp:
                ex = sp['key2']
                lineLenght = ex['l_lenght']
                maxChar = ex['m_char']
                maxGap = ex['m_gap']
                file_suffix = ex['f_suffix']
        except IOError as e:
            logger.debug(f"Merger, I/O error: {e}")
        except Exception as e:
            logger.debug(f"Merger, unexpected error: {e}")

        try:
            text = WORK_TEXT.getvalue()
            subs_a = pysrt.from_string(text)

        except IOError as e:
            logger.debug(f"Merger srt, I/O error({e}")
        except Exception as e:
            logger.debug(f"Merger _1, unexpected error: {e}")

        if subs_a[1].start and subs_a[2].start == "00:00:00,000":

            msginfo = wx.MessageDialog(
                self,
                'Erroneous subtitle\n\nAll values are zero!',
                'SubtitleConverter',
                wx.OK | wx.ICON_INFORMATION,
            )
            msginfo.ShowModal()
            return

        self.pre_suffix = file_suffix

        if len(subs_a) > 0:

            myMerger(
                subs_in=subs_a,
                max_time=lineLenght,
                max_char=maxChar,
                _gap=maxGap,
            )

            b1 = len(pysrt.from_string(WORK_TEXT.getvalue()))
            a1 = len(subs_a)

            text = WORK_TEXT.getvalue()
            subs = list(srt.parse(text))
            text = srt.compose(subs)
            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)

            self.bytesToBuffer(text, entered_enc)
            self.text_1.SetValue(text)

            try:
                prf = format(((a1 - b1) / a1 * 100), '.2f')
            except ZeroDivisionError as e:
                logger.debug(f"Merger Error: {e}")
            else:
                logger.debug(
                    f"Merger: Spojenih linija ukupno: {a1-b1}, ili {prf} %"
                )
                sDlg = wx.MessageDialog(
                    self,
                    f"Merged file:\n\nSpojenih linija ukupno: {a1-b1}, ili {prf} %",
                    'SubtitleConverter',
                    wx.OK | wx.ICON_INFORMATION,
                )
                sDlg.ShowModal()
            
            enc = printEncoding(self.newEnc)
            self.SetStatusText(enc, 1)
            self.postAction(path)
            self.addPrevious("Merger", self.newEnc, text, self.pre_suffix)
            
        event.Skip()
    
    def exportZIP(self, event):

        self.PathEnc()

        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.exportZIPmultiple()
        else:
            if self.droped:
                if len(self.droped) > 1:
                    return
            fpath, e = self.PathEnc()
            tpath = os.path.basename(fpath)
            enc = self.newEnc
            sas_wildcard = "ZipArchive (*.zip)|*.zip|All Files (*.*)|*.*"
            
            if len(PREVIOUS) == 1:
                logger.debug(f"Export Zip: Nothing to do.")
                return
            
            dlg = wx.FileDialog(
                self,
                message="Export file as ZIP",
                defaultDir=self.real_dir,
                defaultFile="",
                wildcard=sas_wildcard,
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            )
            try:
                if fpath:
                    fname, nsufix = newName(tpath, self.pre_suffix, multi=False)
            except Exception as e:
                logger.debug(f"On ZIP error({e})")

            dlg.SetFilename(fname)

            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                dirname = os.path.dirname(path)
                name = path

                def data_out(buffer, f_path):
                    if f_path:
                        f = open(f_path, 'rb')
                        b_data = f.read()
                        f.close()
                        return b_data
                    if buffer:
                        a_data = buffer.getvalue()
                        if type(a_data) == str:
                            a_data = a_data.encode(enc)
                        a_data = a_data.replace(b"\n", b"\r\n")
                        buffer.seek(0)
                        return a_data

                if PREVIOUS[-1].action == "toCYR":
                    tUTF = os.path.join("tmp", os.path.basename(self.cyrUTF)) # cyr_UTF-8
                    try:
                        shutil.copy(self.cyrUTF, tUTF)
                    except Exception as e:
                        logger.debug(f"exportZIP error: {e}")
                        self.text_1.SetValue("ERROR\n\nTry different options.")
                        return

                    cyr_file = (
                        fname + os.path.splitext(tpath)[-1]
                    )  # info1 dodaje cyr pre_suffix i file se pise u ZIP pod tim imenom
                    utf8_lat = (
                        os.path.splitext(tpath)[0]
                        + ".utf8"
                        + os.path.splitext(tpath)[-1]
                    )
                    cyr_file = cyr_file.strip('/')
                    utf8_lat = utf8_lat.strip("/")
                    info2 = os.path.basename(tUTF)  # cyrUTF-8
                    info1 = os.path.basename(fpath)  # latFile original
                    izbor = [cyr_file, info2, info1, utf8_lat]
                    
                    f_enc = PREVIOUS[0].enc
                    text = open(fpath, "r", encoding=f_enc).read()
                    text = remTag(text)
                    writeToFile(text, fpath, f_enc, False)
                    
                    dlg = wx.MultiChoiceDialog(
                        self, 'Pick files:', os.path.basename(name), izbor
                    )
                    if dlg.ShowModal() == wx.ID_OK:
                        response = dlg.GetSelections()
                        files = [izbor[x] for x in response]
                        zip_data = []
                        zdata = None        # latFile original
                        tzdata = None       # cyrUTF-8
                        cyrdata = None      # cyrillic text binary
                        utf8ldata = None    # latFile utf-8
                        if not files:
                            return
                        if len(files) == 1:
                            try:
                                if info2 in files:
                                    tzdata = data_out(None, tUTF)
                                    zip_data.append(tzdata)
                                
                                elif info1 in files:
                                    zdata = data_out(None, fpath)
                                    zip_data.append(zdata)
                                
                                elif cyr_file in files:
                                    cyrdata = data_out(self.bytesText, None)
                                    zip_data.append(cyrdata)
                                
                                elif utf8_lat in files:
                                    utf8ldata = self.utf8_latText
                                    zip_data.append(utf8ldata)
                                logger.debug(f"Remove {self.cyrUTF}")
                                os.remove(self.cyrUTF)                                
                            except Exception as e:
                                logger.debug(f"Export ZIP error: {e}")

                        elif len(files) == 2:
                            try:
                                if info1 in files and info2 in files:
                                    tzdata = data_out(None, tUTF)
                                    zdata = data_out(None, fpath)
                                    zip_data.extend((zdata, tzdata))
                                    
                                elif info1 in files and cyr_file in files:
                                    cyrdata = data_out(self.bytesText, None)
                                    zdata = data_out(None, fpath)
                                    zip_data.extend((cyrdata, zdata))
                                
                                elif info1 in files and utf8_lat in files:
                                    zdata = data_out(None, fpath)
                                    utf8ldata = self.utf8_latText
                                    zip_data.extend((zdata, utf8ldata))
                                
                                elif cyr_file in files and info2 in files:
                                    cyrdata = data_out(self.bytesText, None)
                                    tzdata = data_out(None, tUTF)
                                    zip_data.extend((cyrdata, tzdata))
                                
                                elif info2 in files and utf8_lat in files:
                                    tzdata = data_out(None, tUTF)
                                    utf8ldata = self.utf8_latText
                                    zip_data.extend((tzdata, utf8ldata))
                                
                                elif cyr_file in files and utf8_lat in files:
                                    cyrdata = data_out(self.bytesText, None)
                                    utf8ldata = self.utf8_latText
                                    zip_data.extend((cyrdata, utf8ldata))
                                    
                                logger.debug(f"Remove {self.cyrUTF}")
                                os.remove(self.cyrUTF)
                            except Exception as e:
                                logger.debug(f"Export ZIP error: {e}")                            

                        elif len(files) == 3:   # izbor = [cyr_file, info2(tzdata), info1(zdata), utf8_lat]
                            try:
                                if not utf8_lat in files:
                                    zdata = data_out(None, fpath)
                                    tzdata = data_out(None, tUTF)
                                    cyrdata = data_out(self.bytesText, None)
                                    zip_data.extend((cyrdata, tzdata, zdata))
                                
                                elif not cyr_file in files:
                                    tzdata = data_out(None, tUTF)
                                    zdata = data_out(None, fpath)
                                    utf8ldata = self.utf8_latText
                                    zip_data.extend((tzdata, zdata, utf8ldata))
                                
                                elif not info1 in files:
                                    cyrdata = data_out(self.bytesText, None)
                                    tzdata = data_out(None, tUTF)
                                    utf8ldata = self.utf8_latText
                                    zip_data.extend((cyrdata, tzdata, utf8ldata))
                                
                                elif not info2 in files:
                                    zdata = data_out(None, fpath)
                                    cyrdata = data_out(self.bytesText, None)
                                    utf8ldata = self.utf8_latText
                                    zip_data.extend((cyrdata, zdata, utf8ldata))
                                logger.debug(f"Remove {self.cyrUTF}")
                                os.remove(self.cyrUTF)
                            except Exception as e:
                                logger.debug(f"Export ZIP error: {e}")                            

                        elif len(files) == 4:
                            try:
                                utf8ldata = self.utf8_latText
                                zdata = data_out(None, fpath)
                                tzdata = data_out(None, tUTF)
                                cyrdata = data_out(self.bytesText, None)
                                zip_data.extend(
                                    (cyrdata, tzdata, zdata, utf8ldata)
                                )
                                logger.debug(f"Remove {self.cyrUTF}")
                                os.remove(self.cyrUTF)                                
                            except Exception as e:
                                logger.debug(f"Export ZIP error: {e}")                            
                    else:
                        zip_data = []
                        files = []
                        logger.debug("ZIP export: None selected")
                        return
                else:
                    zip_data = []
                    previous_action = PREVIOUS[-1].action
                    if previous_action == 'toCyrUTF8':
                        zdata = data_out(None, self.cyrUTF)
                        zip_data.append(zdata)
                        info1 = os.path.basename(self.cyrUTF).strip('/')
                        files = [info1]
                        os.remove(self.cyrUTF)
                    elif previous_action == "toUTF":
                        tzdata = data_out(self.bytesText, None)
                        zip_data.append(tzdata)
                        suffix = fpath[-4:]
                        if self.preferences.IsChecked(1012):
                            suffix = '.txt'
                        presuffix = self.pre_suffix
                        info2 = (
                            os.path.basename(fpath)[:-3] + presuffix + suffix
                        )
                        files = [info2]
                    else:
                        tzdata = data_out(self.bytesText, None)
                        zip_data.append(tzdata)
                        suffix = fpath[-4:]
                        presuffix = self.pre_suffix
                        info2 = (
                            os.path.basename(fpath)[:-3] + presuffix + suffix
                        )
                        files = [info2]
                try:
                    with zipfile.ZipFile(name, 'w') as fzip:
                        for i, x in zip(
                            files, zip_data
                        ):
                            if not i:
                                continue
                            if len(x) == 0:
                                continue
                            fzip.writestr(i, x, zipfile.ZIP_DEFLATED)

                except Exception as e:
                    logger.debug(f" Export ZIP error: {e}")
                
                shutil.move(name, os.path.join(dirname, name))

                if os.path.isfile(tpath):
                    os.remove(tpath)
                if os.path.isfile(path):
                    logger.debug(
                        f"ZIP file saved sucessfully: {path}")
                    sDlg = wx.MessageDialog(
                        self,
                        f'Fajl je uspešno sačuvan\n{os.path.basename(path)}', 
                        'SubtitleConverter',
                        wx.OK | wx.ICON_INFORMATION,
                    )
                    sDlg.ShowModal()
                    # Dodaje putanju i enkoding u recnik
                    self.saved_file[path] = self.newEnc
                    # self.saved += 1
                    # self.resetTool()
            else:
                logger.debug(f"Export ZIP: None selected")
                return
        event.Skip()
        
    def exportZIPmultiple(self):

        self.PathEnc()

        tpath = os.path.basename(list(self.multiFile)[0][:-4])
        epattern = re.compile(r"episode\s*-*\d*", re.I)
        tpath = epattern.sub("", tpath)
        tpath = re.sub(r"e01", "", tpath, count=1, flags=re.I)
        tpath = (
            tpath.replace(" 1 ", "").replace("x01", "").replace("  ", " ")
        )

        sas_wildcard = "ZipArchive (*.zip)|*.zip|All Files (*.*)|*.*"

        dlg = wx.FileDialog(
            self,
            message="Export file as ZIP",
            defaultDir=self.real_dir,
            defaultFile="",
            wildcard=sas_wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )

        dlg.SetFilename(tpath)

        def t_out(textin):
            tout = ""
            for i in textin:
                tout += i + "\n"
            return tout

        def data_out(filein):
            f = open(filein, 'rb')
            _data = f.read()
            f.close()
            return _data

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            # dirname = os.path.dirname(path)
            name = path

            if PREVIOUS[-1].action == 'toCYR_multiple':

                izbor_ansi = []
                izbor_txt = []
                _txt_list = []

                for i, x in zip(self.tmpPath, self.cyrUTFmulti):

                    tANSI = os.path.join(
                        "tmp", os.path.basename(i)
                    )  # ansi cirilica
                    tUTF = os.path.join(
                        "tmp", os.path.basename(x)
                    )  # utf_txt fajlovi
                    if not os.path.exists(tANSI):
                        shutil.copy(i, tANSI)
                    if not os.path.exists(tUTF):
                        shutil.copy(x, tUTF)

                    info2 = os.path.basename(tUTF)
                    izbor_ansi.append(tANSI)
                    izbor_txt.append(x)
                    _txt_list.append(info2)
                izbor = izbor_ansi + izbor_txt

                l_txt = len(_txt_list)
                if l_txt > 16:
                    p_txt_list = [x for x in _txt_list[:12]]
                    p_txt_list.append("...\n...\nUkupno [{}]".format(l_txt))
                elif l_txt < 16:
                    p_txt_list = [x for x in _txt_list]

                lat_files = [x for x in self.multiFile.keys()]
                lat_srt = [os.path.basename(x) for x in lat_files]
                if len(lat_srt) > 16:
                    l_srt_list = [x for x in lat_srt[:12]]
                    l_srt_list.append(
                        "...\n...\nUkupno [{}]".format(len(lat_srt))
                    )
                elif len(lat_srt) < 16:
                    l_srt_list = [x for x in lat_srt]

                text1 =\
                f"Include original latin?\n\nPostojeći *latin fajlovi:\n\n{t_out(l_srt_list)}"
                
                text = f"Include utf-8?\n\nPostojeći *utf-8* fajlovi:\n\n{t_out(p_txt_list)}"
                
                dlg = wx.RichMessageDialog(
                    self,
                    text,
                    "{}".format(os.path.basename(name)),
                    wx.YES_NO | wx.ICON_QUESTION,
                )
                dlg1 = wx.RichMessageDialog(
                    self,
                    text1,
                    "{}".format(os.path.basename(name)),
                    wx.YES_NO | wx.ICON_QUESTION,
                )

                if dlg.ShowModal() == wx.ID_YES:

                    files = izbor
                    zlist_a = [
                        data_out(x) for x in files if x.endswith('.txt')
                    ]
                    zlist_b = [
                        data_out(x) for x in files if x.endswith('.srt')
                    ]
                    info = [os.path.basename(x) for x in izbor]
                    zlist = zlist_b + zlist_a

                if dlg1.ShowModal() == wx.ID_YES:

                    files = lat_files
                    zlist_c = [
                        data_out(x) for x in files if i.endswith('.srt')
                    ]
                    info = info + lat_srt
                    zlist = zlist + zlist_c
            else:
                zlist = []
                try:
                    izbor = [
                        os.path.join("tmp", x)
                        if not x.startswith("tmp")
                        else x
                        for x in self.tmpPath
                        if not x.endswith(".zip")
                    ]
                    info = [
                        os.path.basename(x)
                        for x in self.tmpPath
                        if not x.endswith(".zip")
                    ]
                    for i, x in zip(self.tmpPath, izbor):
                        if not os.path.exists(x) and not i.endswith(".zip"):
                            shutil.copy(i, x)
                    zlist = [data_out(x) for x in izbor]
                except IOError as e:
                    logger.debug(f"ExportZIP IOError: {e}")
                    logger.debug(
                        "exportZIP IOError {}: ".format(sys.exc_info()[1:])
                    )
                except Exception:
                    logger.debug(
                        "ExportZIP_A error, {}".format(sys.exc_info())
                    )
            if PREVIOUS[-1].action == 'toCyrUTF8_multiple':
                files = izbor
                zlist = [data_out(x) for x in files]
                info = [os.path.basename(x) for x in files]            
            try:
                with zipfile.ZipFile(name, 'w') as fzip:
                    for i, x in zip(info, zlist):
                        if i == None:
                            continue
                        fzip.writestr(i, x, zipfile.ZIP_DEFLATED)
                for i in self.tmpPath:
                    if os.path.exists(i):
                        os.remove(i)
                    logger.debug("Removed {}".format(i))
                for i in self.cyrUTFmulti:
                    os.remove(i)
                    logger.debug("Removed {}".format(i))
            except IOError as e:
                logger.debug(
                    "Export ZIP_final, IOError({0}{1}):".format(tpath, e)
                )
            except Exception as e:
                logger.debug(f"Export ZIP_final error: {e}")

            if os.path.isfile(path):
                logger.debug("ZIP file saved sucessfully: {}".format(path))
                sDlg = wx.MessageDialog(
                    self,
                    'Fajl je uspešno sačuvan\n{}'.format(
                        os.path.basename(path)
                    ),
                    'SubtitleConverter',
                    wx.OK | wx.ICON_INFORMATION,
                )
                sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[path] = self.newEnc
        else:
            dlg.Destroy()
    
    def onCloseFile(self, event):
        self.text_1.SetValue('')
        self.disableTool()
        self.UNDO.clear()
        self.REDO.clear()
        PREVIOUS.clear()
        self.tmpPath.clear()
        self.enchistory.clear()        
        self.SetStatusText('Subtitle Converter is ready')
        self.SetStatusText("", 1)
        event.Skip()

    def removeFiles(self, event):
        if os.listdir('tmp'):
            file_paths = glob.glob('tmp\*.*')
            fileData = {}
            for fname in file_paths:
                fileData[fname] = os.stat(fname).st_mtime

            sortedFiles = sorted(fileData.items(), key=itemgetter(1))

            delete = len(sortedFiles) - 34
            if not len(self.multiFile) > 10:
                for x in range(0, delete):
                    os.remove(sortedFiles[x][0])
        event.Skip()
        
    def onFileHistory(self, event):
        ''''''
        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
        ):
            if self.ShowDialog() == False:
                return
        # get the file based on the menu ID
        fileNum = event.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(fileNum)
        # add it back to the history so it will be moved up the list
        self.filehistory.AddFileToHistory(path)
        self.real_path.append(path)
        self.real_dir = os.path.dirname(path)
        
        if self.multiFile:
            self.multiFile.clear()
        self.tmpPath.clear()
        self.handleFile([path])

        if PREVIOUS:
            self.pre_suffix = PREVIOUS[0].psuffix
            enc = PREVIOUS[0].enc
            self.enableTool()
            self.clearUndoRedo()
            logger.debug(f"From FileHistory: {os.path.basename(path)}; {enc}")
            if zipfile.is_zipfile(self.tmpPath[0]):
                self.SetStatusText(os.path.basename(self.tmpPath[0]))
            else:
                self.SetStatusText(os.path.splitext(os.path.basename(self.tmpPath[0]))[0])
            self.SetStatusText(printEncoding(enc), 1)
        event.Skip()

    def rwFileHistory(self, hfile):
        """"""
        logfile = open(log_file_history, "w", encoding="utf-8", newline="\r\n")
        if len(hfile) > 9:
            hfile = hfile[-9:]
        file_set = list(unique_everseen(hfile))
        for paths in file_set:
            if os.path.exists(paths):
                logfile.write(paths + "\n")
        logfile.close()
        
    def onCyrToANSI(self, event):
        
        with shelve.open(
            filePath("resources", "var", "dialog_settings.db"),
            flag='writeback',
        ) as sp:
            ex = sp['key5']
            value1_s = ex['lat_ansi_srt']

        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.cyrToANSI_multiple()
        else:
            self.pre_suffix = value1_s

            self.newEnc = 'windows-1250'
            t_enc = 'utf-8'

            text = WORK_TEXT.getvalue()
            # text = self.text_1.GetValue()

            if text:
                text = text.replace('?', '¬')

            text, msg = changeLetters(text, t_enc, reversed_action=True)
            cyr_path = path
            
            text = bufferCode(text, self.newEnc)
            
            error_text = checkFile(path, cyr_path, text, multi=False)
            text = displayError(
                text,
                self.text_1,
                self.real_dir,
                cyr_path,
                self.newEnc,
                multi=False,
            )

            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
                self.Error_Text = error_text

            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)
            self.bytesToBuffer(text, self.newEnc)
            
            if os.path.exists(self.cyrUTF):
                os.remove(self.cyrUTF)
            
            self.SetStatusText(self.newEnc, 1)

            self.postAction(path)
            self.addPrevious("cyrToANSI", self.newEnc, text, self.pre_suffix)
            self.addHistory(self.enchistory, path, self.newEnc)
            
        event.Skip()
    
    def cyrToANSI_multiple(self):
        
        with open(
            filePath("resources", "var", "file_ext.pkl"), "rb"
        ) as f:
            ex = pickle.load(f)  # ["key5"]
            value1_s = ex["lat_ansi_srt"]
        self.text_1.SetValue("")
        
        self.PathEnc()

        self.tmpPath.clear()
        self.pre_suffix = value1_s
        self.newEnc = 'windows-1250'
        t_enc = 'utf-8'
        f_text = ["Files Processed:\n"]

        for key, value in self.multiFile.items():
            path = key
            entered_enc = value

            try:
                text = normalizeText(entered_enc, path)
                if text:
                    text = text.replace('?', '¬')

                text, msg = changeLetters(text, t_enc, reversed_action=True)

                nam, b = newName(path, self.pre_suffix, True)
                newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)

                f_text.append('\n')
                f_text.append(os.path.basename(newF))
                self.tmpPath.append(newF)

                text = bufferCode(text, self.newEnc)
                
                error_text = checkFile(path, newF, text, multi=True)
                text = displayError(
                    text,
                    self.text_1,
                    self.real_dir,
                    newF,
                    self.newEnc,
                    multi=True,
                )

                writeToFile(text, newF, self.newEnc, multi=True)

                if error_text:
                    ErrorDlg = wx.MessageDialog(
                        self,
                        error_text,
                        "SubtitleConverter",
                        wx.OK | wx.ICON_ERROR,
                    )
                    ErrorDlg.ShowModal()
                    self.Error_Text = error_text
                self.SetStatusText(f"Processing {os.path.basename(newF)}")
            except Exception as e:
                logger.debug(f"cyrToANSI error: {e}")
        
        for item in f_text:
            self.text_1.WriteText(item)
        self.multipleTools()
        self.reloaded = 0
        self.addPrevious("cyrToANSI_multiple", self.newEnc, "", self.pre_suffix)
        self.SetStatusText('Multiple files done.')
        
    def onCyrToUTF(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            value1_s = ex['lat_utf8_srt']        
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.cyrToUTF_multiple()
        else:        
                
            self.pre_suffix = value1_s
            
            if self.preferences.IsChecked(1011):
                self.newEnc = 'utf-8-sig'
            else:
                self.newEnc = 'utf-8'
            
            # text = WORK_TEXT.getvalue()
            text = self.text_1.GetValue()
            
            if text: text = text.replace('?', '¬')
                    
            text, msg = changeLetters(text, self.newEnc, reversed_action=True)
            cyr_path = path
            
            text = bufferCode(text, self.newEnc)
            
            error_text = checkFile(path, cyr_path, text, multi=False)
            text = displayError(
                text,
                self.text_1,
                self.real_dir,
                cyr_path,
                self.newEnc,
                multi=False,
            )

            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
                self.Error_Text = error_text

            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)
            self.bytesToBuffer(text, self.newEnc)
            
            if os.path.exists(self.cyrUTF):
                os.remove(self.cyrUTF)
            
            self.SetStatusText(printEncoding(self.newEnc), 1)

            self.postAction(path)            
            self.addPrevious("cyrToUTF", self.newEnc, text, self.pre_suffix)
            self.addHistory(self.enchistory, path, self.newEnc)
            
        event.Skip()
        
    def cyrToUTF_multiple(self):
        
        with open(
            os.path.join("resources", "var", "file_ext.pkl"), "rb"
        ) as f:
            ex = pickle.load(f)  # ["key5"]
            value1_s = ex["lat_utf8_srt"]

        self.text_1.SetValue("")
        f_text = ["Files Processed:\n"]
        self.PathEnc()

        self.pre_suffix = value1_s
        self.tmpPath.clear()

        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'

        for key, value in self.multiFile.items():
            path = key
            entered_enc = value

            text = normalizeText(entered_enc, path)
            if text:
                text = text.replace('?', '¬')

            nam, b = newName(path, self.pre_suffix, True)
            newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)

            text, msg = changeLetters(
                text, self.newEnc, reversed_action=True
            )
            
            text = bufferCode(text, self.newEnc)

            error_text = checkFile(path, newF, text, multi=True)
            text = displayError(
                text,
                self.text_1,
                self.real_dir,
                newF,
                self.newEnc,
                multi=True,
            )

            f_text.append('\n')
            f_text.append(os.path.basename(newF))
            self.tmpPath.append(newF)

            writeToFile(text, newF, self.newEnc, multi=True)

            if error_text:
                ErrorDlg = wx.MessageDialog(
                    self,
                    error_text,
                    "SubtitleConverter",
                    wx.OK | wx.ICON_ERROR,
                )
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            self.SetStatusText(os.path.basename(path))
            
        for item in f_text:
            self.text_1.WriteText(item)
        self.multipleTools()
        self.reloaded = 0
        self.SetStatusText(printEncoding(self.newEnc), 1)
        self.addPrevious("cyrToUTF_multiple", self.newEnc, "", self.pre_suffix)
        self.SetStatusText('Multiple files done.')
        
    def onFixSubs(self):

        tval = self.text_1.GetValue()
        if (
            not tval.startswith('Files ')
            and len(tval) > 0
            and self.save.IsEnabled()
            and self.reloaded == 0
        ):
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1:
            return

        try:
            with shelve.open(
                os.path.join('resources', 'var', 'dialog_settings.db'),
                flag='writeback',
            ) as sp:
                ex = sp['key1']
                cb1_s = ex['state1']
                cb8_s = ex['state8']
                fx = sp['key5']
                value1_s = fx['fixed_subs']
        except Exception as e:
            logger.debug(f"FixSubtitle error: {e}")

        self.pre_suffix = value1_s
        self.newEnc = entered_enc  # VAZNO za Save funkciju
        
        text = WORK_TEXT.getvalue()
        subs = pysrt.from_string(text)

        if len(subs) == 0:
            logger.debug("Fixer: No subtitles found.")
        else:
            text = ""

            def chg(subs_in):
                N = 0
                for first, second in zip(subs_in, subs_in[1:]):
                    t1 = first.end.ordinal
                    t2 = second.start.ordinal
                    if t1 > t2 or t2 - t1 < 85:
                        N += 1
                return N

            def rpt(path, enc):
                m = 0
                s1 = 0
                while True:
                    subs = pysrt.from_string(WORK_TEXT.getvalue())
                    x, y = fixGaps(subs)
                    m += x
                    s1 += y
                    if x == 0:
                        break
                return m, s1

            if cb1_s == True:
                if not cb8_s == True:

                    pn = chg(subs)
                    if pn > 0:
                        m, s1 = rpt(path, entered_enc)
                    else:
                        m = 0
                        s1 = 0
                else:
                    logger.debug("Fixer: Remove gaps not enabled.")
            try:
                if not cb8_s:
                    text = WORK_TEXT.getvalue()
                    textis = srt.parse(text)
                    text = srt.compose(textis)
                else:
                    text = WORK_TEXT.getvalue()
            except IOError as e:
                logger.debug(f"FixSubtitle, I/O error({e.errno}): {e.strerror}")
            except Exception as e:
                logger.debug(f"FixSubtitle, unexpected error: {e}")

            text = rm_dash(text)

            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)
            self.text_1.SetValue(text)

            self.bytesToBuffer(text, entered_enc)
            
            if cb1_s == True:
                if not cb8_s == True:
                    if s1 > 1:
                        s1 = s1 - 1
                        m1 = f'\nPreklopljenih linija ukupno: {s1}'
                        logger.debug(m1)
                    else:
                        m1 = ''
                    logger.debug(f'Fixer: Popravljenih gapova ukupno: {m}')
                    if m >= 0:
                        sDlg = wx.MessageDialog(
                            self,
                            f'Subtitle fix\n\nPopravljenih gapova ukupno: {m}\n{m1}',
                            'SubtitleConverter',
                            wx.OK | wx.ICON_INFORMATION,
                        )
                        sDlg.ShowModal()

        self.addPrevious("FixSubtitle", self.newEnc, text, self.pre_suffix)
        self.addHistory(self.enchistory, path, self.newEnc)
        self.SetStatusText(printEncoding(self.newEnc), 1)

        self.postAction(path)
        
    def ShowDialog(self):

        if self.dont_show:
            return
    
        dlg = wx.RichMessageDialog(
            self,
            "Current conten has not been saved! Proceed?",
            "Please confirm!",
            style=wx.OK | wx.CANCEL,
        )
        dlg.ShowCheckBox("Don't show this message again")
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.IsCheckBoxChecked():
                self.dont_show = True
            return True
        else:
            if dlg.IsCheckBoxChecked():
                self.dont_show = True
            return False
        
    def utfSetting(self, event):

        if self.preferences.IsChecked(1012):
            item_txt = 'txt'
        else:
            item_txt = 'srt'
        with open(filePath('resources', 'var', 'tcf.pkl'), 'wb') as tf:
            pickle.dump(item_txt, tf)

        if self.preferences.IsChecked(1011):
            item = 'Checked'
        else:
            item = 'NotChecked'
        with open(filePath('resources', 'var', 'bcf.pkl'), 'wb') as fb:
            pickle.dump(item, fb)
            
        if self.preferences.IsChecked(1014):
            val = True
        else:
            val = False
        with open(filePath("resources", "var", "obs1.pkl"), "wb") as f:
            pickle.dump(val, f)

        event.Skip()
        
    def showLog(self, event):
        
        if self.preferences.IsChecked(1013):
            ch = True
        else:
            ch = False
        cb3s = os.path.join('resources', 'var', 'fixer_cb3.data')
        with open(cb3s, 'wb') as p:
            pickle.dump(ch, p)            
        
        event.Skip()

    def onFileSettings(self, event):
        settings_dlg = FileSettings(None)
        settings_dlg.ShowModal()
        event.Skip()
        
    def onAbout(self, event):
        text = '''SubtitleConverter\n\n\
        Jednostavna wxPython aplikacija \n\
        za konvertovanje srt i txt fajlova\n\
        i transkripciju engleskih imena i pojmova.\n\n\
        Program ima ove opcije:\n\
        -Preslovljavanje latinice u ćirilicu i promena kodnog rasporeda. \n\
        -Konvertovanje unikode u ANSI format.\n\
        -Konvertovanje ANSI u unikode.\n\
        -Default izlazni kodeci su cp1250, 1251 i utf-8.\n\
        -Zamena engleskih imena u titlu odgovarajućim iz rečnika.\n\
         Default izlazni kodek je UTF-8.\n\
        -Mogućnost dodavanja novih definicija za transkripciju u rečnicima. \n\
        -Program konvertuje titlove sa ćiriličnim pismom u latinicu.\n\n\
        Autor: padovaSR\n\
        https://github.com/padovaSR\n\
        License: GNU GPL v2'''
        AboutDlg = wx.MessageDialog(self, text, "SubtitleConverter {}".format(VERSION), wx.OK | wx.ICON_INFORMATION)
        AboutDlg.ShowModal()
        event.Skip()
        
    def onManual(self, event):
        dlg = MyManual(None)
        dlg.Show()
        event.Skip()        
    
    def onFixerSettings(self, event):
        fixer_dlg = FixerSettings(None)
        ret_code = fixer_dlg.ShowModal()
        fixer_dlg.Destroy()
        if ret_code == True:
            self.onFixSubs()
        event.Skip()

    def onMergerSettings(self, event):
        settings_dialog = Settings(None, -1, "")
        settings_dialog.ShowModal()        
        event.Skip()

    def onSelectFont(self, event):
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(self.curClr)         # set colour
        data.SetInitialFont(self.curFont)

        dlg = wx.FontDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            colour = data.GetColour()
            bld = font.GetWeight()
            logger.debug('Selected font: "%s", %d points, color %s' % (font.GetFaceName(), font.GetPointSize(), colour.Get()))
            with shelve.open(os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback') as s:
                s['key4'] = {'new_font': font.GetFaceName(), 'fontSize': font.GetPointSize(), 'fontColour': colour.Get(), 'weight': bld}
            self.curFont = font
            self.curClr = colour
            self.updateUI()
            # Don't destroy the dialog until you get everything you need from the dialog
        dlg.Destroy()        
        event.Skip()
        
    def onShortcutChanged(self, event):
        
        shortcut = event.GetShortcut()
        newAccel = event.GetAccelerator()
        if newAccel == "Disabled":
            newAccel = ""
        self.sc[shortcut.label] = newAccel
        
        event.Skip()
        
    def editShortcuts(self, event):
        
        dlg = SE.ShortcutEditor(self)
        dlg.FromMenuBar(self)
        dlg.Bind(SE.EVT_SHORTCUT_CHANGED, self.onShortcutChanged)
        
        if dlg.ShowModal() == wx.ID_OK:
            dlg.ToMenuBar(self)
            
            shortcutsKey.update([(key, self.sc[key]) for key in self.sc.keys()])
            
            i_list = list(shortcutsKey.keys())
            
            with open(filePath("resources","shortcut_keys.cfg"), "r",
                      encoding="utf-8") as cf:
                new_f = ""
                for line in cf:
                    if any(line.startswith(n) for n in i_list):
                        x = line.split("=")
                        s = f"{x[0].strip()}={shortcutsKey[x[0].strip()]}\n"
                        new_f += s
                    else: new_f += line
            
            with  open(filePath("resources","shortcut_keys.cfg"), "w",
                       encoding="utf-8", newline="\r\n") as cf:
                cf.write(new_f)            
            
            dlg.Destroy()
        
        event.Skip()
        
    def size_frame(self, event):
        
        width, height = event.GetSize()
        
        self.fsize["W"] = width
        self.fsize["H"] = height
        
        event.Skip()
        
    def addPrevious(self, action, enc, content, psuffix):
        '''This function creates namedtuple'''
        if PREVIOUS:
            if PREVIOUS[-1].enc == enc and PREVIOUS[-1].content == content:
                return
        prev = namedtuple("prev", ["action", "enc", "content", "psuffix"])
        PREVIOUS.append(prev(action, enc, content, psuffix))
        
    def undoAction(self, event):
        '''Undo text'''
        
        path = self.tmpPath[0]
        actions = [x.action for x in PREVIOUS]
        if PREVIOUS:
            self.REDO.append(PREVIOUS[-1])
        else:
            return
        if not "Open" in actions:
            prev_items = PREVIOUS.pop(len(PREVIOUS)-2)
        else:
            if PREVIOUS[-1].action == "Open" and len(PREVIOUS) == 2:
                PREVIOUS.reverse()
            prev_items = PREVIOUS[len(PREVIOUS)-2]
            if len(PREVIOUS) > 2:
                PREVIOUS.pop()
        
        entered_enc = prev_items.enc
        
        if prev_items:
            text = prev_items.content
            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)
            self.text_1.SetValue(text)
                
        if self.cyrUTF:
            if os.path.exists(self.cyrUTF):
                os.remove(self.cyrUTF)
    
        if len(self.REDO) >= 6:
            self.REDO = self.REDO[1:]
        
        enc = printEncoding(entered_enc)
            
        self.postAction(path)
        self.SetStatusText(enc, 1)
        self.pre_suffix = prev_items.psuffix
        self.addHistory(self.enchistory, path, entered_enc)
        self.addPrevious(prev_items.action, entered_enc, text, self.pre_suffix)
        self.reloaded = 0
        
        if not prev_items.action == "toCYR":
            self.frame_toolbar.EnableTool(1003, True)   # toANSI
            self.to_ansi.Enable(True)
        if prev_items.action == "Open":
            self.undo.Enable(False)
        
        event.Skip()
    
    def redoAction(self, event):
        '''Redo text'''
        
        path = self.tmpPath[0]
        prev = self.REDO.pop()
        
        # actions = [x.action for x in self.REDO]
        
        if prev:
            text = prev.content
            bufferText(text, WORK_TEXT)
            bufferText(text, self.workText)
            self.text_1.SetValue(text)
            
        if not prev.action == "toCYR":
            self.frame_toolbar.EnableTool(1003, True)   # toANSI
            self.to_ansi.Enable(True)

        self.postAction(path)
        self.SetStatusText(printEncoding(prev.enc), 1)
        self.pre_suffix = prev.psuffix
        self.addHistory(self.enchistory, path, prev.enc)
        self.addPrevious(prev.action, prev.enc, text, self.pre_suffix)
        
        event.Skip()
        
    def onChoice(self, event):
        
        ctrl = event.GetEventObject()
        value = ctrl.GetValue()
        
        with open(filePath('resources', 'var', 'obsE.pkl'), 'wb') as f:
            pickle.dump(value, f)
            
        event.Skip()
        
class MyApp(wx.App):
    
    def remOnstart(self):
        
        for i in os.listdir(filePath("resources","var","log")):
            fsize = os.path.getsize(filePath("resources","var","log",i))
            if fsize >= 1048576:
                os.remove(i)
        
        f_list = [
            "r_text0.pkl",
            "droped0.pkl",
            "'LatCyr.map.cfg",
            "path0.pkl",
            "rpath0.pkl",
        ]
        for x in f_list:
            file_path = filePath("resources","var",x)
            if os.path.isfile(file_path):
                os.remove(file_path)

        if not os.path.isdir('tmp'):
            os.mkdir('tmp')

        b_file = filePath("resources","var","presuffix_list.bak")
        if os.path.exists(b_file):
            with open(b_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            line_set = set(lines)
            out = open(b_file, "w", encoding="utf-8")
            for line in line_set:
                out.write(line)
            out.close()

    def m_files(self):

        v_list = [
            "m_extensions.pkl",
            "file_ext.pkl",
            "bcf.pkl",
            "bcp.pkl",
            "obsE.pkl",
            "set_size.pkl",
            "tcf.pkl",
            "txt0.pkl",
            "fixer_cb3.data",
            "obs1.pkl",
            "presuffix_list.bak", 
        ]
        r_list = ["shortcut_keys.cfg", "Regex_def.config"]

        v_paths = [os.path.join("resources", "var", x) for x in v_list]
        r_paths = [os.path.join("resources", x) for x in r_list]
        logs = os.path.join("resources","var","log","file.history.log")
        v_list.append(logs)
        m_list = [x for x in (v_paths + r_paths) if not os.path.isfile(x)]

        if m_list:
            error_text = "File Not Found\n\n{}\nPlease check files!".format(
                "".join([x + '\n' for x in m_list])
            )
            ErrorDlg = wx.MessageDialog(
                None, error_text, "SubConverter", wx.OK | wx.ICON_ERROR
            )
            ErrorDlg.ShowModal()
    
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.remOnstart()
        self.m_files()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()