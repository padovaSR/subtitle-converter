#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import re
import shutil
import zipfile
import pickle
import shelve
import pysrt
import srt
from io import StringIO, BytesIO
from operator import itemgetter
import glob
import logging
import traceback
from pydispatch import dispatcher 

from FileProcessing import FileProcessed, FileOpened, Preslovljavanje, writeTempStr, TextProcessing, bufferCode
from showError import w_position, showMeError
from merger_settings import Settings
from fixer_settings import FixerSettings
from file_settings import FileSettings
from merge import myMerger, fixGaps
from zamenaImena import shortcutsKey 

from Manual import MyManual

from settings import filePath, WORK_SUBS, WORK_TEXT
from file_dnd import FileDrop


import wx
import wx.lib.agw.shortcuteditor as SE

from subtitle_converter_gui import ConverterFrame 


VERSION = "v0.5.8"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(filename=filePath("resources", "var", "subtitle_converter.log"), mode="w", encoding="utf-8")
handler.setFormatter(formatter)
logger.addHandler(handler)


      
class MyFrame(ConverterFrame):
    def __init__(self, *args, **kwds):
        ConverterFrame.__init__(self, *args, **kwds)
        
        self.wildcard = "SubRip (*.zip; *.srt;\
        *.txt)|*.zip;*.srt;*.txt|MicroDVD (*.sub)|*.sub|Text File\
        (*.txt)|*.txt|All Files (*.*)|*.*"        
        
        with shelve.open(filePath('resources', 'var', 'dialog_settings.db'), flag='writeback') as s:
            ex = s['key4']
            new_font = ex['new_font']; fontSize = int(ex['fontSize']); fC = ex['fontColour']; bl = ex['weight']
        
        if bl == 92:
            weight = wx.FONTWEIGHT_BOLD
        else:
            weight = wx.FONTWEIGHT_NORMAL
            
        self.text_1.SetFont(wx.Font(fontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight, 0, new_font))    
        self.curFont = self.text_1.GetFont()
        self.curClr = wx.Colour((fC[0], fC[1], fC[2], fC[3]))
        self.text_1.SetForegroundColour(self.curClr)
        self.text_1.SetFont(self.curFont)
        # self.curClr = self.text_1.GetForegroundColour()
        self.updateUI()        
        
        # drop target
        dt = FileDrop(self.text_1)
        self.text_1.SetDropTarget(dt)        
        
        self.dont_show = False
        
        self.sc = {}
        self.fsize = {}
        
        self.workText = StringIO()
        self.bytesText = BytesIO()        
        
        self.undo_text = []
        self.redo_text = []
        
        self.previous_action= {}
        self.multiFile = {}
        self.enchistory = {}
        self.droped = {}
        self.saved_file = {}
        self.newEnc = ""
        self.real_dir = ""
        self.location = "tmp"
        self.tmpPath = []
        self.real_path = []
        self.cyrUTFmulti = []
        
        self.filehistory = wx.FileHistory()
        self.filehistory.UseMenu(self.file_sub)
        self.filehistory.AddFilesToMenu()        
        
        self.menu_items = [self.merger,
                           self.fixer, self.to_cyrillic, self.to_ansi, self.to_utf8,
                           self.cleaner, self.specials, self.transcrib, self.cyr_to_ansi,
                           self.cyr_to_utf, self.export_zip, self._regex]
        
        #  MenuBar events --------------------------------------------------------------------------#
        self.Bind(wx.EVT_MENU, self.onOpen, id=self.fopen.GetId())
        self.Bind(wx.EVT_MENU, self.onOpenNext, id=self.open_next.GetId())
        self.Bind(wx.EVT_MENU, self.onReload, id=self.reload.GetId())
        self.Bind(wx.EVT_MENU, self.onSave, id=self.save.GetId())
        self.Bind(wx.EVT_MENU, self.onSaveAs, id=self.save_as.GetId())
        self.Bind(wx.EVT_MENU, self.exportZIP, id=self.export_zip.GetId())
        self.Bind(wx.EVT_MENU, self.onCloseFile, id=self.close.GetId())
        self.Bind(wx.EVT_MENU, self.onQuit, id=self.quit_program.GetId())
        ############################################################################
        self.Bind(wx.EVT_MENU, self.onUndo, id=self.undo.GetId())
        self.Bind(wx.EVT_MENU, self.onRedo, id=self.redo.GetId())
        self.Bind(wx.EVT_MENU, self.onCut, id=self.cut.GetId())
        self.Bind(wx.EVT_MENU, self.onCopy, id=self.copy.GetId())
        self.Bind(wx.EVT_MENU, self.onPaste, id=self.paste.GetId())
        self.Bind(wx.EVT_MENU, self.onFind, id=self.find.GetId())
        ############################################################################
        self.Bind(wx.EVT_MENU, self.toCyrillic, id=self.to_cyrillic.GetId())
        self.Bind(wx.EVT_MENU, self.toANSI, id=self.to_ansi.GetId())
        self.Bind(wx.EVT_MENU, self.toUTF, id=self.to_utf8.GetId())
        self.Bind(wx.EVT_MENU, self.onTranscribe, id=self.transcrib.GetId())
        self.Bind(wx.EVT_MENU, self.onRepSpecial, id=self.specials.GetId())
        self.Bind(wx.EVT_MENU, self.onCleanup, id=self.cleaner.GetId())
        self.Bind(wx.EVT_MENU, self.applyRegex, id=self._regex.GetId())
        self.Bind(wx.EVT_MENU, self.onCyrToANSI, id=self.cyr_to_ansi.GetId())
        self.Bind(wx.EVT_MENU, self.onCyrToUTF, id=self.cyr_to_utf.GetId())
        self.Bind(wx.EVT_MENU, self.onFixSubs, id=self.fixer.GetId())
        self.Bind(wx.EVT_MENU, self.onMergeLines, id=self.merger.GetId())
        ############################################################################
        self.Bind(wx.EVT_MENU, self.onSelectFont, id=self.fonts.GetId())
        self.Bind(wx.EVT_MENU, self.onFixerSettings, id=self.fixer_settings.GetId())
        self.Bind(wx.EVT_MENU, self.editShortcuts, id=self.shortcuts.GetId())
        self.Bind(wx.EVT_MENU, self.onMergerSettings, id=self.merger_pref.GetId())
        self.Bind(wx.EVT_MENU, self.onAbout, id = self.about.GetId())
        self.Bind(wx.EVT_MENU, self.onManual, id=self.manual.GetId())        
        
        # Toolbar events ---------------------------------------------------------------------------#
        self.Bind(wx.EVT_TOOL, self.onOpen, id = 1001)
        self.Bind(wx.EVT_TOOL, self.onSave, id = 1010)
        self.Bind(wx.EVT_TOOL, self.toCyrillic, id = 1002)
        self.Bind(wx.EVT_TOOL, self.toANSI, id = 1003)
        self.Bind(wx.EVT_TOOL, self.toUTF, id = 1004)
        self.Bind(wx.EVT_TOOL, self.onTranscribe, id = 1005)
        self.Bind(wx.EVT_TOOL, self.onRepSpecial, id = 1006)
        self.Bind(wx.EVT_TOOL, self.onCleanup, id = 1007)
        self.Bind(wx.EVT_TOOL, self.onQuit, id = 1008)
        self.Bind(wx.EVT_TOOL, self.undoAction, id = 101)
        self.Bind(wx.EVT_TOOL, self.redoAction, id = 102)
        
        # Events other -----------------------------------------------------------------------------#
        self.text_1.Bind(wx.EVT_KEY_UP, self.onChanged, id=wx.ID_ANY)
        self.text_1.Bind(wx.EVT_TEXT, self.removeFiles, id=-1, id2=wx.ID_ANY)
        self.Bind(wx.EVT_MENU_RANGE, self.onFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
        self.comboBox1.Bind(wx.EVT_COMBOBOX, self.onChoice, id=-1, id2=wx.ID_ANY)
        self.Bind(wx.EVT_MENU, self.toCyrSRT_utf8, id=82)
        self.Bind(wx.EVT_MENU, self.onFileSettings, id=83)
        self.Bind(wx.EVT_MENU, self.ShowDialog, id=84)
        self.Bind(wx.EVT_SIZE, self.size_frame, id=-1)
        self.Bind(wx.EVT_CLOSE, self.onClose, id=wx.ID_ANY)
        #-------------------------------------------------------------------------------------------#
        entries = [wx.AcceleratorEntry() for i in range(2)]
        entries[0].Set(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('Y'), 82)
        entries[1].Set(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('F'), 83)
        
        accel_tbl = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel_tbl)
        #-------------------------------------------------------------------------------------------#
    
        dispatcher.connect(self.updateStatus, "TMP_PATH", sender=dispatcher.Any)
        dispatcher.connect(self.enKode, "TMP_PATH", sender=dispatcher.Any)
        dispatcher.connect(self.dropedFiles, "droped", sender=dispatcher.Any)
    
    def updateStatus(self, message, msg):
        
        if msg[2] == True:
            self.SetStatusText('Multiple files ready for processing')
        else:
            path = message
            if type(path) == list:
                path = path[-1]
            self.SetStatusText(os.path.basename(path))
            self.tmpPath = [path]            
        
    def enKode(self, message, msg):
            
        self.enableTool()
        
        rlPath = msg[0]
        tpath = message
        if type(tpath) == list: tpath = tpath[-1]
        enc = msg[1]
            
        self.real_dir = os.path.dirname(rlPath[-1])
        self.enchistory[tpath] = enc
        self.real_path = [rlPath]
        
    def dropedFiles(self, msg):
        self.droped = msg
        
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
       
    def enableTool(self):
        
        self.frame_toolbar.EnableTool(wx.ID_CLOSE, True)
        self.frame_toolbar.EnableTool(1002, True)   # toCyrillic
        self.frame_toolbar.EnableTool(1003, True)   # toANSI
        self.frame_toolbar.EnableTool(1004, True)   # toUTF
        self.frame_toolbar.EnableTool(1005, True)   # Transcribe
        self.frame_toolbar.EnableTool(1006, True)   # Special
        self.frame_toolbar.EnableTool(1007, True)   # Cleanup
        
        new_items = [self.undo, self.redo, self.cut, self.copy, self.paste, self.find]
        
        for i in new_items: i.Enable(True)
        for i in self.menu_items: i.Enable(True)
        
    def disableTool(self):
        
        self.frame_toolbar.EnableTool(wx.ID_CLOSE, False)
        self.frame_toolbar.EnableTool(1010, False)
        self.frame_toolbar.EnableTool(1002, False)   # toCyrillic
        self.frame_toolbar.EnableTool(1003, False)   # toANSI
        self.frame_toolbar.EnableTool(1004, False)   # toUTF
        self.frame_toolbar.EnableTool(1005, False)   # Transcribe
        self.frame_toolbar.EnableTool(1006, False)   # Special
        self.frame_toolbar.EnableTool(1007, False)   # Cleanup
        
        new_items = [self.save, self.save_as, self.reload]
        
        for i in new_items: i.Enable(False)
        for i in self.menu_items: i.Enable(False)
    
    def postAction(self):
        
        self.MenuBar.Enable(wx.ID_SAVE, True)
        self.MenuBar.Enable(wx.ID_SAVEAS, True)
        self.MenuBar.Enable(wx.ID_CLOSE, True)
        self.reload.Enable(True)
        self.frame_toolbar.EnableTool(1010, True)  # Save
        self.reloaded = 0
        
    def handleFile(self, filepaths):
        
        def file_go(infile, realF):
            fop = FileOpened(infile)
            enc = fop.findCode()
            fproc = FileProcessed(enc, infile)
            text = fproc.normalizeText()
            fproc.bufferText(text, WORK_TEXT)
            nlist = fproc.checkErrors(text)
            self.text_1.SetValue(text)
            self.undo_text.append(text)
            for i in nlist:
                a = i[0]
                b = i[1]                        
                self.text_1.SetStyle(a, b, wx.TextAttr("YELLOW","BLUE"))
                self.text_1.SetInsertionPoint(b)            
            logger.debug(f'File opened: {os.path.basename(infile)}')
            self.filehistory.AddFileToHistory(infile)
            self.enchistory[infile] = enc
            self.reloadText = text
            fproc.bufferText(text, self.workText)
            
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
        tmp_path = [os.path.join(self.location, os.path.basename(item)) for item in inpaths]  # sef.locatin is tmp/
        
        if len(inpaths) == 1:  # Jedan ulazni fajl, ZIP ili TXT,SRT
            path = inpaths[0]
            tpath = tmp_path[0]
            if not zipfile.is_zipfile(path):
                shutil.copy(path, tpath)
                file_go(tpath, path)    # U tmp/ folderu
                self.tmpPath.append(tpath)
                self.SetStatusText(os.path.basename(path))
            elif zipfile.is_zipfile(path):
                
                fop = FileOpened(path)
                try:
                    outfile, rfile = fop.isCompressed()  # U tmp/ folderu
                except:
                    logger.debug(f'{path}: No files selected.')
                else:
                    if len(outfile) == 1:   # Jedan fajl u ZIP-u
                        file_go(outfile[0], rfile)
                        self.tmpPath.append(outfile[0])
                        self.SetStatusText(os.path.basename(outfile[0]))
                    elif len(outfile) > 1:  # Više fajlova u ZIP-u
                        self.text_1.SetValue('Files List:\n')
                        for i in range(len(outfile)):
                            name = os.path.basename(outfile[i])
                            fop = FileOpened(path=outfile[i])
                            enc = fop.findCode()
                            fproc = FileProcessed(enc, outfile[i])
                            fproc.normalizeText()
                            self.enchistory[outfile[i]] = enc
                            self.text_1.AppendText('\n')
                            self.text_1.AppendText(name)
                            self.multiFile[outfile[i]] = enc
                        logger.debug('FileHandler: Ready for multiple files.')
                        self.SetStatusText('Files ready for processing')
                        
        elif len(inpaths) > 1:      # Više selektovanih ulaznih fajlova
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
                    except Exception:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                        logger.error(''.join('!! ' + line for line in lines))
                    except:
                        logger.debug(f'{fpath}: No files selected.')                    
                    else:
                        if len(outfile) == 1:  # Jedan fajl
                            fop = FileOpened(path=outfile[0])
                            enc = fop.findCode()
                            fproc = FileProcessed(enc, outfile[0])
                            fproc.normalizeText()
                            self.enchistory[outfile[0]] = enc
                            self.text_1.AppendText('\n')
                            self.text_1.AppendText(os.path.basename(outfile[0]))
                            self.multiFile[outfile[0]] = enc
                        elif len(outfile) > 1:  # Više fajlova
                            for i in range(len(outfile)):
                                fpath = outfile[i]
                                fop = FileOpened(fpath)
                                enc = fop.findCode()
                                fproc = FileProcessed(enc, fpath)
                                fproc.normalizeText()
                                self.enchistory[fpath] = enc
                                self.text_1.AppendText('\n')
                                self.text_1.AppendText(os.path.basename(fpath))
                                self.multiFile[fpath] = enc
                else:   # Nije ZIP
                    name = os.path.basename(fpath)
                    fop = FileOpened(fpath)
                    enc = fop.findCode()
                    fproc = FileProcessed(enc, fpath)
                    fproc.normalizeText()
                    self.text_1.AppendText("\n")
                    self.text_1.AppendText(name)
                    self.enchistory[fpath] = enc
                    self.multiFile[fpath] = enc
                    self.reloadText = name
                    
            self.multipleTools()
            logger.debug('FileHandler: Ready for multiple files')
            self.SetStatusText('Files ready for processing')
    
    def onOpen(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and not self.previous_action:
            dl1 = wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                                wx.ICON_QUESTION | wx.YES_NO, self)
            if dl1 == wx.NO:
                return
        
        dlgOpen = wx.FileDialog(self, "Otvori novi fajl",
                                style=wx.FD_OPEN|wx.FD_MULTIPLE, wildcard=self.wildcard)
        if dlgOpen.ShowModal() == wx.ID_OK:
            self.tmpPath.clear()
            if len(self.multiFile) >= 1:
                self.multiFile.clear()
                self.previous_action.clear()
                self.enchistory.clear()
            self.filepath = dlgOpen.GetPaths() # Get the file location
            if len(self.filepath) == 1:
                real_path = self.filepath[-1]
                self.real_path = [real_path]
                self.real_dir = os.path.dirname(real_path)
            else:
                for fpath in self.filepath:
                    self.real_path.append(fpath)
                    
            self.handleFile(self.filepath)
            self.enableTool()
            self.open_next.Enable(False)
            dlgOpen.Destroy()            
            
        event.Skip()

    def onOpenNext(self, event):
        
        open_next, enc = self.saved_file.popitem()
        
        _path = os.path.join("tmp", os.path.basename(open_next))
        
        ask = 'Open this file:\n{}'.format(os.path.basename(open_next))
        askDlg = wx.MessageDialog(self, ask, caption="SubtitleConverter",
                                  style= wx.OK_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
        if askDlg.ShowModal() == wx.ID_OK:
            try:
                shutil.copy(open_next, _path)
                self.text_1.SetValue("")
                fop = FileProcessed(enc, _path)
                
                text = self.textToBuffer(open_next, enc)
                self.text_1.SetValue(text)
                logger.debug(f"Open_next: {os.path.basename(open_next)}, encoding: {enc}")
                fop.bufferText(text, self.workText)
                fop.bufferText(text, WORK_TEXT)
                self.SetStatusText(os.path.basename(open_next))
                self.open_next.Enable(False)
            except Exception as e:
                logger.debug(f"OpneNext error: {e}")
        else:
            askDlg.Destroy()
        event.Skip()
    
    def onReload(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled():
            dl1 = wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                                wx.ICON_QUESTION | wx.YES_NO, self)
            if dl1 == wx.NO:
                return        
        path = self.tmpPath[-1]
        enc = self.enchistory[path]
        
        fproc = FileProcessed(enc, path)
        
        if os.path.isfile(os.path.join('resources', 'var', 'r_text0.pkl')):
            with open(os.path.join('resources', 'var', 'r_text0.pkl'), 'rb') as f:
                text=pickle.load(f)
            
            self.reloadText = text
            self.text_1.SetValue(text)
            writeTempStr(path, text, enc)
            os.remove(os.path.join('resources', 'var', 'r_text0.pkl'))
            fproc.bufferText(text, WORK_TEXT)
            self.reloaded += 1
        else:
            text = self.reloadText
            self.text_1.SetValue(text)
            writeTempStr(path, text, enc)
            fproc.bufferText(text, WORK_TEXT)
            self.reloaded += 1
        logger.debug('Reloaded {}, encoding: {}'.format(os.path.basename(path), enc))
        
        event.Skip()
        
    def fileErrors(self, path, new_enc, multi):
        
        text = self.workText.getvalue()
        nlist = w_position('\?', text)     # Locira novonastale znakove ako ih ima
        epath = os.path.basename(path)
        outf = os.path.join(self.real_dir, os.path.splitext(epath)[0]+'_error.log')
        showMeError(path, text, outf, new_enc)
        text = text.replace('¬', '?')
        if multi == False:
            self.text_1.SetValue(text)
            for i in nlist:
                if not len(nlist) > 500:
                    a = i[0]
                    b = i[1]                        
                    self.text_1.SetStyle(a, b, wx.TextAttr("YELLOW","GREEN"))
                    self.text_1.SetInsertionPoint(b)
        return text
    
    def textToBuffer(self, path, enc):
        codelist = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-32', 'utf-16-be', 'utf-16-le', 'utf-32-be', 'utf-32-le']
        if enc in codelist: error = "surrogatepass"
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
                    logger.debug(f"TextToBuffer content: {os.path.basename(path)}")
            return text
        except Exception as e:
            logger.debug(f"textToBuffer error: {e}")
            
    def bytesToBuffer(self, text, enc):
        
        try:
            self.bytesText.truncate(0)
            self.bytesText.seek(0)
            self.bytesText.write(text.encode(enc))
            self.bytesText.seek(0)
        
            return self.bytesText.getvalue()
        
        except Exception as e:
            logger.debug(f"bytesToBuffer error: {e}")
        
        
    def toANSI(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            value4_s = ex['lat_ansi_srt']
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled():
            if self.ShowDialog() == False:
                return        
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toANSI_multiple()
        else:        
            self.enchistory[path] = entered_enc            
            self.previous_action.clear()
            
            self.newEnc = 'windows-1250'
            self.pre_suffix = value4_s
            
            if entered_enc == self.newEnc:
                logger.debug(f"toANSI, ecoding is already: {entered_enc}")
                InfoDlg = wx.MessageDialog(self, f"Tekst je već enkoding {entered_enc.upper()}.\nNastavljate?", "SubtitleConverter",
                                           style= wx.OK | wx.CANCEL|wx.CANCEL_DEFAULT | wx.ICON_INFORMATION)
                if InfoDlg.ShowModal() == wx.ID_CANCEL:
                    return
                else:
                    InfoDlg.Destroy()
                
            def ansiAction(inpath):
                fproc = FileProcessed(entered_enc, inpath)
                if not entered_enc == 'windows-1251':
                    logger.debug(f'toANSI: {os.path.basename(inpath)}, {entered_enc}')
                
                # text = WORK_TEXT.getvalue()                
                text = self.text_1.GetValue()
                
                text = fproc.rplStr(text)
                text = text.replace('?', '¬')
                new_fproc = FileProcessed(self.newEnc, inpath)
                text = bufferCode(text, self.newEnc)
                new_fproc.bufferText(text, self.workText)
                text = new_fproc.fixI(text)
                error_text = new_fproc.checkFile(inpath, inpath, text, multi=False)
                text = self.fileErrors(inpath, self.newEnc, multi=False)
                new_fproc.bufferText(text, self.workText)
                self.bytesToBuffer(text, self.newEnc)
                self.real_path = inpath
                
                self.tmpPath.append(inpath)
                if text:
                    msginfo = wx.MessageDialog(self, f'Tekst je konvertovan u enkoding: {self.newEnc.upper()}.',
                                               'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                    msginfo.ShowModal()
                    new_fproc.bufferText(text, WORK_SUBS)
                    new_fproc.bufferText(text, WORK_TEXT)
                return text, error_text
            
            def postAnsi():
                self.SetStatusText(os.path.basename(path))
                self.MenuBar.Enable(wx.ID_SAVE, True)
                self.MenuBar.Enable(wx.ID_SAVEAS, True)
                self.MenuBar.Enable(wx.ID_CLOSE, True)
                self.frame_toolbar.EnableTool(1010, True)  # Save
                self.frame_toolbar.EnableTool(101, True)
                self.previous_action['toANSI'] = self.newEnc
                self.enchistory[path] = self.newEnc
                self.reloaded = 0
            
            def dialog1(text_1):
                ErrorDlg = wx.MessageDialog(self, text_1, "SubtitleConverter",
                                            style= wx.OK | wx.CANCEL|wx.CANCEL_DEFAULT | wx.ICON_INFORMATION)
                if ErrorDlg.ShowModal() == wx.ID_OK:
                    return True
            
            fproc_a = FileProcessed(entered_enc, path)
            text = self.workText.getvalue()
            zbir_slova, procent, chars = fproc_a.checkChars(text)
            
            #----------------------------------------------------------------------------------------------------------
            if zbir_slova == 0 and procent == 0:
                text,error_text = ansiAction(path)
                fproc = FileProcessed(self.newEnc, path)
                if error_text:
                    ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                    ErrorDlg.ShowModal()
                    self.Error_Text = error_text
                postAnsi()
                self.previous_action['toANSI'] = entered_enc                
                self.enc = self.newEnc
            #----------------------------------------------------------------------------------------------------------
            elif procent > 0:
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                f_procent = 'Najmanje {} % teksta.\nIli najmanje [ {} ] znakova.'.format(procent, zbir_slova)
                ErrorText = "Greška:\n\nUlazni fajl sadrži ćiriliči alfabet.\n\n{}\n{}\n\nNastavljate?\n".format(f_procent, ",".join(chars))
                dlg = dialog1(ErrorText)
                if dlg == True:
                    if procent >= 50:
                        ErrorDlg = wx.MessageDialog(
                                self, "Too many errors!\n\nAre you sure you want to proceed?\n", "SubtitleConverter",
                                style=wx.CANCEL|wx.CANCEL_DEFAULT|wx.OK|wx.ICON_ERROR)
                        if ErrorDlg.ShowModal() == wx.ID_CANCEL:
                                        return
                    text,error_text = ansiAction(path)
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                        self.Error_Text = error_text
                    postAnsi()
                    
                    self.previous_action['toANSI'] = entered_enc
                    self.enc = self.newEnc
            #----------------------------------------------------------------------------------------------------------
            elif zbir_slova > 0:
                f_zbir = 'Najmanje [ {} ] znakova.'.format(zbir_slova)
                ErrorText = "Greška:\n\nUlazni fajl sadrži ćiriliči alfabet.\n{}\n{}\n\nNastavljate?\n".format(f_zbir, ",".join(chars))
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                dlg = dialog1(ErrorText)
                if dlg == True:
                    text,error_text = ansiAction(path)
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                        self.Error_Text = error_text            
                    postAnsi()
                    self.previous_action['toANSI'] = entered_enc
                    self.enc = self.newEnc                        
        event.Skip()
        
    def toANSI_multiple(self):
        
        with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
            ex = pickle.load(f)     # ["key5"]
            value4_s = ex['lat_ansi_srt']
        
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        
        self.PathEnc()
            
        self.newEnc = 'windows-1250'
        self.pre_suffix = value4_s
        self.tmpPath.clear()
                
        for key, value in self.multiFile.items():
            
            path=key
            fpath = os.path.basename(path)
            entered_enc=value
            
            fproc = FileProcessed(entered_enc, path)
            
            if entered_enc == 'windows-1251':
                logger.debug(f"------------------------------------------------------\n\
                Encoding is windows-1251! {fpath}")
                self.text_1.AppendText("\n")
                self.text_1.AppendText(fpath+" __skipped_")                
                continue
               
            text = fproc.normalizeText()
            fproc.bufferText(text, self.workText)
            zbir_slova, procent, chars = fproc.checkChars(text)
            
            def ansiAction(path):
                if not entered_enc == 'windows-1251':
                    logger.debug('ToANSI, next input encoding: {}'.format(entered_enc))                    
                text = self.workText.getvalue()
                text = fproc.rplStr(text)
                text = text.replace('?', '¬')
                
                nam, b = fproc.newName(self.pre_suffix, True)
                newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)                
                text = bufferCode(text, self.newEnc)
                new_fproc = FileProcessed(self.newEnc, newF)
                self.tmpPath.append(newF)
                text = new_fproc.fixI(text)
                new_fproc.bufferText(text, self.workText)
                return newF, text
            
            def postAnsi():
                self.SetStatusText('Processing multiple files.')
                self.previous_action['toANSI'] = self.newEnc
            def dialog1(text_1):
                ErrorDlg = wx.MessageDialog(self, text_1, "SubtitleConverter",
                                            style= wx.OK | wx.CANCEL|wx.CANCEL_DEFAULT | wx.ICON_INFORMATION)
                if ErrorDlg.ShowModal() == wx.ID_OK:
                    return True
                    
            if zbir_slova == 0 and procent == 0:
                newF,text = ansiAction(path)
                
                error_text = fproc.checkFile(path, newF, text, multi=True)
                
                text = self.fileErrors(newF, self.newEnc, multi=True)
                fproc.bufferText(text, self.workText)
                newfproc = FileProcessed(self.newEnc, newF)
                newfproc.writeToFile(text)
                
                self.text_1.AppendText('\n')
                self.text_1.AppendText(os.path.basename(newF))                
                if error_text:
                    ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                    ErrorDlg.ShowModal()
                postAnsi()
                
            elif procent > 0:
                logger.debug(f'ToANSI: Cyrillic alfabet u tekstu: {entered_enc} cyrillic')
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                f_procent = 'Najmanje {} % teksta.\nIli najmanje [ {} ] znakova.'.format(procent, zbir_slova)
                ErrorText = "Greška:\n\n{0}\nsadrži ćiriliči alfabet.\n{1}\n{2}\n\nNastavljate?\n"\
                    .format(os.path.basename(path), f_procent, ",".join(chars))
                
                dlg = dialog1(ErrorText)
                
                if dlg == True:
                    if procent >= 50:
                        ErrorDlg = wx.MessageDialog(
                                self, "Too many errors!\n\nAre you sure you want to proceed?\n", "SubtitleConverter",
                                style=wx.CANCEL|wx.CANCEL_DEFAULT|wx.OK|wx.ICON_ERROR)
                        if ErrorDlg.ShowModal() == wx.ID_CANCEL:
                            continue
                    newF,text = ansiAction(path)
                    error_text = fproc.checkFile(path, newF, text, multi=True)
                    newfproc = FileProcessed(self.newEnc, newF)
                    
                    text = self.fileErrors(newF, self.newEnc, multi=True)
                    newfproc.bufferText(text, self.workText)
                    newfproc.writeToFile(text)
                    
                    self.text_1.AppendText('\n')
                    self.text_1.AppendText(os.path.basename(newF))                    
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                    postAnsi()
                    
            elif zbir_slova > 0:
                logger.debug(f'ToANSI: Cyrillic alfabet u tekstu: {entered_enc} cyrillic')
                f_zbir = 'Najmanje [ {} ] znakova.'.format(zbir_slova)
                ErrorText = "Greška:\n\n{0}\nsadrži ćiriliči alfabet.\n{1}\n{2}\n\nNastavljate?\n"\
                    .format(os.path.basename(path),f_zbir, ",".join(chars))
                
                dlg = dialog1(ErrorText)
                
                if dlg == True:
                    newF,text = ansiAction(path)
                    error_text = fproc.checkFile(path, path, text, multi=True)
                    newfproc = FileProcessed(self.newEnc, newF)
                    
                    self.text_1.AppendText('\n')
                    self.text_1.AppendText(os.path.basename(newF))
                    
                    text = self.fileErrors(newF, self.newEnc, multi=True)
                    newfproc.bufferText(text, self.workText)
                    newfproc.writeToFile(text)
                    
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                    postAnsi()
                    
        self.SetStatusText('Multiple files done.')            
        self.multipleTools()
        
    def toCyrillic(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            value1_s = ex['cyr_ansi_srt']
            value2_s = ex['cyr_utf8_txt']
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled():
            if self.ShowDialog() == False:
                return
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toCyrillic_multiple()
        
        else:        
            self.previous_action.clear()
                
            self.newEnc = 'windows-1251'
            
            self.pre_suffix = value1_s
            
            fproc = FileProcessed(entered_enc, path)
            # text = WORK_TEXT.getvalue()
            text = self.text_1.GetValue()
            
            if text: text = text.replace('?', '¬')
            
            utfText, suffix = fproc.newName(value2_s, multi=False)
            
            if self.preferences.IsChecked(1011):  
                utf8_enc = 'utf-8-sig'
            else:
                utf8_enc = 'utf-8'
            utf_path = os.path.join(self.real_dir, utfText+suffix)
            
            if os.path.exists(utf_path):
                nnm = fproc.nameCheck(os.path.basename(utf_path), self.real_dir, suffix)+1
                utf_path = '{0}_{1}{2}'.format(utf_path, nnm, suffix)
                
            self.cyrUTF = utf_path
            self.orig_path = path
                   
            new_fproc = FileProcessed(utf8_enc, utf_path)
            
            text = bufferCode(text, utf8_enc)
            text = new_fproc.fixI(text)
            
            cyr_proc = Preslovljavanje(utf8_enc, utf_path)
            text = cyr_proc.preLatin(text)
            text = cyr_proc.preProc(text, reversed_action=False)
            text = cyr_proc.changeLetters(text, reversed_action=False)
            text = cyr_proc.rplStr(text)    
            text = cyr_proc.fineTune(text)
            text = cyr_proc.fontColor(text)
            
            cyr_path = path
            text = bufferCode(text, self.newEnc)
            cyr_proc.bufferText(text, self.workText)
            
            error_text = cyr_proc.checkFile(path, cyr_path, text, multi=False)
            text = self.fileErrors(cyr_path, self.newEnc, multi=False)
            
            new_fproc.writeToFile(text)
            
            cyr_proc.bufferText(text, WORK_SUBS)
            cyr_proc.bufferText(text, WORK_TEXT)
            cyr_proc.bufferText(text, self.workText)
            self.bytesToBuffer(text, self.newEnc)
            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            
            self.enc = self.newEnc
            
            if path:
                
                self.SetStatusText(os.path.basename(path))
                
                self.postAction()
                
                self.frame_toolbar.EnableTool(1003, False)   # toANSI
                self.to_ansi.Enable(False)
                
                self.enchistory[path] = self.newEnc
                self.previous_action['toCYR'] = self.newEnc
                self.reloaded = 0
                
        event.Skip()
        
    def toCyrillic_multiple(self):
        
        with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
            ex = pickle.load(f)     # ["key5"]   
            value1_s = ex['cyr_ansi_srt']
            value2_s = ex['cyr_utf8_txt']
            
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        
        self.newEnc = 'windows-1251'
        self.pre_suffix = value1_s
        
        self.PathEnc()
            
        self.tmpPath.clear()
        self.cyrUTFmulti.clear()
        
        for key, value in self.multiFile.items():
            
            path=key
            entered_enc=value
            
            fproc = FileProcessed(entered_enc, path)
            
            file_suffix = os.path.splitext(path)[-1]
            
            text = fproc.normalizeText()
            if text:
                text = text.replace('?', '¬')
            
            utfText, suffix = fproc.newName(value2_s, multi=True)   # 'cyr_utf8'
            
            if self.preferences.IsChecked(1011):  
                utf8_enc = 'utf-8-sig'
            else:
                utf8_enc = 'utf-8'
                
            utf_path = os.path.join(self.real_dir, utfText+suffix)
            self.cyrUTFmulti.append(utf_path)
            
            if os.path.exists(utf_path):
                nnm = fproc.nameCheck(os.path.basename(utf_path), self.real_dir, suffix)
                utf_path = '{0}_{1}{2}'.format(utf_path, nnm, suffix)
            
            new_fproc = FileProcessed(utf8_enc, utf_path)
            text = bufferCode(text, utf8_enc)
            text = new_fproc.fixI(text)  # Isto kao i kod rplStr text
            
            cyr_name, cyr_suffix = new_fproc.newName(self.pre_suffix, multi=True)
            
            cyr_path = os.path.join(self.real_dir, cyr_name+file_suffix)
            
            self.tmpPath.append(cyr_path)
                
            cyr_proc = Preslovljavanje(utf8_enc, utf_path)
            text = cyr_proc.preLatin(text)
            text = cyr_proc.preProc(text, reversed_action=False)
            text = cyr_proc.changeLetters(text, reversed_action=False)
            text = cyr_proc.rplStr(text)    # Ovde ide tekst ne putanja
            text = bufferCode(text, utf8_enc)
            text = cyr_proc.fineTune(text)
            text = cyr_proc.fontColor(text)
            cyr_proc.bufferText(text, self.workText)
            
            error_text = cyr_proc.checkFile(utf_path, cyr_path, text, multi=True)
            text = self.fileErrors(cyr_path, self.newEnc, multi=True)
            
            cyr_ansi = Preslovljavanje(self.newEnc, cyr_path)
            text_ansi = bufferCode(text, self.newEnc)            
            
            cyr_proc.writeToFile(text)
            cyr_ansi.writeToFile(text_ansi)
            
            self.text_1.AppendText('\n')
            self.text_1.AppendText(os.path.basename(cyr_path))
            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            
            self.enc = self.newEnc
            self.SetStatusText('Processing multiple files')
            self.previous_action['toCYR_multiple'] = self.newEnc
            
        self.reloaded = 0   
        self.SetStatusText('Multiple files done.')
        self.multipleTools()
        self.frame_toolbar.EnableTool(1003, False)
        self.to_ansi.Enable(False)        
        
    def toCyrSRT_utf8(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            value1_s = ex['cyr_ansi_srt']
            value2_s = ex['cyr_utf8_txt']
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled():
            dl = self.ShowDialog()
            if dl == False:
                return
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toCyrSRTutf8_multiple()
        else:        
            self.enchistory[path] = entered_enc
            self.previous_action.clear()
                
            self.pre_suffix = value1_s
            
            fproc = FileProcessed(entered_enc, path)
            # text = WORK_TEXT.getvalue()
            text = self.text_1.GetValue()
            
            if text: text = text.replace('?', '¬')
            
            utfText, suffix = fproc.newName(value2_s, multi=False)
            suffix = ".srt"
            
            if self.preferences.IsChecked(1011):  
                utf8_enc = 'utf-8-sig'
            else:
                utf8_enc = 'utf-8'
                
            real_dir = os.path.dirname(self.real_path[-1])    
            utf_path = os.path.join(real_dir, utfText+suffix)
            self.cyrUTF = utf_path
            
            if os.path.exists(utf_path):
                nnm = fproc.nameCheck(os.path.basename(utf_path), real_dir, suffix)+1
                utf_path = '{0}_{1}{2}'.format(utf_path, nnm, suffix)
                
            new_fproc = FileProcessed(utf8_enc, utf_path)
            text = bufferCode(text, utf8_enc)
            text = new_fproc.fixI(text)
            
            cyr_proc = Preslovljavanje(utf8_enc, utf_path)
            text = cyr_proc.preLatin(text)
            text = cyr_proc.preProc(text, reversed_action=False)
            text = cyr_proc.changeLetters(text, reversed_action=False)
            text = cyr_proc.rplStr(text)
            text = bufferCode(text, utf8_enc)
            text = cyr_proc.fineTune(text)
            text = cyr_proc.fontColor(text)
            cyr_proc.bufferText(text, self.workText)
            cyr_proc.bufferText(text, WORK_TEXT)
            
            error_text = cyr_proc.checkFile(path, utf_path, text, multi=False)
            text = self.fileErrors(utf_path, utf8_enc, multi=False)
            
            cyr_proc.writeToFile(text)  # Write corrected text to file
            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            
            self.newEnc = utf8_enc
            
            self.SetStatusText(os.path.basename(path))
            
            self.postAction()
            
            self.frame_toolbar.EnableTool(1010, False)  # Save
            self.to_ansi.Enable(False)
            self.frame_toolbar.EnableTool(1003, False)
            self.save.Enable(False)
            
            
            self.enchistory[path] = self.newEnc
            self.previous_action['toCyrSRTutf8'] = self.newEnc
            self.cyrUTF = utf_path
                
        event.Skip()
        
    def toCyrSRTutf8_multiple(self):
        
        with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
            ex = pickle.load(f)     # ["key5"]
            value1_s = ex['cyr_ansi_srt']
            value3_s = ex['cyr_utf8_srt']            
        
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        
        self.pre_suffix = value1_s
        
        self.PathEnc()
        self.tmpPath.clear()
        self.cyrUTFmulti.clear()
        
        if self.preferences.IsChecked(1011):  
            utf8_enc = 'utf-8-sig'
        else:
            utf8_enc = 'utf-8'        
        
        for key, value in self.multiFile.items():
            
            path=key
            entered_enc=value
            
            fproc = FileProcessed(entered_enc, path)
            text = fproc.normalizeText()
            
            if text:
                text = text.replace('?', '¬')
                
            utfText, suffix = fproc.newName(value3_s, multi=True)   # 'cyr_utf8'
            suffix = ".srt"
                
            utf_path = os.path.join(self.real_dir, utfText+suffix)
            self.cyrUTFmulti.append(utf_path)
            
            if os.path.exists(utf_path):
                nnm = fproc.nameCheck(os.path.basename(utf_path), self.real_dir, suffix)+1
                utf_path = '{0}_{1}{2}'.format(utf_path, nnm, suffix)
            
            new_fproc = FileProcessed(utf8_enc, utf_path)
            text = bufferCode(text, utf8_enc)
            text = new_fproc.fixI(text)
            
            cyr_proc = Preslovljavanje(utf8_enc, utf_path)
            text = cyr_proc.preLatin(text)
            text = cyr_proc.preProc(text, reversed_action=False)
            text = cyr_proc.changeLetters(text, reversed_action=False)
            text = cyr_proc.rplStr(text)    
            text = cyr_proc.fineTune(text)
            text = cyr_proc.fontColor(text)
            cyr_proc.bufferText(text, self.workText)
            
            self.tmpPath.append(utf_path)
            self.newEnc = utf8_enc
            
            error_text = cyr_proc.checkFile(path, utf_path, text, multi=True)
            text = self.fileErrors(utf_path, self.newEnc, multi=True)
            
            cyr_proc.writeToFile(text)
            
            self.text_1.AppendText('\n')
            self.text_1.AppendText(os.path.basename(utf_path))
            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            
            self.SetStatusText('Processing multiple files')
            
        self.reloaded = 0
        self.previous_action['toCyrSRTutf8_multiple'] = self.newEnc
        self.SetStatusText('Multiple files done.')
        self.multipleTools()
                
    def toUTF(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            value1_s = ex['lat_utf8_srt']        
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and self.reloaded == 0:
            if self.ShowDialog() == False:
                return
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toUTF_multiple()
        else:
            self.enchistory[path] = entered_enc
            cyr_utf = ""
            if self.previous_action:
                cyr_utf = list(self.previous_action.keys())[0]
            self.previous_action.clear()
            
            self.pre_suffix = value1_s
            
            if self.preferences.IsChecked(1011):
                self.newEnc = 'utf-8-sig'
            else:
                self.newEnc = 'utf-8'
            action_l = ["toCyrSRTutf8", "toCYR"]
            if entered_enc == "utf-8" or entered_enc == "utf-8-sig" and not cyr_utf in action_l:
                code = "UTF-8"
                if entered_enc == "utf-8-sig":
                    code = "BOM_UTF-8"                
                logger.debug(f"toUTF: Encoding is {entered_enc}.")
                InfoDlg = wx.MessageDialog(self, f"Tekst je već enkoding {code}.\nNastavljate?", "SubtitleConverter",
                                           style= wx.OK | wx.CANCEL|wx.CANCEL_DEFAULT | wx.ICON_INFORMATION)
                if InfoDlg.ShowModal() == wx.ID_CANCEL:
                    return
                else:
                    InfoDlg.Destroy()
            
            # text = WORK_TEXT.getvalue()
            text = self.text_1.GetValue()
            
            utfproc = FileProcessed(self.newEnc, path)
            text = bufferCode(text, self.newEnc)   # change to newEnc
            text = utfproc.fixI(text)
            utfproc.bufferText(text, self.workText)# StringIO
            self.text_1.SetValue(text)
            
            self.real_path = path
            
            if text:
                if self.newEnc == "utf-8-sig":
                    code = "BOM_UTF-8"
                else:
                    code = self.newEnc.upper()
                    
                utfproc.bufferText(text, WORK_SUBS)
                utfproc.bufferText(text, WORK_TEXT)
                self.bytesToBuffer(text, self.newEnc)
                msginfo = wx.MessageDialog(self, f'Tekst je konvertovan u enkoding: {code}.', 'SubtitleConverter',
                                           wx.OK | wx.ICON_INFORMATION)
                msginfo.ShowModal()
                
            self.enc = self.newEnc
            self.SetStatusText(os.path.basename(path))
            
            self.postAction()
            
            self.previous_action['toUTF'] = self.newEnc
            self.enchistory[path] = self.newEnc
                            
        event.Skip()
        
    def exportZIPmultiple(self):
        
        self.PathEnc()
        
        tpath = os.path.basename(list(self.multiFile)[0][:-4])
        epattern = re.compile(r"episode\s*-*\d*", re.I)
        tpath = epattern.sub("", tpath)
        tpath = re.sub(r"e01", "", tpath, count=1, flags=re.I)
        tpath = tpath.replace(" 1 ", "").replace("x01", "").replace("  ", " ")
        
        sas_wildcard =  "ZipArchive (*.zip)|*.zip|All Files (*.*)|*.*"
    
        dlg = wx.FileDialog(self, message="Export file as ZIP",\
                                defaultDir=self.real_dir, defaultFile="", wildcard=sas_wildcard,\
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        dlg.SetFilename(tpath)
        
        def t_out(textin):
            tout = ""
            for i in textin:
                tout += i+"\n"
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
            
            if list(self.previous_action.keys())[-1] == 'toCYR_multiple':
                
                izbor_ansi = []
                izbor_txt = []
                _txt_list = []
                
                for i, x in zip(self.tmpPath, self.cyrUTFmulti):
                    
                    tANSI = os.path.join("tmp", os.path.basename(i))            # ansi cirilica
                    tUTF = os.path.join("tmp", os.path.basename(x))             # utf_txt fajlovi
                    if not os.path.exists(tANSI):
                        shutil.copy(i, tANSI)
                    if not os.path.exists(tUTF):
                        shutil.copy(x, tUTF)
        
                    info2 = os.path.basename(tUTF)
                    izbor_ansi.append(tANSI)
                    izbor_txt.append(x)
                    _txt_list.append(info2)
                izbor = izbor_ansi+izbor_txt
                
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
                    l_srt_list.append("...\n...\nUkupno [{}]".format(len(lat_srt)))
                elif len(lat_srt) < 16:
                    l_srt_list = [x for x in lat_srt]                
                
                text1 = "Include original latin?\n\nPostojeći *latin fajlovi:\n\n{}".format(t_out(l_srt_list))
                text = "Include utf-8?\n\nPostojeći  *utf-8* fajlovi:\n\n{}".format(t_out(p_txt_list))
                dlg = wx.RichMessageDialog(self, text, "{}".format(os.path.basename(name)), wx.YES_NO|wx.ICON_QUESTION)
                dlg1 = wx.RichMessageDialog(self, text1, "{}".format(os.path.basename(name)), wx.YES_NO|wx.ICON_QUESTION)
                
                if dlg.ShowModal() == wx.ID_YES:
                    
                    files = izbor
                    zlist_a = [data_out(x) for x in files if x.endswith('.txt')]
                    zlist_b = [data_out(x) for x in files if x.endswith('.srt')]
                    info = [os.path.basename(x) for x in izbor]
                    zlist = zlist_b + zlist_a
                    
                if dlg1.ShowModal() == wx.ID_YES:
                    
                    files = lat_files
                    zlist_c =[data_out(x) for x in files if i.endswith('.srt')]
                    info = info + lat_srt
                    zlist = zlist + zlist_c
                        
                #else:
                    #files = izbor
                    #zlist = [data_out(x) for x in files if x.endswith('.txt')]
                    #info = [os.path.basename(x) for x in files]
            else:
                zlist = []
                try:
                    izbor = [os.path.join("tmp", x) if not x.startswith("tmp") else x for x in\
                             self.tmpPath if not x.endswith(".zip")]
                    info = [os.path.basename(x) for x in self.tmpPath if not x.endswith(".zip")]
                    for i,x in zip(self.tmpPath, izbor):
                        if not os.path.exists(x) and not i.endswith(".zip"):
                            shutil.copy(i, x)
                    zlist = [data_out(x) for x in izbor]
                except IOError as e:
                    logger.debug(f"ExportZIP IOError: {e}")
                    logger.debug("exportZIP IOError {}: ".format(sys.exc_info()[1:]))
                except Exception:
                    logger.debug("ExportZIP_A error, {}".format(sys.exc_info()))                
                    
            if list(self.previous_action.keys())[-1] == 'toCyrSRTutf8_multiple':
                files = izbor
                zlist = [data_out(x) for x in files]
                info = [os.path.basename(x) for x in files]
            #else:
                #files = izbor
                #zlist = [data_out(x) for x in files if not x.endswith('.zip')]
                #info = [os.path.basename(x) for x in files if not x.endswith('.zip')]
                #try:
                    #for i in self.tmpPath:
                        #os.remove(i)
                        #logger.debug("Removed {}".format(i))
                #except Exception:
                    #logger.debug("Remove files error, {}".format(sys.exc_info()))
            try:
                with zipfile.ZipFile(name, 'w') as fzip:
                    for i,x in zip(info, zlist):
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
                logger.debug("Export ZIP_final, IOError({0}{1}):".format(tpath, e))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                logger.debug(''.join('!' + line for line in lines))
    
            if os.path.isfile(path):
                logger.debug("ZIP file saved sucessfully: {}".format(path))
                sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(path)),\
                                        'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[path] = self.newEnc                
                self.open_next.Enable(True)
        else:
            dlg.Destroy()
    
    def toUTF_multiple(self):
        
        with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
            ex = pickle.load(f)     # ["key5"]
            value1_s = ex["lat_utf8_srt"]
        
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")

        self.PathEnc()
        
        self.tmpPath.clear()
        self.pre_suffix = value1_s
        
        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'        
        entered_enc = ""
        for key, value in self.multiFile.items():
                    
            path=key
            entered_enc=value
            
            fproc = FileProcessed(entered_enc, path)
            text = fproc.normalizeText()
            if text:
                text = text.replace('?', '¬')
                
            nam, b = fproc.newName(self.pre_suffix, True)
            newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)
            
            newFproc = FileProcessed(self.newEnc, newF)
            text = bufferCode(text, self.newEnc)
            self.tmpPath.append(newF)  # VAZNO
            text = newFproc.fixI(text)
            newFproc.bufferText(text, self.workText)
            
            error_text = fproc.checkFile(path, newF, text, multi=True)
            
            text = self.fileErrors(newF, self.newEnc, multi=True)
            
            newFproc.writeToFile(text)
            
            self.text_1.AppendText('\n')
            self.text_1.AppendText(os.path.basename(newF))
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
            self.SetStatusText('Processing multiple files.')
        
        self.multipleTools()
        if entered_enc == "windows-1251":
            self.frame_toolbar.EnableTool(1003, False)
            self.to_ansi.Enable(False)
            msginfo = wx.MessageDialog(self, f'Novi enkoding: {self.newEnc} Ćirilica.', 'SubtitleConverter',
                                       wx.OK | wx.ICON_INFORMATION)
            msginfo.ShowModal()
        self.reloaded = 0
        self.previous_action['toUTF_multiple'] = self.newEnc
        self.SetStatusText('Multiple files done.')
        
    def onTranscribe(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            value1_s = ex['transcribe']        
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and self.reloaded == 0:
            if self.ShowDialog() == False:
                return
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            return
    
        self.enchistory[path] = entered_enc
        self.pre_suffix = value1_s
        
        self.previous_action.clear()
        
        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'
        
        # text = WORK_TEXT.getvalue()
        text = self.text_1.GetValue()
        
        utf_proc = FileProcessed(self.newEnc, path)
        text = bufferCode(text, self.newEnc)
        text = utf_proc.fixI(text)
        
        newfproc = TextProcessing(self.newEnc, path)
        num = newfproc.zameniImena(text)
        
        if num > 28 or num < 28 and num > 2:
            msginfo = wx.MessageDialog(self, f'Zamenjenih objekata\nukupno [ {num} ]',
                                       'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
            msginfo.ShowModal()
        text = newfproc.getContent(None)
        text = newfproc.rplStr(text)
        self.text_1.SetValue(text)
        newfproc.bufferText(text, WORK_TEXT)
        newfproc.bufferText(text, self.workText)
        self.bytesToBuffer(text, self.newEnc)
        self.real_path = path
        
        self.enc = self.newEnc
        self.SetStatusText(os.path.basename(path))
        
        self.postAction()
        
        self.previous_action['Transcribe'] = self.newEnc
        self.enchistory[path] = self.newEnc
        
        event.Skip()
        
    def onRepSpecial(self, event):
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and self.reloaded == 0:
            if self.ShowDialog() == False:
                return
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1:
            return
    
        self.enchistory[path] = entered_enc
        self.newEnc = entered_enc
        self.previous_action.clear()
        
        self.pre_suffix = 'rpl'
        
        fproc = TextProcessing(entered_enc, path)
        
        # text = WORK_TEXT.getvalue()
        text = self.text_1.GetValue()
        
        text = text.replace('?', '¬')
        
        num,text_o = fproc.doReplace(text)
        fproc.bufferText(text_o, self.workText)
        
        error_text = fproc.checkFile(path, path, text_o, multi=False)
        text_s = self.fileErrors(path, entered_enc, multi=False)
        
        fproc.bufferText(text_s, WORK_SUBS)
        fproc.bufferText(text_s, WORK_TEXT)
        fproc.bufferText(text_s, self.workText)
        
        self.bytesToBuffer(text_s, entered_enc)
        self.real_path = path
        
        msginfo = wx.MessageDialog(self, 'Zamenjenih objekata\nukupno [ {} ]'\
                                   .format(num), 'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
        msginfo.ShowModal()            
        if error_text:
            ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
            ErrorDlg.ShowModal()
            self.Error_Text = error_text
        
        self.SetStatusText(os.path.basename(path))
        
        self.postAction()
        
        self.previous_action['repSpec'] = self.newEnc
        
        event.Skip()
        
    def applyRegex(self, event):
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and self.reloaded == 0:
            if self.ShowDialog() == False:
                return

        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1: return
        
        self.previous_action.clear()
        
        self.pre_suffix = "reg"
        
        fproc = TextProcessing(entered_enc, path)
        
        # text = WORK_TEXT.getvalue()
        text = self.text_1.GetValue()
        
        d_file = os.path.join("resources", "Regex_def.config")
        
        with open(d_file, "r", encoding="utf-8") as f_open:
            
            reg_1 = re.compile('find=|\'|"', re.I)
            cn = 0
            
            for line in f_open:
                
                cn += 1
                if line.startswith("#"): continue
                if not line: continue
                
                line = line.strip().lower()
                
                if line and not "replace=" in line:
                    logger.debug(f"Apply Regex, missing argument, line {cn}; {d_file}")                
                
                x = line.split("replace=")
                
                finds = re.sub(reg_1, '', x[0]).strip()
                reps = re.sub(reg_1, '', x[-1]).strip()
                
                if reps:
                    x = reps.split("#")
                    if x[-1]: reps = x[0].strip()
                    
                try:
                    if "ignorecase" in reps:
                        reps = reps.replace("ignorecase", "").strip()
                        rflags = (re.M | re.I)
                        reg_def = re.compile(finds, rflags)
                    else:
                        reg_def = re.compile(finds, re.M)
                    
                    text = reg_def.sub(reps, text)
                    
                except Exception as e:
                    logger.debug(f"Apply Regex error:\n_{d_file}_, line {cn}; {e}")
                
        self.text_1.SetValue(text)
        
        fproc.bufferText(text, WORK_TEXT)
        fproc.bufferText(text, self.workText)
        
        self.bytesToBuffer(text, entered_enc)
        self.real_path = path 
        
        self.SetStatusText(os.path.basename(path))
        
        self.postAction()
        
        self.previous_action['CustomRegex'] = entered_enc
                
        event.Skip()
        
    def PathEnc(self):

        if self.droped:
            self.multiFile.clear()
            self.multiFile.update(self.droped)
        
        if self.tmpPath and not self.multiFile:
            
            path = self.tmpPath[-1]
            entered_enc = self.enchistory[path]
            
            return path, entered_enc
        
        else: return "", ""
        
    def onCleanup(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            ef = sp['key1']
            cb8_s = ef["state8"]
            value1_s = ex['cleanup']        
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and self.reloaded == 0:
            if self.ShowDialog() == False: return
        
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1: return
    
        self.newEnc = entered_enc
        self.enchistory[path] = entered_enc
        self.pre_suffix = value1_s
        
        # text = WORK_TEXT.getvalue()
        text = self.text_1.GetValue()
        
        try:
            subs = list(srt.parse(text))
        
            subs = list(srt.parse(WORK_TEXT.getvalue()))
            subs = srt.compose(subs)
            
            fproc = TextProcessing(entered_enc, path)
            if "repSpec" or "Cleanup" in self.previous_action.keys():
                arg1 = False
            else: arg1 = True
            
            text = fproc.cleanUp(subs, arg1)
            
            self.previous_action.clear()
            
            deleted, trimmed,text_s = fproc.cleanLine(text)
            
            fproc.bufferText(text_s, WORK_TEXT)
            fproc.bufferText(text_s, self.workText)
            self.text_1.SetValue(text_s)
            logger.debug(f"CleanUp _1: {sys.exc_info()}")
            
            self.bytesToBuffer(text_s, entered_enc)
            self.real_path = path

            if (deleted + trimmed) == 0:
                msginfo = wx.MessageDialog(self, 'Subtitle clean\nno changes made.', 'SubtitleConverter',
                                           wx.OK | wx.ICON_INFORMATION)
                msginfo.ShowModal()
            else:
                msginfo = wx.MessageDialog(self, f'Subtitles deleted: [{deleted} ]\nSubtitles trimmed: [{trimmed} ]',\
                                           'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                msginfo.ShowModal()                
            
            self.SetStatusText(os.path.basename(path))
            self.previous_action['Cleanup'] = self.newEnc
            
            self.postAction()
                
        except Exception as e:
            logger.debug(f"Cleanup: {e}")
            self.previous_action['Cleanup'] = self.newEnc
            return
        
        event.Skip()
    
    def onMergeLines(self, event):
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and self.reloaded == 0:
            if self.ShowDialog() == False:
                return
        
        path, entered_enc = self.PathEnc()

        if len(self.multiFile) >= 1: return
    
        self.enchistory[path] = entered_enc
        self.newEnc = entered_enc                           # path je u tmp/ folderu
        
        try:
            with shelve.open(os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback') as  sp:
                ex = sp['key2']
                lineLenght = ex['l_lenght']; maxChar = ex['m_char']; maxGap = ex['m_gap']; file_suffix = ex['f_suffix']
        except IOError as e:
            logger.debug("Merger, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e:
            logger.debug("Merger, unexpected error:", sys.exc_info())        
        
        fproc = FileProcessed(entered_enc, path)
        
        try:
            # text = WORK_TEXT.getvalue()
            text = self.text_1.GetValue()
            subs_a=pysrt.from_string(text)
        
        except IOError as e:
            logger.debug("Merger srt, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e: logger.debug(f"Merger _1, unexpected error: {e}")
        
        if subs_a[1].start and subs_a[2].start == "00:00:00,000":
            
            msginfo = wx.MessageDialog(self, 'Erroneous subtitle\n\nAll values are zero!', 'SubtitleConverter',
                                       wx.OK | wx.ICON_INFORMATION)
            msginfo.ShowModal()
            return        
            
        self.pre_suffix = file_suffix
        
        if len(subs_a) > 0:
                
            myMerger(subs_in=subs_a, max_time=lineLenght, max_char=maxChar, _gap=maxGap, kode=entered_enc)
            
            b1 = len(pysrt.from_string(WORK_TEXT.getvalue()))
            a1 = len(subs_a)
            
            text = WORK_TEXT.getvalue()
            subs = list(srt.parse(text))
            text = srt.compose(subs)
            fproc.bufferText(text, WORK_TEXT)
            fproc.bufferText(text, self.workText)
            
            self.bytesToBuffer(text, entered_enc)
            self.real_path = path
            
            self.text_1.SetValue(text)
            
            try:
                prf = format(((a1 - b1) / a1 * 100), '.2f')
            except ZeroDivisionError as e:
                logger.debug(f"Merger Error: {e}")
            else:
                logger.debug("Merger: Spojenih linija ukupno: {}, ili {} %".format(a1 - b1, prf))
                sDlg = wx.MessageDialog(self, "Merged file:\n\nSpojenih linija ukupno: {0}, ili {1} %"
                                        .format(a1 - b1, prf), 'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                sDlg.ShowModal()
            
            self.SetStatusText(os.path.basename(path))
            
            self.postAction()
            
            self.previous_action['Merger'] = self.newEnc
        
        event.Skip()
    
    def onSave(self, event):
        
        tpath, enc = self.PathEnc()
        if tpath and enc:
            enc = self.enchistory[tpath]
            
            fproc = FileProcessed(enc, tpath)
            fname, nsuffix = fproc.newName(self.pre_suffix, multi=False)
            
            outpath = fproc.nameDialog(fname, nsuffix, self.real_dir)  # Puna putanja sa imenom novog fajla
            
            if outpath:
                text = self.workText.getvalue()
                sproc = FileProcessed(self.newEnc, outpath)
                sproc.writeToFile(text)
                self.reloadText = text
                if os.path.isfile(outpath):
                    logger.debug(f"File saved: {outpath}")
                    sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(outpath)),\
                                            'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                    sDlg.ShowModal()
                    # Dodaje putanju i enkoding u recnik
                    self.saved_file[outpath] = self.newEnc
                    self.MenuBar.Enable(wx.ID_SAVE, False)
                    self.MenuBar.Enable(wx.ID_SAVEAS, False)
                    self.frame_toolbar.EnableTool(1010, False)
                    self.open_next.Enable(True)
                    self.reload.Enable(True)
        event.Skip()
    
    def onSaveAs(self, event):
        
        sas_wildcard =  "SubRip (*.srt)|*.srt|MicroDVD (*.sub)|*.sub|Text File (*.txt)|*.txt|All Files (*.*)|*.*"
        real_dir = os.path.dirname(self.real_path[-1])
        dlg = wx.FileDialog(self, message="Save file as ...", defaultDir=real_dir,
                            defaultFile="", wildcard=sas_wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        try:
            if self.real_path:
                fname = os.path.basename(self.real_path[-1])
            else:
                fname = 'Untitled.srt'
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
            fproc = FileProcessed(self.newEnc, path)
            fproc.writeToFile(text)
            self.reloadText = text
            if os.path.isfile(path):
                logger.debug(f"File saved sucessfully. {path}")
                sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(path)),\
                                        'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[path] = self.newEnc                
                self.MenuBar.Enable(wx.ID_SAVE, False)
                self.MenuBar.Enable(wx.ID_SAVEAS, False)
                self.frame_toolbar.EnableTool(1010, False)
                self.open_next.Enable(True)
                self.reload.Enable(True)
                # self.saved += 1
                # self.resetTool()
        else:
            dlg.Destroy()
        event.Skip()
        
    def exportZIP(self, event):
        
        self.PathEnc()
        
        if len(self.multiFile) > 1:
            self.multipleTools()
            self.exportZIPmultiple()
        else:
            if self.droped:
                if len(self.droped) > 1:
                    return        
            fpath, e = self.PathEnc()
            tpath = os.path.basename(fpath)
                
            enc = self.newEnc
            sas_wildcard =  "ZipArchive (*.zip)|*.zip|All Files (*.*)|*.*"
            
            dlg = wx.FileDialog(self, message="Export file as ZIP",\
                                defaultDir=self.real_dir, defaultFile="", wildcard=sas_wildcard,\
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            try:
                if self.real_path:
                    fproc = FileProcessed(enc, tpath)
                    fname, nsufix = fproc.newName(self.pre_suffix, False)
                    
            except IOError as e:
                logger.debug("On ZIP IOError({0}):".format(e))
            except IndexError as e:
                logger.debug("On ZIP IndexError({0}):".format(e))
            
            dlg.SetFilename(fname)
            if not self.previous_action:
                logger.debug(f"Export Zip: Nothing to do.")
                return
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                dirname = os.path.dirname(path)
                name = path
                
                def data_out(buffer, _path):
                    if not _path == None:
                        f = open(_path, 'rb')
                        b_data = f.read()
                        f.close()
                        return b_data
                    if not buffer == None:
                        _data = buffer.getvalue()
                        _data = _data.replace(b"\n", b"\r\n")
                        buffer.seek(0)
                        return _data
                                    
                if list(self.previous_action.keys())[-1] == "toCYR":
                
                    tUTF = os.path.join("tmp", os.path.basename(self.cyrUTF))
                    shutil.copy(self.cyrUTF, tUTF)
                        
                    lat_file = fname + os.path.splitext(tpath)[-1] # info1 dodaje cyr pre_suffix i file se pise u ZIP pod tim imenom
                    lat_file = lat_file.strip('/')
                    info2 = os.path.basename(tUTF)
                    info1 = os.path.basename(self.orig_path)# [:-5]
                    izbor = [info1, info2, lat_file]
                    
                    dlg = wx.MultiChoiceDialog(self, 'Pick files:', os.path.basename(name), izbor)
                    if dlg.ShowModal() == wx.ID_OK:
                        response = dlg.GetSelections()
                        files = [izbor[x] for x in response]
                        zdata = ""
                        tzdata = ""
                        ldata = ""
                        if len(files) == 1:
                            try:
                                if info2 in files:
                                    info1 = None; lat_file = None
                                    tzdata = data_out(None, tUTF)
                                    logger.debug(f"Remove {self.cyrUTF}")
                                    os.remove(self.cyrUTF)
                                elif info1 in files:
                                    info2 = None; lat_file = None
                                    zdata = data_out(None, fpath)
                                    logger.debug(f"Remove {self.cyrUTF}")
                                    os.remove(self.cyrUTF)
                                elif lat_file in files:
                                    info1 = None; info2 = None
                                    ldata = data_out(self.bytesText, None)
                                    
                            except IOError as e:
                                logger.debug("Export ZIP, IOError({0}{1}):".format(fpath, e))
                            except:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                                logger.debug(''.join('!' + line for line in lines))
                                
                        elif len(files) >= 2:
                            try:
                                if not lat_file in files:
                                    lat_file = None
                                    zdata = data_out(None, fpath)
                                    tzdata = data_out(None, tUTF)
                                    logger.debug(f"Remove {self.cyrUTF}")
                                    os.remove(self.cyrUTF)
                                elif not info2 in files:
                                    info2 = None
                                    zdata = data_out(None, fpath)
                                    ldata = data_out(self.bytesText, None)
                                elif not info1 in files:
                                    info1 = None
                                    tzdata = data_out(None, tUTF)
                                    logger.debug(f"Remove {self.cyrUTF}")
                                    os.remove(self.cyrUTF)
                                    ldata = data_out(self.bytesText, None)
                                elif len(files) == 3:
                                    zdata = data_out(None, fpath)
                                    tzdata = data_out(None, tUTF)
                                    logger.debug(f"Remove {self.cyrUTF}")
                                    os.remove(self.cyrUTF)
                                    ldata = data_out(self.bytesText, None)
                            except IOError as e:
                                logger.debug("Export ZIP_2, IOError({0}):".format(e))
                                self.text_1.SetValue("Error!\nTry again.")
                            except:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                                logger.debug(''.join('!' + line for line in lines))
                                # self.text_1.SetValue("Error!\nTry again.")
                        
                    else:
                        tzdata = ""
                        zdata = ""
                        ldata = ""
                        lat_file = None; info1 = None; info2 = None
                        logger.debug("ZIP export: None selected")
                        logger.debug("On ZIP: None selected")
                        return
                            
                else:
                    previous_action = list(self.previous_action.keys())[-1]
                    if previous_action == 'toCyrSRTutf8':
                        tzdata = ""
                        ldata = ""
                        zdata = data_out(None, self.cyrUTF)
                        info1 = os.path.basename(self.cyrUTF).strip('/')
                        info2 = None
                        lat_file = None
                        os.remove(self.cyrUTF)
                    elif previous_action == "toUTF":
                        tzdata = data_out(self.bytesText, None)
                        zdata = ""
                        ldata = ""
                        suffix = self.real_path[-4:]
                        if self.preferences.IsChecked(1012):
                            suffix = '.txt'
                        presuffix = self.pre_suffix
                        info2 = os.path.basename(self.real_path)[:-3]+presuffix+suffix
                        info1 = None
                        lat_file = None
                    else:
                        tzdata = data_out(self.bytesText, None)
                        zdata =""
                        ldata = ""
                        suffix = self.real_path[-4:]
                        presuffix = self.pre_suffix
                        info2 = os.path.basename(self.real_path)[:-3]+presuffix+suffix
                        info1 = None
                        lat_file = None
                try:
                    with zipfile.ZipFile(name, 'w') as fzip:
                        for i,x in zip([info1, info2, lat_file], [zdata, tzdata, ldata]):
                            if i == None:
                                continue
                            if len(x) == 0:
                                continue
                            fzip.writestr(i, x, zipfile.ZIP_DEFLATED)
                
                except IOError as e:
                    logger.debug("Export ZIP, IOError({0}{1}):".format(fpath, e))
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                    logger.debug(''.join('!' + line for line in lines))
    
                shutil.move(name, os.path.join(dirname, name))
                
                if os.path.isfile(tpath):
                    os.remove(tpath)
                if os.path.isfile(path):
                    logger.debug("ZIP file saved sucessfully: {}".format(path))
                    sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'\
                                            .format(os.path.basename(path)), 'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                    sDlg.ShowModal()
                    # Dodaje putanju i enkoding u recnik
                    self.saved_file[path] = self.newEnc                
                    self.open_next.Enable(True)
                    # self.saved += 1
                    # self.resetTool()
            else:
                logger.debug(f"Export ZIP: None selected")
                return
        event.Skip()
    
    def onCloseFile(self, event):
        self.text_1.SetValue('')
        self.disableTool()
        if os.path.exists(self.path0_p):
            os.remove(self.path0_p)
        if os.path.exists(self.enc0_p):
            os.remove(self.enc0_p)        
        self.SetStatusText('Subtitle Converter is ready')        
        event.Skip()
        
    def onFileHistory(self, event):
        # get the file based on the menu ID
        fileNum = event.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(fileNum)
        enc = self.enchistory[path]
        # add it back to the history so it will be moved up the list
        self.filehistory.AddFileToHistory(path)
        self.enchistory[path] = enc
        fp = FileProcessed(enc, path)
        
        with open(path, 'r', encoding=enc, errors='replace') as f:
            text = f.read()
        self.text_1.SetValue(text)
        
        self.enableTool()
        
        logger.debug(f'From fileHistory: {os.path.basename(path)} encoding: {enc}')
        self.SetStatusText(os.path.basename(path))
        
        event.Skip()
        
    def onCyrToANSI(self, event):
        
        with shelve.open(os.path.join("resources", "var", "dialog_settings.db"), flag='writeback') as  sp:
            ex = sp['key5']
            value1_s = ex['lat_ansi_srt']        
        
        path, entered_enc = self.PathEnc()
            
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.cyrToANSI_multiple()
        else:        
            
            self.enchistory[path] = entered_enc            
            self.pre_suffix = value1_s
            
            self.newEnc = 'windows-1250'
            t_enc = 'utf-8'
            
            # text = WORK_TEXT.getvalue()
            text = self.text_1.GetValue()
            
            if text: text = text.replace('?', '¬')
                
            cyrproc = Preslovljavanje(t_enc, path)
            text = bufferCode(text, t_enc)
            text = cyrproc.fixI(text)
            text = cyrproc.preLatin(text)
            text = cyrproc.preProc(text, reversed_action=True)
            text = cyrproc.changeLetters(text, reversed_action=True)
            text = cyrproc.rplStr(text)
            
            cyr_path = path
            text = bufferCode(text, self.newEnc)
            cyrproc.bufferText(text, self.workText)            
            
            error_text = cyrproc.checkFile(path, cyr_path, text, multi=False)
            text = self.fileErrors(cyr_path, self.newEnc, multi=False)            
            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            
            cyrproc.bufferText(text, WORK_TEXT)
            cyrproc.bufferText(text, self.workText)
            self.bytesToBuffer(text, self.newEnc)
            self.real_path = path
            
            self.SetStatusText(os.path.basename(path))
            
            self.postAction()
            
            self.previous_action['cyrToANSI'] = self.newEnc
            self.enchistory[path] = self.newEnc
        event.Skip()
    
    def cyrToANSI_multiple(self):
        
        with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
            ex = pickle.load(f)     # ["key5"]
            value1_s = ex["lat_ansi_srt"]
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        
        self.PathEnc()
            
        self.tmpPath.clear()
        self.pre_suffix = value1_s
        self.newEnc = 'windows-1250'
        t_enc = 'utf-8'
        
        for key, value in self.multiFile.items():
            path=key
            entered_enc=value        
            
            fproc = FileProcessed(entered_enc, path)
            try:
                text = fproc.normalizeText()
                if text:
                    text = text.replace('?', '¬')
                
                cyrproc = Preslovljavanje(t_enc, path)
                text = bufferCode(text, t_enc)
                text = cyrproc.fixI(text)
                text = cyrproc.preLatin(text)
                text = cyrproc.preProc(text, reversed_action=True)
                text = cyrproc.changeLetters(text, reversed_action=True)
                text = cyrproc.rplStr(text)
                
                nam, b = fproc.newName(self.pre_suffix, True)
                newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)            
                
                self.text_1.AppendText('\n')
                self.text_1.AppendText(os.path.basename(newF))
                self.tmpPath.append(newF)
                
                text = bufferCode(text, self.newEnc)
                cyrproc.bufferText(text, self.workText)            
                
                error_text = cyrproc.checkFile(path, newF, text, multi=True)
                text = self.fileErrors(path, self.newEnc, multi=True)
                
                ansi_cyrproc = Preslovljavanje(self.newEnc, newF)
                ansi_cyrproc.writeToFile(text)
                
                if error_text:
                    ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                    ErrorDlg.ShowModal()
                    self.Error_Text = error_text
                self.SetStatusText(f"Processing {os.path.basename(newF)}")
            except Exception as e:
                logger.debug(f"cyrToANSI error: {e}")
                
        self.multipleTools()
        self.reloaded = 0
        self.previous_action['cyrToANSI_multiple'] = self.newEnc
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
                
            self.enchistory[path] = entered_enc        
                
            self.pre_suffix = value1_s
            
            if self.preferences.IsChecked(1011):
                self.newEnc = 'utf-8-sig'
            else:
                self.newEnc = 'utf-8'
            
            # text = WORK_TEXT.getvalue()
            text = self.text_1.GetValue()
            
            if text: text = text.replace('?', '¬')
                    
            cyproc = Preslovljavanje(self.newEnc, path)
            text = bufferCode(text, self.newEnc)
            text = cyproc.fixI(text)
            text = cyproc.preProc(text, reversed_action=True)
            text = cyproc.changeLetters(text, reversed_action=True)
            text = cyproc.rplStr(text)
            
            cyproc.bufferText(text, self.workText)
            
            error_text = cyproc.checkFile(path, path, text, multi=False)
            text = self.fileErrors(path, self.newEnc, multi=False)
            
            cyproc.bufferText(text, WORK_SUBS)
            cyproc.bufferText(text, WORK_TEXT)
            cyproc.bufferText(text, self.workText)
            self.bytesToBuffer(text, self.newEnc)
            
            self.real_path = path
            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            if path:
                self.SetStatusText(os.path.basename(path))
                
                self.postAction()
                
                self.previous_action['cyrToUTF'] = self.newEnc
                self.enchistory[path] = self.newEnc
        event.Skip()
        
    def cyrToUTF_multiple(self):
        
        with open(os.path.join("resources", "var", "file_ext.pkl"), "rb") as f:
            ex = pickle.load(f)     # ["key5"]
            value1_s = ex["lat_utf8_srt"]
        
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        
        self.PathEnc()
         
        self.pre_suffix = value1_s
        self.tmpPath.clear()
        
        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'       
        
        for key, value in self.multiFile.items():
            path=key
            entered_enc=value
            
            fproc = FileProcessed(entered_enc, path)
            text = fproc.normalizeText()
            if text:
                text = text.replace('?', '¬')
            
            nam, b = fproc.newName(self.pre_suffix, True)
            newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)            
            
            cyproc = Preslovljavanje(self.newEnc, newF)
            text = bufferCode(text, self.newEnc)
            text = cyproc.fixI(text)
            text = cyproc.preProc(text, reversed_action=True)
            text = cyproc.changeLetters(text, reversed_action=True)
            text = cyproc.rplStr(text)
            
            cyproc.bufferText(text, self.workText)
            
            error_text = cyproc.checkFile(path, newF, text, multi=True)
            text = self.fileErrors(newF, self.newEnc, multi=True)
            
            self.text_1.AppendText('\n')
            self.text_1.AppendText(os.path.basename(newF))
            self.tmpPath.append(newF)
            
            cyproc.writeToFile(text)
            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubtitleConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            self.SetStatusText(os.path.basename(path))
            
        self.multipleTools()
        self.reloaded = 0
        self.previous_action['cyrToUTF_multiple'] = self.newEnc
        self.SetStatusText('Multiple files done.')        
        
    def onFixSubs(self, event):
        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and self.reloaded == 0:
            if self.ShowDialog() == False:
                return
       
        path, entered_enc = self.PathEnc()
        
        if len(self.multiFile) >= 1: return        
        
        self.enchistory[path] = entered_enc
            
        try:
            with shelve.open(os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback') as  sp:
                ex = sp['key1']
                cb1_s = ex['state1']; cb2_s = ex['state2']; cb3_s = ex['state3']
                cb4_s = ex['state4']; cb5_s = ex['state5']; cb6_s = ex['state6']; cb7_s = ex['state7']; cb8_s = ex['state8']
                fx = sp['key5']
                value1_s = fx['fixed_subs']                
        except IOError as e:
            logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e:
            logger.debug(f"FixSubtitle error: {e}")
            
        self.pre_suffix = value1_s
        self.newEnc = entered_enc   # VAZNO za Save funkciju
        fproc = TextProcessing(entered_enc, path)
        
        # text=WORK_TEXT.getvalue()
        text = self.text_1.GetValue()
        subs=pysrt.from_string(text)
        
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
                m = 0; s1 = 0
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
                        m = 0; s1 = 0
                else:
                    logger.debug("Fixer: Remove gaps not enabled.")
            try:
                if not cb8_s:
                    text = WORK_TEXT.getvalue()
                    textis = srt.parse(text)
                    text = srt.compose(textis)
                else: text = WORK_TEXT.getvalue()
                
            except IOError as e:
                logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
            except Exception as e: 
                logger.debug(f"FixSubtitle, unexpected error: {e}")         
                        
            text = fproc.rm_dash(text)
            
            fproc.bufferText(text, WORK_TEXT)
            fproc.bufferText(text, self.workText)
            
            self.text_1.SetValue(text)
            
            self.bytesToBuffer(text, entered_enc)
            self.real_path = path
            
            if cb1_s == True:
                if not cb8_s == True:
                    if s1 > 1:
                        s1 = s1 - 1
                        m1 = '\nPreklopljenih linija ukupno: {}'.format(s1)
                        logger.debug(m1)
                    else:
                        m1 = ''
                    logger.debug('Fixer: Popravljenih gapova ukupno: {}'.format(m))
                    if m >= 0:
                        sDlg = wx.MessageDialog(self, 'Subtitle fix\n\nPopravljenih gapova između linija ukupno: {}\n{}'
                                                        .format(m, m1), 'SubtitleConverter', wx.OK | wx.ICON_INFORMATION)
                        sDlg.ShowModal()
        
        self.previous_action['FixSubtitle'] = self.newEnc
        self.SetStatusText(os.path.basename(path))
        
        self.postAction()
        
        event.Skip()
        
    def undoAction(self, event):
        
        event.Skip()
        
    def redoAction(self, event):
        
        event.Skip()
    
    def editShortcuts(self, event):
        
        dlg = SE.ShortcutEditor(self)
        dlg.FromMenuBar(self)
        
        if dlg.ShowModal() == wx.ID_OK:
            dlg.ToMenuBar(self)
        dlg.Destroy()        
        
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

    def onChoice(self, event):
        
        ctrl = event.GetEventObject()
        value = ctrl.GetValue()
        
        with open(filePath('resources', 'var', 'obsE.pkl'), 'wb') as f:
            pickle.dump(value, f)
            
        event.Skip()
    
    def utfSetting(self, event):
        
        if self.preferences.IsChecked(1012):
            item_txt = 'txt'
        else:
            item_txt = 'srt'
        with open(os.path.join('resources', 'var', 'tcf.pkl'), 'wb') as tf:
            pickle.dump(item_txt, tf)
            
        if self.preferences.IsChecked(1011):
            item = 'Checked'
        else:
            item = 'NotChecked'
        with open(os.path.join('resources', 'var', 'bcf.pkl'), 'wb') as fb:
            pickle.dump(item, fb)        

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
    
    def onMergerSettings(self, event):
        settings_dialog = Settings(None, -1, "")
        settings_dialog.ShowModal()        
        event.Skip()
    
    def onFixerSettings(self, event):
        fixer_dlg = FixerSettings(None)
        fixer_dlg.ShowModal()
        event.Skip()
        
    def onFileSettings(self, event):
        settings_dlg = FileSettings(None)
        settings_dlg.ShowModal()
        event.Skip()    
    
    def onQuit(self, event):
        with open(filePath("resources","var","set_size.pkl"), "wb") as wf:
            pickle.dump(self.fsize, wf)        
        tval = self.text_1.GetValue()
        prev = ""
        if self.previous_action:
            prev = list(self.previous_action.keys())[0]
        if not tval.startswith('Files ') and len(tval) > 0\
           and self.save.IsEnabled() and not prev == 'toCyrSRTutf8':
            dl1 = wx.MessageBox("Current content has not been saved! Proceed?",
                                "Please confirm", wx.ICON_QUESTION | wx.YES_NO, self)
            if dl1 == wx.NO:
                return
            else:
                self.Destroy()
        else:
            self.Destroy()
    
    def onClose(self, event):
        with open(filePath("resources","var","set_size.pkl"), "wb") as wf:
            pickle.dump(self.fsize, wf)        
        self.Destroy()
            
    def ShowDialog(self):
    
        if self.dont_show:
            return
    
        dlg = wx.RichMessageDialog(self, "Current conten has not been saved! Proceed?", "Please confirm!", style=wx.OK|wx.CANCEL)
        dlg.ShowCheckBox("Don't show this message again")
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.IsCheckBoxChecked():
                self.dont_show = True            
            return True
        else:
            if dlg.IsCheckBoxChecked():
                self.dont_show = True            
            return False
        
    def onChanged(self, event):
        
        if self.text_1.CanUndo():
            
            self.undo_text.append(self.text_1.GetValue())
            if len(self.undo_text) >= 30: self.undo_text=self.undo_text[1:]
            self.enableTool()
            
        event.Skip()
        
    def onUndo(self, event):
        
        place = self.text_1.GetLastPosition()
       
        if (place - self.text_1.GetInsertionPoint()) > 12:
            place=self.text_1.GetInsertionPoint()-1
        
        self.redo_text.append(self.text_1.GetValue())
        
        if self.undo_text:
            self.text_1.Undo()
            self.text_1.SetValue(self.undo_text[len(self.undo_text)-1])
            self.text_1.SetInsertionPoint(place)
            self.undo_text=self.undo_text[:-1]
        if len(self.redo_text) >= 60: self.redo_text=self.redo_text[1:]        
        event.Skip()
        
    def onRedo(self, event):
        
        event.Skip()
        
    def onCut(self, event):
        
        event.Skip()
        
    def onCopy(self, event):
        
        event.Skip()
        
    def onPaste(self, event):
        
        event.Skip()
        
    def onFind(self, event):
        
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
                        line = x[0].strip()+"="+shortcutsKey[x[0].strip()]+"\n"
                        new_f += line
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
    
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()