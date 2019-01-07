#  Copyright (C) 2018  padovaSR
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import codecs
import shutil
import zipfile
import pickle
import shelve
import pysrt
import srt
from collections import OrderedDict
from operator import itemgetter
import glob
from FileProcessing import FileProcessed, FileOpened, Preslovljavanje, writeTempStr, TextProcessing
from showError import w_position, showMeError
from merger_settings import Settings
from FixSettings import FixerSettings
from merge import myMerger, fixLast, fixGaps

import logging
from logging.handlers import RotatingFileHandler
import traceback

import wx

VERSION = "v0.5.7.0beta1"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = RotatingFileHandler('subtitle_converter.logging.log', mode='a', maxBytes=4000)
handler.setFormatter(formatter)
logger.addHandler(handler)



class FileDrop(wx.FileDropTarget):
    file_name = r""
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    def OnDropFiles(self, x, y, filenames):
        lfiles = [x for x in filenames]
        kodes = ''
        tpath = ''
        rpath = ''
        droped = 0
        # self.droped = lfiles[0]
        # fop = FileOpened(path)
        def file_go(infile, rfile):
            FileDrop.file_name = infile
            fop = FileOpened(infile)
            enc = fop.findCode()
            fproc = FileProcessed(enc, infile)
            fproc.normalizeText()
            fproc.regularFile(rfile)
            logger.debug(f"FileDrop: {os.path.basename(infile)}")
            text = fproc.getContent()
            self.window.SetValue(text)
            tpath = infile
            with open('resources\\var\\r_text0.pkl', 'wb') as t:
                pickle.dump(text, t)
            return enc, text
        if len(lfiles) > 1:
            new_d = OrderedDict()
            rpath = lfiles[-1]
            self.window.SetValue('Files List:\n')
            for i in range(len(lfiles)):
                if not zipfile.is_zipfile(lfiles[i]):
                    try:
                        tmp_path = os.path.join('tmp', os.path.basename(lfiles[i]))
                        if lfiles[i].endswith(('zip', 'srt', 'txt')):
                            shutil.copy(lfiles[i], tmp_path)
                    except:
                        logger.debug('FileDrop: Unexpected file type.')
                    else:
                        fop = FileOpened(tmp_path)
                        enc = fop.findCode()
                        fproc = FileProcessed(enc, tmp_path)
                        fproc.normalizeText()
                        new_d[tmp_path] = enc
                        text = os.path.basename(tmp_path)
                        self.window.AppendText("\n")
                        self.window.AppendText(text)
                else:
                    try:
                        fop = FileOpened(lfiles[i])
                        outfile, rfile = fop.isCompressed()
                        rpath = rfile
                    except:
                        logger.debug('FileDrop: No files selected.')
                    else:
                        if len(outfile) == 1:
                            fop = FileOpened(outfile[0])
                            enc = fop.findCode()
                            fproc = FileProcessed(enc, outfile[0])
                            fproc.normalizeText()
                            kodes = enc
                            nam = outfile[0]
                            tpath = nam
                            droped += 1
                            new_d[nam] = enc
                            text = os.path.basename(nam)
                            self.window.AppendText("\n")
                            self.window.AppendText(text)
                        elif len(outfile) > 1:
                            droped += 1
                            for i in range(len(outfile)):
                                fop = FileOpened(outfile[i])
                                enc = fop.findCode()
                                fproc = FileProcessed(enc, outfile[i])
                                fproc.normalizeText()
                                new_d[outfile[i]] = enc
                                text = os.path.basename(outfile[i])
                                self.window.AppendText("\n")
                                self.window.AppendText(text)                            
            logger.debug('FileDrop: Ready for multiple files.')
            with open('resources\\var\\droped0.pkl', 'wb') as f:
                pickle.dump(new_d, f)
            with open('resources\\var\\rpath0.pkl', 'wb') as f:
                pickle.dump(rpath, f, pickle.HIGHEST_PROTOCOL)
        else:
            for name in  lfiles:
                if zipfile.is_zipfile(name) == True:
                    logger.debug(f'ZIP archive: {os.path.basename(name)}')
                    try:
                        fop = FileOpened(name)
                        outfile, rfile = fop.isCompressed()
                        rpath = rfile
                    except:
                        logger.debug('No files selected.')
                    else:
                        if len(outfile) == 1:
                            enc, t = file_go(outfile[0], rfile)
                            kodes = enc
                            nam = outfile[0]
                            tpath = nam
                            droped += 1
                            empty = {}
                            with open('resources\\var\\droped0.pkl', 'wb') as d:
                                pickle.dump(empty, d)
                            self.window.SetValue(t)
                        elif len(outfile) > 1:
                            droped += 1
                            self.window.SetValue('Files List:\n')
                            new_d = OrderedDict()
                            for i in range(len(outfile)):
                                fop = FileOpened(outfile[i])
                                enc = fop.findCode()
                                fproc = FileProcessed(enc, outfile[i])
                                fproc.normalizeText()
                                new_d[outfile[i]] = enc
                                text = os.path.basename(outfile[i])
                                self.window.AppendText("\n")
                                self.window.AppendText(text)
                            with open('resources\\var\\droped0.pkl', 'wb') as f:
                                pickle.dump(new_d, f)
                            logger.debug('FileDrop: Ready for multiple files.')
                elif zipfile.is_zipfile(lfiles[0]) == False:
                    name = lfiles[0]
                    tmp_path = os.path.join('tmp', os.path.basename(name))
                    shutil.copy(name, tmp_path)
                    enc, txt1 = file_go(tmp_path, name)
                    rpath = name
                    kodes = enc
                    tpath = tmp_path
                    droped += 1
                    empty = {}
                    with open('resources\\var\\droped0.pkl', 'wb') as d:
                        pickle.dump(empty, d)
                    self.window.SetValue(txt1)
            # print('Droped_FILE tmp: ', tpath)
            with open('resources\\var\\rpath0.pkl', 'wb') as f:
                pickle.dump(rpath, f, pickle.HIGHEST_PROTOCOL)
            with open('resources\\var\\obs1.pkl', 'wb') as f:
                pickle.dump(droped, f, pickle.HIGHEST_PROTOCOL)
            with shelve.open('resources\\var\\dialog_settings.db', flag='writeback') as s:
                s['key3'] = {'tmPath': tpath, 'realPath': rpath, 'kode': kodes, 'drop': droped}        
        return True

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((637, 582))
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.text_1 = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_BESTWRAP | wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.TE_RICH)
        # drop target
        dt = FileDrop(self.text_1)
        self.text_1.SetDropTarget(dt)        
        self.frame_statusbar = self.CreateStatusBar(1)
        
        self.wildcard = "SubRip (*.zip; *.srt)|*.zip;*.srt|MicroDVD (*.sub)|*.sub|Text File (*.txt)|*.txt|All Files (*.*)|*.*"
        self.modify = False
        self.dont_show = False
        self.undohist=[]
        self.redohist=[]
        self.real_path = []
        self.tmpPath = []
        self.undoAction = []
        self.redoAction = []
        self.enchistory = OrderedDict()
        self.multiFile = OrderedDict()
        self.saved_file = OrderedDict()
        self.pre_suffix = r""
        self.location = r"tmp"
        self.newEnc = r""
        self.orig_path = r""
        self.real_dir = r""
        self.pre_suffix = r""
        self.Error_Text = r""
        self.reloadText = r""
        self.cyrUTF = r""
        self.reloaded = 0
        self.previous_action= {}
            
        self.__set_menuBar()
        self.__set_ToolBar()
        self.__set_properties()
        self.__do_layout()
        
        self.filehistory = wx.FileHistory()
        self.filehistory.UseMenu(self.file_sub)
        self.filehistory.AddFilesToMenu()        
        
        # MenuBar events
        self.Bind(wx.EVT_MENU, self.utfSetting, id=-1)
        
        # Toolbar events
        self.Bind(wx.EVT_TOOL, self.onOpen, id = 1001)
        self.Bind(wx.EVT_TOOL, self.onSave, id = 1010)
        self.Bind(wx.EVT_TOOL, self.toCyrillic, id = 1002)
        self.Bind(wx.EVT_TOOL, self.toANSI, id = 1003)
        self.Bind(wx.EVT_TOOL, self.toUTF, id = 1004)
        self.Bind(wx.EVT_TOOL, self.onTranscribe, id = 1005)
        self.Bind(wx.EVT_TOOL, self.onRepSpecial, id = 1006)
        self.Bind(wx.EVT_TOOL, self.onCleanup, id = 1007)
        self.Bind(wx.EVT_TOOL, self.OnUndo, id=101)
        self.Bind(wx.EVT_TOOL, self.OnRedo, id=102)
        self.Bind(wx.EVT_TOOL, self.onQuit, id = 1008)
        self.Bind(wx.EVT_MENU_RANGE, self.onFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
        self.comboBox1.Bind(wx.EVT_COMBOBOX, self.onChoice, id=-1, id2=wx.ID_ANY)
        self.text_1.Bind(wx.EVT_TEXT, self.updateStatus, id=-1)
        self.text_1.Bind(wx.EVT_TEXT, self.enKode, id=-1)
        self.text_1.Bind(wx.EVT_TEXT, self.OnTextChanged, id=-1)
        self.text_1.Bind(wx.EVT_TEXT, self.OnTextGetSelection, id=-1)
        self.text_1.Bind(wx.EVT_TEXT, self.removeFiles, id=-1, id2=wx.ID_ANY)
        self.text_1.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        #self.text_1.Bind(wx.EVT_LEFT_DOWN, self.OnTextGetSelection, id=-1)
        #self.text_1.Bind(wx.EVT_LEFT_UP, self.OnTextGetSelection, id=-1)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateEditMenu)
        self.text_1.Bind(wx.EVT_MIDDLE_UP, self.OnContextMenu, id=-1)
        # Menu Bar
    def __set_menuBar(self): 
        self.frame_menubar = wx.MenuBar()
        self.file = wx.Menu()
        self.fopen = wx.MenuItem(self.file, wx.ID_OPEN, "&Open\tCtrl+O", "Otvori fajl", wx.ITEM_NORMAL)
        self.fopen.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.onOpen, id=self.fopen.GetId())
        self.file.Append(self.fopen)
        
        self.open_next = wx.MenuItem(self.file, wx.ID_ANY, u"Open next...\tAlt+E", u"Otvori sačuvani fajl", wx.ITEM_NORMAL)
        self.open_next.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_GO_DIR_UP, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.onOpenNext, id=self.open_next.GetId())
        self.file.Append(self.open_next)
        self.open_next.Enable(False)
        
        self.file.AppendSeparator()
        self.reload = wx.MenuItem(self.file, wx.ID_ANY, "&Reload file\tCtrl+R", "Ponovo učitaj fajl", wx.ITEM_NORMAL)
        self.reload.SetBitmap(wx.Bitmap(u"resources/icons/reload.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onReload, id=self.reload.GetId())
        self.file.Append(self.reload)
        self.reload.Enable(False)
        self.file.AppendSeparator()
        
        self.save = wx.MenuItem(self.file, wx.ID_SAVE, u"Save"+ u"\t" + u"Ctrl+S", u"Sačuvaj fajl", wx.ITEM_NORMAL)
        self.save.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.onSave, id=self.save.GetId())
        self.file.Append(self.save)
        self.save.Enable(False)
        
        self.save_as = wx.MenuItem(self.file, wx.ID_SAVEAS, u"Save as..."+ u"\t" + u"Ctrl+Shift+S", u"Sačuvaj fajl kao...", wx.ITEM_NORMAL)
        self.save_as.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.onSaveAs, id=self.save_as.GetId())
        self.file.Append(self.save_as)
        self.save_as.Enable(False)

        self.export_zip = wx.MenuItem(self.file, wx.ID_ANY, "&Export as ZIP\tCtrl+E", "Izvezi u zip formatu", wx.ITEM_NORMAL)
        self.export_zip.SetBitmap(wx.Bitmap("resources\\icons\\zip_file.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.exportZIP, id=self.export_zip.GetId())
        self.file.Append(self.export_zip)
        self.export_zip.Enable(False)
        
        self.file.AppendSeparator()

        self.close = wx.MenuItem(self.file, wx.ID_CLOSE, u"Close"+ u"\t" + u"Ctrl+W", u"Zatvori fajl", wx.ITEM_NORMAL)
        self.close.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.onCloseFile, id=self.close.GetId())
        self.file.Append(self.close)
        self.close.Enable(False)

        self.file.AppendSeparator()

        #self.recent.SetBitmap(wx.Bitmap(u"16x16/mimetypes/text-x-generic.png", wx.BITMAP_TYPE_ANY))
        # Submenu
        self.file_sub = wx.Menu()
        self.file_sub.Append(-1, "Recent files", "")
        self.file.Append(-1, "Recent", self.file_sub, "")
        
        self.file.AppendSeparator()
        # Submenu end        

        # self.file.AppendSeparator()
        
        self.quit_program = wx.MenuItem(self.file, wx.ID_ANY, u"Quit"+ u"\t" + u"Ctrl+Q", u"Quit program", wx.ITEM_NORMAL)
        self.quit_program.SetBitmap(wx.Bitmap(u"resources/icons/application-exit.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onQuit, id=self.quit_program.GetId())
        self.file.Append(self.quit_program)
        self.frame_menubar.Append(self.file, u"File")
        
        # Edit menu -----------------------------------------------------------------------------------------------------------------------
        self.edit = wx.Menu()
        self.undo = wx.MenuItem(self.edit, wx.ID_UNDO, "&Undo\tCtrl+Z", "Undo text", wx.ITEM_NORMAL)
        self.undo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.OnUndo, id=self.undo.GetId())
        self.edit.Append(self.undo)
        self.undo.Enable(False)
        
        self.redo = wx.MenuItem(self.edit, wx.ID_REDO, "&Redo\tCtrl+Shift+Z", "Redo text", wx.ITEM_NORMAL)
        self.redo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.OnRedo, id=self.redo.GetId())
        self.edit.Append(self.redo)
        self.redo.Enable(False)
        self.edit.AppendSeparator()
        
        self.cut = wx.MenuItem(self.edit, wx.ID_CUT, "&Cut\tCtrl+X", "Cut text", wx.ITEM_NORMAL)
        self.cut.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.OnCut, id=self.cut.GetId())
        self.edit.Append(self.cut)
        self.cut.Enable(False)
        
        self.copy = wx.MenuItem(self.edit, wx.ID_COPY, "&Copy\tCtrl+C", "Copy text", wx.ITEM_NORMAL)
        self.copy.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.OnCopy, id=self.copy.GetId())
        self.edit.Append(self.copy)
        self.copy.Enable(False)
        
        self.paste = wx.MenuItem(self.edit, wx.ID_PASTE, "&Paste\tCtrl+V", "Paste text", wx.ITEM_NORMAL)
        self.paste.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.OnPaste, id=self.paste.GetId())
        self.edit.Append(self.paste)
        self.paste.Enable(False)        
        
        self.edit.AppendSeparator()
        self.clear = wx.MenuItem(self.edit, wx.ID_CLEAR, "Clear", "Clear text", wx.ITEM_NORMAL)
        self.clear.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.OnClear, id=self.clear.GetId())
        self.edit.Append(self.clear)
        self.clear.Enable(False)        
        
        self.frame_menubar.Append(self.edit, "Edit")        
        # Actions   -----------------------------------------------------------------------------------------------------------------------
        self.action = wx.Menu()
        self.to_cyrillic = wx.MenuItem(self.action, wx.ID_ANY, u"ToCyrillic"+ u"\t" + u"Ctr+Y", u"Konvertuje u cirilicu", wx.ITEM_NORMAL)
        self.to_cyrillic.SetBitmap(wx.Bitmap(u"resources/icons/cyr-ltr.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.toCyrillic, id=self.to_cyrillic.GetId())
        self.action.Append(self.to_cyrillic)
        self.to_cyrillic.Enable(False)

        self.to_ansi = wx.MenuItem(self.action, wx.ID_ANY, u"ToANSI"+ u"\t" + u"Alt+S", u"Konvertuje u ANSI", wx.ITEM_NORMAL)
        self.to_ansi.SetBitmap(wx.Bitmap(u"resources/icons/go-next.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.toANSI, id=self.to_ansi.GetId())
        self.action.Append(self.to_ansi)
        self.to_ansi.Enable(False)

        self.to_utf8 = wx.MenuItem(self.action, wx.ID_ANY, u"ToUTF"+ u"\t" + u"Alt+D", u"Konvertuje u UTF", wx.ITEM_NORMAL)
        self.to_utf8.SetBitmap(wx.Bitmap(u"resources/icons/go-next.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.toUTF, id=self.to_utf8.GetId())
        self.action.Append(self.to_utf8)
        self.to_utf8.Enable(False)

        self.action.AppendSeparator()

        self.transcrib = wx.MenuItem(self.action, wx.ID_ANY, u"Transcribe"+ u"\t" + u"Alt+N", u"Transcribe", wx.ITEM_NORMAL)
        self.transcrib.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_MENU))
        self.Bind(wx.EVT_MENU, self.onTranscribe, id=self.transcrib.GetId())
        self.action.Append(self.transcrib)
        self.transcrib.Enable(False)

        self.specials = wx.MenuItem(self.action, wx.ID_ANY, u"&SpecReplace\tAlt+C", u"ReplaceSpecial definicije", wx.ITEM_NORMAL)
        self.specials.SetBitmap(wx.Bitmap(u"resources/icons/go-next.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onRepSpecial, id=self.specials.GetId())
        self.action.Append(self.specials)
        self.specials.Enable(False)
       
        self.cleaner = wx.MenuItem(self.action, wx.ID_ANY, u"Cleanup"+ u"\t" + u"Alt+K", u"Clean subtitle file", wx.ITEM_NORMAL)
        self.cleaner.SetBitmap(wx.Bitmap(u"resources/icons/edit-clear-all.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onCleanup, id=self.cleaner.GetId())
        self.action.Append(self.cleaner)
        self.cleaner.Enable(False)

        self.action.AppendSeparator()

        self.cyr_to_ansi = wx.MenuItem(self.action, wx.ID_ANY, u"Cyr to latin ansi"+ u"\t" + u"Ctrl+U", u"Preslovljavanje cirilice u latinicu ansi", wx.ITEM_NORMAL)
        self.cyr_to_ansi.SetBitmap(wx.Bitmap(u"resources/icons/go-next.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onCyrToANSI, id=self.cyr_to_ansi.GetId())
        self.action.Append(self.cyr_to_ansi)
        self.cyr_to_ansi.Enable(False)

        self.cyr_to_utf = wx.MenuItem(self.action, wx.ID_ANY, u"Cyr to latin utf8"+ u"\t" + u"Ctrl+L", u"Preslovljavanje cirilice u latinicu utf8", wx.ITEM_NORMAL)
        self.cyr_to_utf.SetBitmap(wx.Bitmap(u"resources/icons/go-next.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onCyrToUTF, id=self.cyr_to_utf.GetId())
        self.action.Append(self.cyr_to_utf)
        self.cyr_to_utf.Enable(False)

        self.action.AppendSeparator()
        
        self.fixer = wx.MenuItem(self.action, wx.ID_ANY, u"FixSubtitle"+ u"\t" + u"Alt+F", u"Fix subtitle file", wx.ITEM_NORMAL)
        self.fixer.SetBitmap(wx.Bitmap(u"resources/icons/go-next.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onFixSubs, id=self.fixer.GetId())
        self.action.Append(self.fixer)
        self.fixer.Enable(False)

        self.action.AppendSeparator()

        self.merger = wx.MenuItem(self.action, wx.ID_ANY, u"Merger"+ u"\t" + u"Ctrl+M", u"Merge lines", wx.ITEM_NORMAL)
        self.merger.SetBitmap(wx.Bitmap(u"resources/icons/merge.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onMergeLines, id=self.merger.GetId())
        self.action.Append(self.merger)
        self.merger.Enable(False)

        self.frame_menubar.Append(self.action, u"Actions")
        
        # Preferences menu ----------------------------------------------------------------------------------------------------------------
        self.preferences = wx.Menu()
        self.bom_utf8 = wx.MenuItem(self.preferences, 1011, u"bom_utf-8", u"Default za unikode", wx.ITEM_CHECK)
        self.bom_utf8.SetBitmap(wx.NullBitmap)
        self.preferences.Append(self.bom_utf8)

        self.txt_utf8 = wx.MenuItem(self.preferences, 1012, u"txt_utf-8", u"Default fajl format unikode", wx.ITEM_CHECK)
        self.txt_utf8.SetBitmap(wx.NullBitmap)
        self.preferences.Append(self.txt_utf8)

        self.preferences.AppendSeparator()

        self.fonts = wx.MenuItem(self.preferences, wx.ID_ANY, u"Font settings"+ u"\t" + u"Ctrl+F", u"Font settings", wx.ITEM_NORMAL)
        self.fonts.SetBitmap(wx.Bitmap(u"resources/icons/preferences-font.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onSelectFont, id=self.fonts.GetId())
        self.preferences.Append(self.fonts)

        self.preferences.AppendSeparator()

        self.fixer_settings = wx.MenuItem(self.preferences, wx.ID_ANY, u"FixerSettings", wx.EmptyString, wx.ITEM_NORMAL)
        self.fixer_settings.SetBitmap(wx.Bitmap(u"resources/icons/dialog-settings.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onFixerSettings, id=self.fixer_settings.GetId())
        self.preferences.Append(self.fixer_settings)

        self.preferences.AppendSeparator()

        self.merger_pref = wx.MenuItem(self.preferences, wx.ID_ANY, u"MergerSettings", wx.EmptyString, wx.ITEM_NORMAL)
        self.merger_pref.SetBitmap(wx.Bitmap(u"resources/icons/merge-settings.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onMergerSettings, id=self.merger_pref.GetId())
        self.preferences.Append(self.merger_pref)

        self.frame_menubar.Append(self.preferences, u"Preferences")

        self.help = wx.Menu()
        self.about = wx.MenuItem(self.help, wx.ID_ANY, u"About"+ u"\t" + u"Ctrl+I", u"O programu", wx.ITEM_NORMAL)
        self.about.SetBitmap(wx.Bitmap(u"resources/icons/help-about.png", wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_MENU, self.onAbout, id = self.about.GetId())
        self.help.Append(self.about)

        self.frame_menubar.Append(self.help, u"Help")

        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end
        
    # Tool Bar
    def __set_ToolBar(self):
        self.toolBar1 = self.CreateToolBar(wx.TB_HORIZONTAL, wx.ID_ANY)
        self.toolBar1.SetToolBitmapSize(wx.Size(24,24))
        self.fopen = self.toolBar1.AddTool(1001, u"Open", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR), wx.NullBitmap, wx.ITEM_NORMAL, u"Open File", u"Otvori fajl", None)
        self.fsave = self.toolBar1.AddTool(1010, u"Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR), wx.NullBitmap, wx.ITEM_NORMAL, u"Save file", u"Sačuvaj promene", None)
        self.undo_t = self.toolBar1.AddTool(101, "Undo", wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR), wx.NullBitmap, wx.ITEM_NORMAL, "Undo", "Undo change", None)
        self.redo_t = self.toolBar1.AddTool(102, "Redo", wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR), wx.NullBitmap, wx.ITEM_NORMAL, "Redo", "Redo change", None)
        self.cyrillic = self.toolBar1.AddTool(1002, u"Cirilica", wx.Bitmap(u"resources/icons/cyrillic.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"To Cyrillic", u"Konvertuje u ćirilicu", None)
        self.ansi = self.toolBar1.AddTool(1003, u"ANSI", wx.Bitmap(u"resources/icons/ANSI.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"To ANSI", u"Konvertuje u ANSI format", None)
        self.unicode = self.toolBar1.AddTool(1004, u"UTF", wx.Bitmap(u"resources/icons/UTF8.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"To UTF", u"Konvertuje u UTF unikode", None)
        self.transkrib = self.toolBar1.AddTool(1005, u"Transcribe", wx.Bitmap(u"resources/icons/cyr-ltr.24.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"Transcribe", u"Transkripcija", None)
        self.specijal = self.toolBar1.AddTool(1006, u"Specijal", wx.Bitmap(u"resources/icons/edit-find-replace.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"Replace Special", u"Spec-Replace definicije", None)
        self.cleanup = self.toolBar1.AddTool(1007, u"Cleanup", wx.Bitmap(u"resources/icons/editclear.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"Cleanup", u"Ćišćenje HI anotacija i praznih linija", None)
        self.quit_prog = self.toolBar1.AddTool(1008, u"Quit", wx.Bitmap(u"resources/icons/application-exit.24.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"Exit program", u"Zatvori program", None)

        self.toolBar1.AddSeparator()
        self.toolBar1.AddSeparator()
        self.toolBar1.AddSeparator()
        
        # Default za comboBox1
        with open('resources\\var\\obsE.pkl', 'rb') as f:
            kodek = pickle.load(f)
            listChoices2 = [' auto', ' windows-1250', ' windows-1251', ' windows-1252', ' utf-8']
            if kodek in listChoices2:
                kdef = listChoices2.index(kodek)
            else:
                kdef = 0        
        
        comboBox1Choices = [u" auto", u" windows-1250", u" windows-1251", u" windows-1252", u" utf-8", u" utf-16", " utf-16le", u" utf-16be", 
            u" utf-32", u" iso-8859-1", u" iso-8859-2", u" iso-8859-5", u" latin", u" latin2" ]        
        self.comboBox1 = wx.ComboBox(self.toolBar1, wx.ID_ANY, u"auto", wx.DefaultPosition, wx.DefaultSize, comboBox1Choices, wx.CB_DROPDOWN|wx.CB_READONLY)
        self.comboBox1.SetToolTip("Ulazno kodiranje fajla\nako je poznato\nili nije automatski pronađeno\n")
        self.comboBox1.SetSelection(kdef)
        self.toolBar1.AddControl(self.comboBox1)
        self.toolBar1.Realize()
        self.toolBar1.EnableTool(1010, False)
        self.toolBar1.EnableTool(1002, False)
        self.toolBar1.EnableTool(1003, False)
        self.toolBar1.EnableTool(1004, False)
        self.toolBar1.EnableTool(1005, False)
        self.toolBar1.EnableTool(1006, False)
        self.toolBar1.EnableTool(1007, False)
        self.toolBar1.EnableTool(101, False)
        self.toolBar1.EnableTool(102, False)
        # Tool Bar end
        
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle(f"SubtitleConverter {VERSION}")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("resources\\icons\\subConvert.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        self.SetFocus()
        
        # self.text_1.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        with shelve.open('resources\\var\\dialog_settings.db', flag='writeback') as s:
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
        
        self.text_1.SetToolTip(" Drag and Drop file here\n [zip, srt, txt] \n  ")
        self.text_1.SetFocus()
        self.frame_statusbar.SetStatusWidths([-1])
        
        with open('resources\\var\\bcf.pkl', 'rb') as bf:
            item = pickle.load(bf)
        if item == 'Checked':
            self.preferences.Check(1011, check=True)
        if os.path.exists('resources\\var\\tcf.pkl'):
            with open('resources\\var\\tcf.pkl', 'rb') as tf:
                item_txt = pickle.load(tf)
            if item_txt == 'txt':
                self.preferences.Check(1012, check=True)        
        
        # statusbar fields
        frame_statusbar_fields = ["frame_statusbar"]
        for i in range(len(frame_statusbar_fields)):
            self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.text_1, 1, wx.ALL | wx.EXPAND, 3)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()
        # end wxGlade
    
    def updateUI(self):
        self.curClr = wx.BLACK
        with shelve.open('resources\\var\\dialog_settings.db', flag='writeback') as s:
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
    
    def updateStatus(self, event):
        if os.path.exists('resources\\var\\path0.pkl'):
            with open('resources\\var\\path0.pkl', 'rb') as pf:
                path = pickle.load(pf)
                if type(path) is list:
                    self.SetStatusText('Multiple files ready for processing')
                else:
                    self.SetStatusText(os.path.basename(path))
        #p = FileDrop(self.text_1)
        #e = p.file_name
        #print(e)
        event.Skip()    
    
    def enKode(self, event):
        with shelve.open('resources\\var\\dialog_settings.db', flag='writeback') as s:
            ec = s['key3']; enk = ec['kode']; tpath = ec['tmPath']  # ; rlPath = ec['realPath']
        #with open('resources\\var\\enc0.pkl', 'rb') as e:
            #enk = pickle.load(e)
            
        #with open('resources\\var\\path0.pkl', 'rb') as p:
            #tpath = pickle.load(p)
        def load():
            with open('resources\\var\\obs1.pkl', 'rb') as f:
                return pickle.load(f)
        
        self.enableTool()
        
        # self.resetTool()
        
        #with open('resources\\var\path0.pkl', 'wb') as f:    # path je u tmp/ folderu
            #pickle.dump(tpath, f)
        if os.path.isfile('resources\\var\\rpath0.pkl'):
            with open('resources\\var\\rpath0.pkl', 'rb') as f:
                rlPath = pickle.load(f)
            self.real_dir = os.path.dirname(rlPath)
            # print('ON enKode rdir: ', self.real_dir)
            self.enchistory[tpath] = enk
            self.real_path= [rlPath]
        # print('OnEnKode enchist, rpath: ', self.enchistory, rlPath)
        event.Skip()
        
    def multipleTools(self):
        self.disableTool()
        self.toolBar1.EnableTool(1002, True)   # toCyrillic
        self.toolBar1.EnableTool(1003, True)   # toANSI
        self.toolBar1.EnableTool(1004, True)   # toUTF
        
        self.to_ansi.Enable(True)
        self.to_cyrillic.Enable(True)
        self.to_utf8.Enable(True)
        self.cyr_to_ansi.Enable(True)
        self.cyr_to_utf.Enable(True)
        self.export_zip.Enable(False)
       
    def OnContextMenu(self, event):
        menu_c = wx.Menu()
        menu_c.Append(1001, "Open")
        menu_c.Append(self.cut.GetId(), "Cut")
        self.PopupMenu(menu_c)
        menu_c.Destroy()
        event.Skip()
    
    def enableTool(self):
        self.toolBar1.EnableTool(wx.ID_CLOSE, True)
        self.toolBar1.EnableTool(1002, True)   # toCyrillic
        self.toolBar1.EnableTool(1003, True)   # toANSI
        self.toolBar1.EnableTool(1004, True)   # toUTF
        self.toolBar1.EnableTool(1005, True)   # Transcribe
        self.toolBar1.EnableTool(1006, True)   # Special
        self.toolBar1.EnableTool(1007, True)   # Cleanup
        
        self.merger.Enable(True)
        self.fixer.Enable(True)
        self.to_cyrillic.Enable(True)
        self.to_ansi.Enable(True)
        self.to_utf8.Enable(True)
        self.cleaner.Enable(True)
        self.specials.Enable(True)
        self.transcrib.Enable(True)
        self.cyr_to_ansi.Enable(True)
        self.cyr_to_utf.Enable(True)
        self.export_zip.Enable(True)
    
    def disableTool(self):
        self.toolBar1.EnableTool(wx.ID_CLOSE, False)
        self.toolBar1.EnableTool(1002, False)   # toCyrillic
        self.toolBar1.EnableTool(1003, False)   # toANSI
        self.toolBar1.EnableTool(1004, False)   # toUTF
        self.toolBar1.EnableTool(1005, False)   # Transcribe
        self.toolBar1.EnableTool(1006, False)   # Special
        self.toolBar1.EnableTool(1007, False)   # Cleanup
        
        self.merger.Enable(False)
        self.fixer.Enable(False)
        self.to_cyrillic.Enable(False)
        self.to_ansi.Enable(False)
        self.to_utf8.Enable(False)
        self.cleaner.Enable(False)
        self.specials.Enable(False)
        self.transcrib.Enable(False)
        self.cyr_to_ansi.Enable(False)
        self.cyr_to_utf.Enable(False)
        self.open_next.Enable(False)
        self.reload.Enable(False)
        self.export_zip.Enable(False)
    
    def handleFile(self, filepaths):
        def file_go(self, infile, realF):
            fop = FileOpened(infile)
            enc = fop.findCode()
            fproc = FileProcessed(enc, infile)
            fproc.normalizeText()
            fproc.regularFile(realF)
            text = fproc.getContent()
            nlist = fproc.checkErrors()
            self.text_1.SetValue(text)
            for i in nlist:
                a = i[0]
                b = i[1]                        
                self.text_1.SetStyle(a, b, wx.TextAttr("YELLOW","BLUE"))
                self.text_1.SetInsertionPoint(b)            
            logger.debug(f'File opened: {os.path.basename(infile)}')
            self.filehistory.AddFileToHistory(infile)
            self.enchistory[infile] = enc
            self.reloadText = text
            # print('RELOAD: ', self.reloadText)
            
        def multiple(self, inpath, tmppath):
            path = []
            n_path = []
            for i, x in zip(inpath, tmppath):
                path.append(i)
                n_path.append(x)
                if os.path.isfile(i):
                    shutil.copy(i, x)
            with open('resources\\var\\rpath0.pkl', 'wb') as f:
                pickle.dump(path[-1], f, pickle.HIGHEST_PROTOCOL)            
            return path, n_path
        inpaths = [x for x in filepaths]
        tmp_path = [os.path.join(self.location, os.path.basename(item)) for item in inpaths]  # sef.locatin is tmp/
        
        for path in tmp_path:
            self.tmpPath.append(path)
        if len(inpaths) == 1:  # Jedan ulazni fajl, ZIP ili TXT,SRT
            path = inpaths[0]
            tpath = tmp_path[0]
            if not zipfile.is_zipfile(path):
                shutil.copy(path, tpath)
                file_go(self, tpath, path)    # U tmp/ folderu
            elif zipfile.is_zipfile(path):  # == True:
                with open('resources\\var\\rpath0.pkl', 'wb') as f:
                    pickle.dump(path, f, pickle.HIGHEST_PROTOCOL)
                fop = FileOpened(path)
                try:
                    outfile, rfile = fop.isCompressed()  # U tmp/ folderu
                except:
                    logger.debug(f'{path}: No files selected.')
                else:
                    if len(outfile) == 1:   # Jedan fajl u ZIP-u
                        file_go(self, outfile[0], rfile)
                    elif len(outfile) > 1:  # Više fajlova u ZIP-u
                        self.text_1.SetValue('Files List:\n')
                        for i in range(len(outfile)):
                            text = os.path.basename(outfile[i])
                            fop = FileOpened(path=outfile[i])
                            enc = fop.findCode()
                            fproc = FileProcessed(enc, outfile[i])
                            fproc.normalizeText()
                            self.enchistory[outfile[i]] = enc
                            self.text_1.AppendText('\n')
                            self.text_1.AppendText(text)
                            self.multiFile[outfile[i]] = enc
                        with open('resources\\var\\droped0.pkl', 'wb') as d:
                            pickle.dump(self.multiFile, d)
                        logger.debug('FileHandler: Ready for multiple files.')
                        self.SetStatusText('Files ready for processing')
                        
        elif len(inpaths) > 1:      # Više selektovanih ulaznih fajlova
            paths_in, paths_out = multiple(self, inpaths, tmp_path)
            # if not any(zipfile.is_zipfile(x) for x in paths_in):
            self.text_1.SetValue('Files List:\n')
            self.multipleTools()
            for i in range(len(paths_in)):
                fpath = paths_out[i]
                fop = FileOpened(fpath)
                # print(fpath)
                if zipfile.is_zipfile(fpath):
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
                                enc = fop.findCode()
                                fproc = FileProcessed(enc, fpath)
                                fproc.normalizeText()
                                self.enchistory[fpath] = enc
                                self.text_1.AppendText('\n')
                                self.text_1.AppendText(os.path.basename(fpath))
                                self.multiFile[fpath] = enc
                else:   # Nije ZIP
                    text = os.path.basename(fpath)
                    fop = FileOpened(fpath)
                    enc = fop.findCode()
                    fproc = FileProcessed(enc, fpath)
                    fproc.normalizeText()
                    self.text_1.AppendText("\n")
                    self.text_1.AppendText(text)
                    self.enchistory[fpath] = enc
                    self.multiFile[fpath] = enc
                    self.reloadText = text
                    
            with open('resources\\var\\droped0.pkl', 'wb') as d:
                pickle.dump(self.multiFile, d)
            self.multipleTools()
            logger.debug('FileHandler: Ready for multiple files')
            self.SetStatusText('Files ready for processing')
    
    def onOpen(self, event):  # wxGlade: MyFrame.<event_handler>
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and not self.previous_action:
            dl1 = wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO, self)
            if dl1 == wx.NO:
                return
        dlgOpen = wx.FileDialog(self, "Otvori novi fajl", style=wx.FD_OPEN|wx.FD_MULTIPLE, wildcard=self.wildcard) # creates the Open File dialog
        if dlgOpen.ShowModal() == wx.ID_OK:
            if len(self.multiFile) >= 1:
                self.multiFile.clear()
                self.previous_action.clear()
                self.enchistory.clear()
                if os.path.isfile('resources\\var\\droped0.pkl'):
                    os.remove('resources\\var\\droped0.pkl')
            self.filepath = dlgOpen.GetPaths() # Get the file location
            if len(self.filepath) == 1:
                real_path = self.filepath[-1]
                self.real_path = [real_path]
                with open('resources\\var\\rpath0.pkl', 'wb') as f:
                    pickle.dump(real_path, f, pickle.HIGHEST_PROTOCOL)                
                # real_dir = self.real_dir
            else:
                for fpath in self.filepath:
                    self.real_path.append(fpath)
                    
            # self.previous_action='Open'
            self.handleFile(self.filepath)
            self.enableTool()
            self.open_next.Enable(False)
            # self.resetTool()
            dlgOpen.Destroy()            
            
        # self.toolBar1.EnableTool(1003, True)
        event.Skip()

    def onOpenNext(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'onOpenNext' not implemented!")
        event.Skip()
    
    def onReload(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled():
            dl1 = wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO, self)
            if dl1 == wx.NO:
                return        
        with open('resources\\var\\path0.pkl', 'rb') as p:
            path = pickle.load(p)
        with open('resources\\var\\enc0.pkl', 'rb') as p:
            enc = pickle.load(p)
        
        if os.path.isfile('resources\\var\\r_text0.pkl'):
            with open('resources\\var\\r_text0.pkl', 'rb') as f:
                text=pickle.load(f)
            os.remove('resources\\var\\r_text0.pkl')
            self.reloadText = text
            self.text_1.SetValue(text)
            writeTempStr(path, text, enc)
            self.reloaded += 1
        else:
            text = self.reloadText
            self.text_1.SetValue(text)
            writeTempStr(path, text, enc)
            self.reloaded += 1
        logger.debug('Reloaded {}, encoding: {}'.format(os.path.basename(path), enc))
        
        event.Skip()
        
    def fileErrors(self, path, new_enc):
        print('REAL:', self.real_dir)
        fproc = FileProcessed(new_enc, path)
        text = fproc.getContent()
        nlist = w_position(r'\?', text)     # Lociramo novonastale znakove ako ih ima
        epath = os.path.basename(path)
        outf = os.path.join(self.real_dir, os.path.splitext(epath)[0] + '_error.log')
        print(outf)
        showMeError(path, outf, new_enc)
        text = text.replace('¬', '?')       # Ponovo vracamo znakove pitanja na svoja mesta
        fproc.writeToFile(text)
        fproc.unix2DOS()
        self.text_1.SetValue(text)
        for i in nlist:
            if not len(nlist) > 500:
                a = i[0]
                b = i[1]                        
                self.text_1.SetStyle(a, b, wx.TextAttr("YELLOW","GREEN"))
                self.text_1.SetInsertionPoint(b)
        return text
        
    def toANSI(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0:
            dl = self.ShowDialog()
            if dl == False:
                return        
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)
            
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toANSI_multiple()
        else:        
            if os.path.isfile('resources\\var\\path0.pkl'):
                with open('resources\\var\\path0.pkl', 'rb') as p:
                    path = pickle.load(p)          # path je u tmp/ folderu
                with open('resources\\var\\enc0.pkl', 'rb') as e:
                    entered_enc = pickle.load(e)
                self.enchistory[path] = entered_enc            
                self.orig_path = path + '.orig'
                shutil.copy(path, self.orig_path)            
            else:
                text = self.text_1.GetValue()
                path = 'tmp\\Untitled.srt'
                if not os.path.isfile(path):
                    open(path, 'a').close()
                fp = FileProcessed('windows-1250', path)
                fp.writeToFile(text)
                entered_enc = 'windows-1250'
                self.newEnc = entered_enc
            
            entered_enc = self.encAction(path)
                
            self.newEnc = 'windows-1250'
            if entered_enc == self.newEnc:
                logger.debug(f"Nothing to do, encoding is: {entered_enc}")
                return
            self.pre_suffix = 'lat'
            
            def ansiAction(inpath):
                fproc = FileProcessed(entered_enc, inpath)
                if not entered_enc == 'windows-1251':
                    logger.debug(f'toANSI: {inpath}, {entered_enc}')
                fproc.normalizeText()
                text = fproc.getContent()
                text = fproc.rplStr(text)
                text = fproc.writeToFile(text)
                if text:
                    text = text.replace('?', '¬')
                new_fproc = FileProcessed(self.newEnc, inpath)
                text = new_fproc.writeToFile(text)
                text = new_fproc.fixI(text)
                text = new_fproc.writeToFile(text)
                
                text = self.fileErrors(inpath, self.newEnc) 
                
                self.tmpPath.append(inpath)
                if text:
                    msginfo = wx.MessageDialog(self, f'Tekst je konvertovan u enkoding: {self.newEnc}.', 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                    msginfo.ShowModal()                
                return text
            def postAnsi():
                self.SetStatusText(os.path.basename(path))
                self.MenuBar.Enable(wx.ID_SAVE, True)
                self.MenuBar.Enable(wx.ID_SAVEAS, True)
                self.MenuBar.Enable(wx.ID_CLOSE, True)
                self.toolBar1.EnableTool(1010, True)  # Save
                self.previous_action['toANSI'] = self.newEnc
                self.reloaded = 0
            
            def dialog1(text_1):
                ErrorDlg = wx.MessageDialog(self, text_1, "SubConverter", style= wx.OK | wx.CANCEL|wx.CANCEL_DEFAULT | wx.ICON_INFORMATION)
                if ErrorDlg.ShowModal() == wx.ID_OK:
                    return True
            fproc_a = FileProcessed(entered_enc, self.orig_path)
            zbir_slova, procent = fproc_a.checkChars()
            #----------------------------------------------------------------------------------------------------------
            if zbir_slova == 0 and procent == 0:
                text = ansiAction(path)
                fproc = FileProcessed(self.newEnc, path)
                error_text = fproc.checkFile(self.orig_path, path, multi=False)
                if error_text:
                    ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                    ErrorDlg.ShowModal()
                    self.Error_Text = error_text            
                self.undoAction.append(text)
                self.enc = self.newEnc
                postAnsi()
            #----------------------------------------------------------------------------------------------------------
            elif procent > 0:
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                f_procent = 'Najmanje {} % teksta.\nIli najmanje [ {} ] znakova.'.format(procent, zbir_slova)
                ErrorText = "Greška:\n\nUlazni fajl sadrži ćiriliči alfabet.\n{}\n\nNastavljate?\n".format(f_procent)
                dlg = dialog1(ErrorText)
                if dlg == True:
                    if procent >= 50:
                        ErrorDlg = wx.MessageDialog(
                                self, "Too many errors!\n\nAre you sure you want to proceed?\n", "SubConverter", style=wx.CANCEL|wx.CANCEL_DEFAULT|wx.OK|wx.ICON_ERROR)
                        if ErrorDlg.ShowModal() == wx.ID_CANCEL:
                                        return
                    text = ansiAction(path)
                    fproc = FileProcessed(self.newEnc, path)
                    error_text = fproc.checkFile(self.orig_path, path, multi=False)
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                        self.Error_Text = error_text            
                    self.undoAction.append(text)
                    self.enc = self.newEnc
                    postAnsi()
            #----------------------------------------------------------------------------------------------------------
            elif zbir_slova > 0:
                f_zbir = 'Najmanje [ {} ] znakova.'.format(zbir_slova)
                ErrorText = "Greška:\n\nUlazni fajl sadrži ćiriliči alfabet.\n{}\n\nNastavljate?\n".format(f_zbir)
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                dlg = dialog1(ErrorText)
                if dlg == True:
                    text = ansiAction(path)
                    fproc = FileProcessed(self.newEnc, path)
                    error_text = fproc.checkFile(self.orig_path, path, multi=False)
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                        self.Error_Text = error_text            
                    self.undoAction.append(text)
                    self.enc = self.newEnc                        
                    postAnsi()  
        event.Skip()
        
    def toANSI_multiple(self):
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)
        self.newEnc = 'windows-1250'
        self.pre_suffix = 'lat'
                
        for key, value in self.multiFile.items():
            path=key
            entered_enc=value
            fproc = FileProcessed(entered_enc, path)
            if entered_enc == 'windows-1251':
                logger.debug(f"------------------------------------------------------\nOperation not permitted when encoding windows-1251! {os.path.basename(path)}")
                continue
            
            zbir_slova, procent = fproc.checkChars()
            def ansiAction(path):
                if not entered_enc == 'windows-1251':
                    logger.debug('ToANSI, next input encoding: {}'.format(entered_enc))                    
                text = fproc.getContent()
                text = fproc.rplStr(text)
                text = text.replace('?', '¬')
                writeTempStr(path, text, entered_enc)
                nam, b = fproc.newName(path, self.pre_suffix, self.real_dir, True)
                newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)                
                new_fproc = FileProcessed(self.newEnc, newF)
                text = fproc.getContent()
                text = new_fproc.writeToFile(text)
                self.tmpPath.append(newF)
                new_fproc.fixI(newF)
                return newF
            def postAnsi():
                self.SetStatusText('Processing multiple files.')
                self.previous_action['toANSI'] = self.newEnc
            def dialog1(text_1):
                ErrorDlg = wx.MessageDialog(self, text_1, "SubConverter", style= wx.OK | wx.CANCEL|wx.CANCEL_DEFAULT | wx.ICON_INFORMATION)
                if ErrorDlg.ShowModal() == wx.ID_OK:
                    return True
                    
            if zbir_slova == 0 and procent == 0:
                newF = ansiAction(path)
                error_text = fproc.checkFile(path, newF, multi=True)
                newfproc = FileProcessed(self.newEnc, newF)
                try:
                    text = newfproc.getContent()
                except Exception as e:
                    logger.debug("ToANSI, text error:", sys.exc_info()[0:2])                
                text = text.replace('¬', '?')
                writeTempStr(newF, text, self.newEnc)
                newfproc.unix2DOS()
                self.text_1.AppendText('\n')
                self.text_1.AppendText(os.path.basename(newF))                
                if error_text:
                    ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                    ErrorDlg.ShowModal()
                    outf = newF + '.error.log'
                    showMeError(newF, outfile=outf, kode=self.newEnc)                    
                postAnsi()
                text = fproc.getContent()
                text = text.replace('¬', '?')
                writeTempStr(path, text, entered_enc)
                fproc.unix2DOS()
                
            elif procent > 0:
                logger.debug(f'ToANSI: Cyrillic alfabet u tekstu: {entered_enc} cyrillic')
                self.SetStatusText(u'Greška u ulaznom fajlu.')
                f_procent = 'Najmanje {} % teksta.\nIli najmanje [ {} ] znakova.'.format(procent, zbir_slova)
                ErrorText = "Greška:\n\n{}\nsadrži ćiriliči alfabet.\n{}\n\nNastavljate?\n".format(os.path.basename(path), f_procent)
                dlg = dialog1(ErrorText)
                if dlg == True:
                    if procent >= 50:
                        ErrorDlg = wx.MessageDialog(
                                self, "Too many errors!\n\nAre you sure you want to proceed?\n", "SubConverter", style=wx.CANCEL|wx.CANCEL_DEFAULT|wx.OK|wx.ICON_ERROR)
                        if ErrorDlg.ShowModal() == wx.ID_CANCEL:
                            return
                    newF = ansiAction(path)
                    error_text = fproc.checkFile(path, newF, multi=True)
                    newfproc = FileProcessed(self.newEnc, newF)
                    try:
                        text = newfproc.getContent()
                    except Exception as e:
                        logger.debug("ToANSI, text error:", sys.exc_info()[0:2])                    
                    self.text_1.AppendText('\n')
                    self.text_1.AppendText(os.path.basename(newF))                    
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                        outf = newF + '.error.log'
                        showMeError(newF, outfile=outf, kode=self.newEnc)
                        text = newfproc.getContent()
                        text = text.replace('¬', '?')
                        writeTempStr(newF, text, self.newEnc)
                        newfproc.unix2DOS()
                    postAnsi()
                    text = fproc.getContent()
                    text = text.replace('¬', '?')
                    writeTempStr(path, text, entered_enc)
                    fproc.unix2DOS()
                    
            elif zbir_slova > 0:
                logger.debug(f'ToANSI: Cyrillic alfabet u tekstu: {entered_enc} cyrillic')
                f_zbir = 'Najmanje [ {} ] znakova.'.format(zbir_slova)
                ErrorText = "Greška:\n\n{}\nsadrži ćiriliči alfabet.\n{}\n\nNastavljate?\n".format(os.path.basename(path), f_zbir)
                dlg = dialog1(ErrorText)
                if dlg == True:
                    newF = ansiAction(path)
                    error_text = fproc.checkFile(path, newF, multi=True)
                    newfproc = FileProcessed(self.newEnc, newF)
                    try:
                        text = newfproc.getContent()
                    except Exception as e:
                        logger.debug("ToANSI, text error:", sys.exc_info()[0:2])                        
                    self.text_1.AppendText('\n')
                    self.text_1.AppendText(os.path.basename(newF))
                    if error_text:
                        ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                        ErrorDlg.ShowModal()
                        outf = newF + '.error.log'
                        showMeError(newF, outfile=outf, kode=self.newEnc)
                        text = newfproc.getContent()
                        text = text.replace('¬', '?')
                        writeTempStr(newF, text, self.newEnc)
                        newfproc.unix2DOS()
                    postAnsi()
                    text = fproc.getContent()
                    text = text.replace('¬', '?')
                    writeTempStr(path, text, entered_enc)
                    fproc.unix2DOS()
        self.SetStatusText('Multiple files done.')            
        self.multipleTools()
        
    def toCyrillic(self, event):
        if os.path.isfile('resources\\var\\rpath0.pkl'):
            with open('resources\\var\\rpath0.pkl', 'rb') as f:
                rlPath = pickle.load(f)
            self.real_dir = os.path.dirname(rlPath)
            self.real_path= [rlPath]        
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0:
            dl = self.ShowDialog()
            if dl == False:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)
            
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toCyrillic_multiple()
        else:        
            if os.path.isfile('resources\\var\\path0.pkl'):
                with open('resources\\var\\path0.pkl', 'rb') as p:
                    path = pickle.load(p)          # path je u tmp/ folderu
                with open('resources\\var\\enc0.pkl', 'rb') as e:
                    entered_enc = pickle.load(e)
                self.enchistory[path] = entered_enc
                self.orig_path = path + '.orig'
                shutil.copy(path, self.orig_path)                
            else:
                text = self.text_1.GetValue()
                path = 'tmp\\Untitled.srt'
                if not os.path.isfile(path):
                    open(path, 'a').close()
                fp = FileProcessed('utf-8', path)
                fp.writeToFile(text)
                entered_enc = 'utf-8'
                self.newEnc = entered_enc
            
            entered_enc = self.encAction(path)
                
            self.newEnc = 'windows-1251'
            
            if entered_enc == self.newEnc:
                logger.debug(f"Nothing to do, encoding is: {entered_enc}")
                return
            self.pre_suffix = 'cyr'
            new_enc = self.newEnc
            fproc = FileProcessed(entered_enc, path)
            text = fproc.getContent()
            if text:
                text = text.replace('?', '¬')
            writeTempStr(path, text, entered_enc)
            
            utfText, suffix = fproc.newName(path, 'cyr_utf8', self.real_dir, multi=False)
            if self.preferences.IsChecked(1011):  
                utf8_enc = 'utf-8-sig'
            else:
                utf8_enc = 'utf-8'        
            utf_path = os.path.join(self.real_dir, utfText+suffix)
            if os.path.exists(utf_path):
                nnm = fproc.nameCheck(os.path.basename(utf_path), self.real_dir, suffix)
                utf_path = '{0}_{1}{2}'.format(utf_path, nnm, suffix)        
            new_fproc = FileProcessed(utf8_enc, utf_path)
            text = fproc.getContent()
            text = new_fproc.writeToFile(text)
            text = new_fproc.fixI(text)  # Isto kao i kod rplStr text
            text = new_fproc.writeToFile(text)
            
            cyr_proc = Preslovljavanje(utf8_enc, utf_path)
            cyr_proc.preLatin()
            cyr_proc.preProc(reversed_action=False)
            cyr_proc.changeLetters(reversed_action=False)
            text = cyr_proc.getContent()
            text = cyr_proc.rplStr(text)    # Ovde ide tekst ne putanja
            cyr_proc.writeToFile(text)      # izlaz is rplStr mora da se pise u fajl
            cyr_proc.fineTune()
            cyr_proc.fontColor()
            
            cyr_path = path
            cyr_ansi = Preslovljavanje(self.newEnc, cyr_path)
            text = cyr_proc.getContent()
            text = cyr_ansi.writeToFile(text)
            
            text = self.fileErrors(cyr_path, self.newEnc)
            
            error_text = cyr_proc.checkFile(self.orig_path, cyr_path, multi=False)
            
            cyr_proc.writeToFile(text)
            cyr_proc.unix2DOS()
            cyr_ansi.writeToFile(text)
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            text = cyr_ansi.getContent()
            text = text.replace('¬', '?')
            cyr_ansi.writeToFile(text)
            cyr_ansi.unix2DOS()
            self.undoAction.append(text)
            self.enc = self.newEnc
            self.SetStatusText(os.path.basename(path))
            self.MenuBar.Enable(wx.ID_SAVE, True)
            self.MenuBar.Enable(wx.ID_SAVEAS, True)
            self.MenuBar.Enable(wx.ID_CLOSE, True)
            self.toolBar1.EnableTool(1010, True)  # Save
            self.toolBar1.EnableTool(1003, False)
            self.enchistory[path] = self.newEnc
            self.previous_action['toCYR'] = self.newEnc
            self.reloaded = 0
        event.Skip()
    
    def toCyrillic_multiple(self):
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)
        self.newEnc = 'windows-1251'
        self.pre_suffix = 'cyr'
        
        for key, value in self.multiFile.items():
            
            path=key
            entered_enc=value
            fproc = FileProcessed(entered_enc, path)
            
            text = fproc.getContent()
            if text:
                text = text.replace('?', '¬')
            utfText, suffix = fproc.newName(path, 'cyr_utf8', self.real_dir, multi=False)
            if self.preferences.IsChecked(1011):  
                utf8_enc = 'utf-8-sig'
            else:
                utf8_enc = 'utf-8'        
            utf_path = os.path.join(self.real_dir, utfText+suffix)
            if os.path.exists(utf_path):
                nnm = fproc.nameCheck(os.path.basename(utf_path), self.real_dir, suffix)
                utf_path = '{0}_{1}{2}'.format(utf_path, nnm, suffix)
            
            new_fproc = FileProcessed(utf8_enc, utf_path)
            text = new_fproc.writeToFile(text)
            text = new_fproc.fixI(text)  # Isto kao i kod rplStr text
            text = new_fproc.writeToFile(text)
            
            cyr_name, cyr_suffix = new_fproc.newName(path, self.pre_suffix, self.real_dir, multi=True)
            cyr_path = os.path.join(self.real_dir, cyr_name+cyr_suffix)
            if not os.path.isfile(cyr_path):
                open(cyr_path, 'a').close()
            cyr_proc = Preslovljavanje(utf8_enc, utf_path)
            cyr_proc.preLatin()
            cyr_proc.preProc(reversed_action=False)
            cyr_proc.changeLetters(reversed_action=False)
            text = cyr_proc.getContent()
            text = cyr_proc.rplStr(text)    # Ovde ide tekst ne putanja
            cyr_proc.writeToFile(text)      # izlaz is rplStr mora da se pise u fajl
            cyr_proc.fineTune()
            cyr_proc.fontColor()
            
            cyr_ansi = Preslovljavanje(self.newEnc, cyr_path)
            text = cyr_proc.getContent()
            text = cyr_ansi.writeToFile(text)
            
            error_text = cyr_proc.checkFile(utf_path, cyr_path, multi=True)
            #cyr_proc.unix2DOS()
            #cyr_ansi.unix2DOS()
            self.text_1.AppendText('\n')
            self.text_1.AppendText(os.path.basename(cyr_path))            
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
                outf = cyr_path + '.error.log'
                showMeError(cyr_path, outfile=outf, kode=self.newEnc)                
                text = cyr_ansi.getContent()
                text = text.replace('¬', '?')
                writeTempStr(cyr_path, text, self.newEnc)
                cyr_ansi.unix2DOS()
            self.enc = self.newEnc
            self.reloaded = 0
            text = cyr_proc.getContent()
            text = text.replace('¬', '?')
            writeTempStr(utf_path, text, utf8_enc)
            cyr_proc.unix2DOS()
            text = cyr_ansi.getContent()
            text = text.replace('¬', '?')
            writeTempStr(cyr_path, text, self.newEnc)
            self.SetStatusText('Processing multiple files')
            self.previous_action['toCYR_multiple'] = self.newEnc
            
        self.SetStatusText('Multiple files done.')
        self.multipleTools()
    
    def toUTF(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0 and self.reloaded == 0:
            dl = self.ShowDialog()
            if dl == False:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.toUTF_multiple()
        else:
            if os.path.isfile('resources\\var\\path0.pkl'):
                with open('resources\\var\\path0.pkl', 'rb') as p:
                    path = pickle.load(p)          # path je u tmp/ folderu
                with open('resources\\var\\enc0.pkl', 'rb') as e:
                    entered_enc = pickle.load(e)
                self.enchistory[path] = entered_enc
            else:
                text = self.text_1.GetValue()
                path = 'tmp\\Untitled.srt'
                if not os.path.isfile(path):
                    open(path, 'a').close()
                writeTempStr(path, text, 'utf-8')
                
            self.pre_suffix = 'utf8'
            
            entered_enc = self.encAction(path)
            
            if self.preferences.IsChecked(1011):
                self.newEnc = 'utf-8-sig'
            else:
                self.newEnc = 'utf-8'
                
            fproc = FileProcessed(entered_enc, path)
            text = fproc.getContent()
            utfproc = FileProcessed(self.newEnc, path)
            text = utfproc.writeToFile(text)
            text = utfproc.fixI(text)
            writeTempStr(path, text, self.newEnc)
            utfproc.unix2DOS()
            text = utfproc.getContent()
            self.text_1.SetValue(text)
            self.undoAction.append(text)
            self.enc = self.newEnc
            self.SetStatusText(os.path.basename(path))
            self.MenuBar.Enable(wx.ID_SAVE, True)
            self.MenuBar.Enable(wx.ID_SAVEAS, True)
            self.MenuBar.Enable(wx.ID_CLOSE, True)
            self.toolBar1.EnableTool(1010, True)  # Save
            self.previous_action['toUTF'] = self.newEnc            
            self.reloaded = 0
        event.Skip()
    
    def toUTF_multiple(self):
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)
        self.pre_suffix = 'utf8'
        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'        
        
        for key, value in self.multiFile.items():
                    
            path=key
            entered_enc=value
            fproc = FileProcessed(entered_enc, path)
            
            text = fproc.getContent()
            if text:
                text = text.replace('?', '¬')
                writeTempStr(path, text, entered_enc)
            nam, b = fproc.newName(path, self.pre_suffix, self.real_dir, True)
            newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)
            
            newFproc = FileProcessed(self.newEnc, newF)
            text = newFproc.writeToFile(text)
            self.tmpPath.append(newF)  # VAZNO
            text = newFproc.fixI(text)
            writeTempStr(newF, text, self.newEnc)
            
            error_text = fproc.checkFile(path, newF, multi=True)
            self.text_1.AppendText('\n')
            self.text_1.AppendText(os.path.basename(newF))
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                outf = newF + '.error.log'
                showMeError(newF, outfile=outf, kode=self.newEnc)
                text = newFproc.getContent()
                text = text.replace('¬', '?')
                writeTempStr(newF, text, self.newEnc)
                newFproc.unix2DOS()
            self.SetStatusText('Processing multiple files.')
            text = fproc.getContent()
            text = text.replace('¬', '?')
            writeTempStr(path, text, entered_enc)
            fproc.unix2DOS()
            text = newFproc.getContent()
            text = text.replace('¬', '?')
            writeTempStr(newF, text, self.newEnc)
            newFproc.unix2DOS()
        self.multipleTools()
        self.reloaded = 0
        self.previous_action['toUTF_multiple'] = self.newEnc
        self.SetStatusText('Multiple files done.')
        
    def onTranscribe(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0 and self.reloaded == 0:
            dl = self.ShowDialog()
            if dl == False:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)        
        if len(self.multiFile) >= 1:
            return
    
        if os.path.isfile('resources\\var\\path0.pkl'):
            with open('resources\\var\\path0.pkl', 'rb') as p:
                path = pickle.load(p)          # path je u tmp/ folderu
            with open('resources\\var\\enc0.pkl', 'rb') as e:
                entered_enc = pickle.load(e)
            self.enchistory[path] = entered_enc
        else:
            text = self.text_1.GetValue()
            path = 'tmp\\Untitled.srt'
            if not os.path.isfile(path):
                open(path, 'a').close()
            writeTempStr(path, text, 'utf-8')
            
        self.pre_suffix = 'utf8'
        
        entered_enc = self.encAction(path)
        
        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'
            
        fproc = FileProcessed(entered_enc, path)
        text = fproc.getContent()
        utf_proc = FileProcessed(self.newEnc, path)
        text = utf_proc.writeToFile(text)
        text = utf_proc.fixI(text)
        writeTempStr(path, text, self.newEnc)
        newfproc = TextProcessing(self.newEnc, path)
        num = newfproc.zameniImena()
        if num > 28 or num < 28 and num > 2:
            msginfo = wx.MessageDialog(self, 'Zamenjenih objekata\nukupno [ {} ]'.format(num), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
            msginfo.ShowModal()
        text = newfproc.getContent()
        text = newfproc.rplStr(text)
        writeTempStr(path, text, self.newEnc)
        newfproc.unix2DOS()
        self.text_1.SetValue(text)
        self.undoAction.append(text)
        self.enc = self.newEnc
        self.SetStatusText(os.path.basename(path))
        self.MenuBar.Enable(wx.ID_SAVE, True)
        self.MenuBar.Enable(wx.ID_SAVEAS, True)
        self.MenuBar.Enable(wx.ID_CLOSE, True)
        self.reload.Enable(True)
        self.toolBar1.EnableTool(1010, True)  # Save        
        self.previous_action['Transcribe'] = self.newEnc
        self.reloaded = 0
        event.Skip()
        
    def onRepSpecial(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0 and self.reloaded == 0:
            dl = self.ShowDialog()
            if dl == False:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)        
        if len(self.multiFile) >= 1:
            return
    
        if os.path.isfile('resources\\var\\path0.pkl'):
            with open('resources\\var\\path0.pkl', 'rb') as p:
                path = pickle.load(p)          # path je u tmp/ folderu
            with open('resources\\var\\enc0.pkl', 'rb') as e:
                entered_enc = pickle.load(e)
            self.enchistory[path] = entered_enc
        else:
            text = self.text_1.GetValue()
            path = 'tmp\\Untitled.srt'
            if not os.path.isfile(path):
                open(path, 'a').close()
            writeTempStr(path, text, 'utf-8')
        
        entered_enc = self.encAction(path)
        self.newEnc = entered_enc    
        
        self.orig_path = path + '.orig'
        if not os.path.isfile(self.orig_path):
            shutil.copy(path, self.orig_path)
        
        self.pre_suffix = 'rpl'
        
        prethodna = self.previous_action   # Poslednji element i kada je lista prazna
        
        fproc = TextProcessing(entered_enc, path)
        text = fproc.getContent()
        text = text.replace('?', '¬')
        writeTempStr(path, text, entered_enc)
        num = fproc.doReplace()
        text = fproc.getContent()
        text = self.fileErrors(path, entered_enc)
        error_text = fproc.checkFile(self.orig_path, path, multi=False)
        msginfo = wx.MessageDialog(self, 'Zamenjenih objekata\nukupno [ {} ]'.format(num), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
        msginfo.ShowModal()            
        if error_text:
            ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
            ErrorDlg.ShowModal()
            self.Error_Text = error_text
        self.undoAction.append(text)
        # self.enc = self.newEnc
        self.SetStatusText(os.path.basename(path))
        self.MenuBar.Enable(wx.ID_SAVE, True)
        self.MenuBar.Enable(wx.ID_SAVEAS, True)
        self.MenuBar.Enable(wx.ID_CLOSE, True)
        self.toolBar1.EnableTool(1010, True)  # Save        
        self.previous_action['repSpec'] = self.newEnc
        self.reloaded = 0
        event.Skip()
        
    def onCleanup(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0 and self.reloaded == 0:
            dl = self.ShowDialog()
            if dl == False:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)        
        if len(self.multiFile) >= 1:
            return
    
        if os.path.isfile('resources\\var\\path0.pkl'):
            with open('resources\\var\\path0.pkl', 'rb') as p:
                path = pickle.load(p)          # path je u tmp/ folderu
            with open('resources\\var\\enc0.pkl', 'rb') as e:
                entered_enc = pickle.load(e)
            self.enchistory[path] = entered_enc
            self.newEnc = entered_enc
        else:
            text = self.text_1.GetValue()
            path = 'tmp\\Untitled.srt'
            if not os.path.isfile(path):
                open(path, 'a').close()
            writeTempStr(path, text, 'utf-8')
        
        entered_enc = self.encAction(path)
        self.newEnc = entered_enc
            
        self.pre_suffix = 'cln'
        
        subs = pysrt.open(path, encoding=entered_enc)
        if len(subs) > 0:
                
            fproc = TextProcessing(entered_enc, path)
            fproc.cleanUp()
            try:
                deleted, trimmed = fproc.cleanLine()
                logger.debug(f"CleanUp _1: {sys.exc_info()}")
                msginfo = wx.MessageDialog(self, f'Subtitles deleted:   [ {deleted} ]\nSubtitles trimmed: [ {trimmed} ]', 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                msginfo.ShowModal()                
            except TypeError as e:
                logger.debug(f"CleanUp _2: {sys.exc_info()}")
                msginfo = wx.MessageDialog(self, 'Subtitle clean\nno changes made.', 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                msginfo.ShowModal()                
            fproc.unix2DOS()
            text = fproc.getContent()
            self.text_1.SetValue(text)
            self.undoAction.append(text)
            # self.enc = self.newEnc
            self.SetStatusText(os.path.basename(path))
            self.MenuBar.Enable(wx.ID_SAVE, True)
            self.MenuBar.Enable(wx.ID_SAVEAS, True)
            self.MenuBar.Enable(wx.ID_CLOSE, True)
            self.toolBar1.EnableTool(1010, True)  # Save            
            self.previous_action['Cleanup'] = self.newEnc
            self.reloaded = 0
        else:
            logger.debug(f"Cleanup: No subtitles found!")
            self.previous_action['Cleanup'] = self.newEnc
            return
        event.Skip()
    
    def onMergeLines(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0 and self.reloaded == 0:
            dl = self.ShowDialog()
            if dl == False:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)        
        if len(self.multiFile) >= 1:
            return
    
        if os.path.isfile('resources\\var\\path0.pkl'):
            with open('resources\\var\\path0.pkl', 'rb') as p:
                path = pickle.load(p)          # path je u tmp/ folderu
            with open('resources\\var\\enc0.pkl', 'rb') as e:
                entered_enc = pickle.load(e)
            self.enchistory[path] = entered_enc
            self.newEnc = entered_enc
            self.orig_path = path + '.orig'
            shutil.copy(path, self.orig_path)            
        else:
            text = self.text_1.GetValue()
            path = 'tmp\\Untitled.srt'
            if not os.path.isfile(path):
                open(path, 'a').close()
            writeTempStr(path, text, 'utf-8')
        
        entered_enc = self.encAction(path)
        self.newEnc = entered_enc                           # path je u tmp/ folderu
        
        try:
            with shelve.open('resources\\var\\dialog_settings.db', flag='writeback') as  sp:
                ex = sp['key2']
                lineLenght = ex['l_lenght']; maxChar = ex['m_char']; maxGap = ex['m_gap']; file_suffix = ex['f_suffix']
        except IOError as e:
            logger.debug("Merger, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e: #handle other exceptions such as attribute errors
            logger.debug("Merger, unexpected error:", sys.exc_info())        
        
        fproc = FileProcessed(entered_enc, path)
        name, b = fproc.newName(path, file_suffix, self.real_dir, multi=False)
        fproc.remove_bom_inplace()
        
        try:
            with open(path, 'r', encoding=entered_enc) as f:
                textis = srt.parse(f.read())
                outf = srt.compose(textis)
                writeTempStr(path, outf, entered_enc)
        except IOError as e:
            logger.debug("Merger srt, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e: #handle other exceptions such as attribute errors
            logger.debug("Merger _1, unexpected error: {}".format(sys.exc_info()))
            if format(sys.exc_info()[0]) == "<class 'srt.SRTParseError'>":
                logger.debug('SRTParseError: This error is harmless.')
        
        self.pre_suffix = file_suffix
        
        myMerger(file_in=path, file_out=path, max_time=lineLenght, max_char=maxChar, _gap=maxGap, kode=entered_enc)
        
        fixLast(infile=path, kode=entered_enc)
        fproc.unix2DOS()
        text = fproc.getContent()
        self.text_1.SetValue(text)
        a1 = len(pysrt.open(self.orig_path, encoding=entered_enc))
        b1 = len(pysrt.open(path, encoding=entered_enc))
        prf = format(((a1 - b1) / a1 * 100), '.2f')
        logger.debug('Merger: Spojenih linija ukupno: {}, ili {} %'.format(a1 - b1, prf))
        sDlg = wx.MessageDialog(self, 'Merged file:\n\nSpojenih linija ukupno: {0}, ili {1} %'.format(a1 - b1, prf), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
        sDlg.ShowModal()
        self.undoAction.append(text)
        # self.enc = self.newEnc
        self.SetStatusText(os.path.basename(path))
        self.MenuBar.Enable(wx.ID_SAVE, True)
        self.MenuBar.Enable(wx.ID_SAVEAS, True)
        self.MenuBar.Enable(wx.ID_CLOSE, True)
        self.reload.Enable(True)
        self.toolBar1.EnableTool(1010, True)  # Save            
        self.reloaded = 0
        self.previous_action['Merger'] = self.newEnc
        event.Skip()
    
    def onSave(self, event):  # wxGlade: MyFrame.<event_handler>
        if os.path.isfile('resources\\var\\path0.pkl') and self.modify == False:
            with open('resources\\var\\path0.pkl', 'rb') as p:
                tpath = pickle.load(p)
            enc = self.enchistory[tpath]
            fproc = FileProcessed(enc, tpath)
            # text = fproc.getContent()
            fname, nsuffix = fproc.newName(tpath, self.pre_suffix, self.real_dir, multi=False)
            outpath = fproc.nameDialog(fname, nsuffix, self.real_dir)  # Puna putanja sa imenom novog fajla
            if outpath:
                shutil.copy(tpath, outpath)
                if os.path.isfile(outpath):
                    logger.debug(f"File saved sucessfully. {outpath}")
                    sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(outpath)), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                    sDlg.ShowModal()
                    # Dodaje putanju i enkoding u recnik
                    self.saved_file[outpath] = self.newEnc                
                    self.MenuBar.Enable(wx.ID_SAVE, False)
                    self.MenuBar.Enable(wx.ID_SAVEAS, False)
                    self.toolBar1.EnableTool(1010, False)
                    self.open_next.Enable(True)
                    self.reload.Enable(True)
        elif os.path.isfile('resources\\var\\path0.pkl') and self.modify == True:
            with open('resources\\var\\path0.pkl', 'rb') as p:
                tpath = pickle.load(p)            
            self.pre_suffix = 'new'
            entered_enc = self.encAction(tpath)
            fproc = FileProcessed(entered_enc, tpath)
            fname, nsuffix = fproc.newName(tpath, self.pre_suffix, self.real_dir, multi=False)
            outpath = fproc.nameDialog(fname, nsuffix, self.real_dir)
            if outpath:
                new_fproc = FileProcessed(entered_enc, outpath)
                text = self.text_1.GetValue()
                text = new_fproc.writeToFile(text)
                self.text_1.SetValue(text)
                if os.path.isfile(outpath):
                    logger.debug(f"File saved sucessfully. {outpath}")
                    sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(outpath)), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                    sDlg.ShowModal()
                    self.saved_file[outpath] = entered_enc                
                    self.MenuBar.Enable(wx.ID_SAVE, False)
                    self.MenuBar.Enable(wx.ID_SAVEAS, False)
                    self.toolBar1.EnableTool(1010, False)
                    self.open_next.Enable(True)
                    self.reload.Enable(True)
        else:
            tpath = 'tmp\\Untitled.srt'
            self.newEnc = 'utf-8'
            self.pre_suffix = 'new'
            self.real_dir = os.getcwd()
            text = self.text_1.GetValue()
            fproc = FileProcessed(self.newEnc, tpath)
            fname, nsuffix = fproc.newName(tpath, self.pre_suffix, self.real_dir, multi=False)
            outpath = fproc.nameDialog(fname, nsuffix, self.real_dir)  # Puna putanja sa imenom novog fajla
            new_fproc = FileProcessed(self.newEnc, outpath)
            text = new_fproc.writeToFile(text)
            new_fproc.unix2DOS()
            if os.path.isfile(outpath):
                logger.debug(f"File saved sucessfully. {outpath}")
                sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(outpath)), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[outpath] = self.newEnc                
                self.MenuBar.Enable(wx.ID_SAVE, False)
                self.MenuBar.Enable(wx.ID_SAVEAS, False)
                self.toolBar1.EnableTool(1010, False)
                self.open_next.Enable(True)
                self.reload.Enable(True)
        
        event.Skip()
    
    def onSaveAs(self, event):
        if os.path.isfile('resources\\var\\path0.pkl'):
            with open('resources\\var\\path0.pkl', 'rb') as p:
                tpath = pickle.load(p)
        else:
            tpath = 'tmp\\Untitled.srt'
            fproc = FileProcessed('utf-8', tpath)
            text = self.text_1.GetValue()
            fproc.writeToFile(text)
            
        sas_wildcard =  "SubRip (*.srt)|*.srt|MicroDVD (*.sub)|*.sub|Text File (*.txt)|*.txt|All Files (*.*)|*.*"
        
        dlg = wx.FileDialog(self, message="Save file as ...", defaultDir=self.real_dir,
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
            if not self.newEnc:
                self.newEnc = 'utf-8'
            if os.path.isfile(tpath):
                fproc = FileProcessed(self.newEnc, tpath)
                text = fproc.getContent()
            else:
                text = self.text_1.GetValue()
            fproc = FileProcessed(self.newEnc, path)
            fproc.writeToFile(text)
            fproc.unix2DOS()
            if os.path.isfile(path):
                logger.debug(f"File saved sucessfully. {path}")
                sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(path)), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[path] = self.newEnc                
                self.MenuBar.Enable(wx.ID_SAVE, False)
                self.MenuBar.Enable(wx.ID_SAVEAS, False)
                self.toolBar1.EnableTool(1010, False)
                self.open_next.Enable(True)
                self.reload.Enable(True)
                # self.saved += 1
                # self.resetTool()
        else:
            dlg.Destroy()
        event.Skip()
        
    def exportZIP(self, event):
        if self.multiFile:
            if len(self.multiFile) > 1:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as f:
                dp = pickle.load(f)
            if len(dp) > 1:
                return        
        if os.path.isfile('resources\\var\\path0.pkl'):
            with open('resources\\var\\path0.pkl', 'rb') as p:
                fpath = pickle.load(p)
            tpath = os.path.basename(fpath)
                
        else:
            text = self.text_1.GetValue()
            fpath = 'tmp\\Untitled.srt'
            fp = FileProcessed(self.newEnc, fpath)
            fp.writeToFile(text)
            tpath = fpath
            
        sas_wildcard =  "ZipArchive (*.zip)|*.zip|All Files (*.*)|*.*"
        
        dlg = wx.FileDialog(self, message="Export file as ZIP",\
                            defaultDir=self.real_dir, defaultFile="", wildcard=sas_wildcard,\
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        try:
            if self.real_path:
                fname = os.path.basename(self.real_path[-1])
            else:
                fname = 'Untitled.srt'
        except IOError as e:
            logger.debug("On ZIP IOError({0}):".format(e))
        except IndexError as e:
            logger.debug("On ZIP IndexError({0}):".format(e))
        if not fname.endswith('.zip'):
            fname = fname + '.zip'
        else:
            fname = fname
        dlg.SetFilename(fname)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dirname = os.path.dirname(path)
            name = path
            if name.endswith('txt'):
                name = name + '.zip'
            elif name.endswith('srt'):
                name = name + '.zip'
            elif name.endswith('.py'):
                name = name + '.zip'
            if not os.path.isfile(tpath):
                shutil.copy(fpath, tpath)
            try:
                with zipfile.ZipFile(name, 'w') as fzip:
                    fzip.write(tpath)
            except IOError as e:
                logger.debug("Export ZIP, IOError({0}{1}):".format(self.putanja, e))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                logger.debug(''.join('!' + line for line in lines))
                
            shutil.move(name, os.path.join(dirname, name))
            
            if os.path.isfile(tpath):
                os.remove(tpath)
            if os.path.isfile(path):
                logger.debug(f"ZIP file saved sucessfully: {path}")
                sDlg = wx.MessageDialog(self, 'Fajl je uspešno sačuvan\n{}'.format(os.path.basename(path)), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                sDlg.ShowModal()
                # Dodaje putanju i enkoding u recnik
                self.saved_file[path] = self.newEnc                
                self.open_next.Enable(True)
                # self.saved += 1
                # self.resetTool()
        else:
            dlg.Destroy()
        event.Skip()
    
    def OnTextChanged(self, event):
        pass
        event.Skip()
        
    def onCloseFile(self, event):
        self.reload.Enable(True)
        event.Skip()
        
    def onFileHistory(self, event):
        # get the file based on the menu ID
        fileNum = event.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(fileNum)
        enc = self.enchistory[path]
        # add it back to the history so it will be moved up the list
        self.filehistory.AddFileToHistory(path)
        self.enchistory[path] = enc
        with open(path, 'r', encoding=enc, errors='replace') as f:
            text = f.read()
        self.text_1.SetValue(text)
        with open('resources\\var\\path0.pkl', 'wb') as v:
            pickle.dump(path, v)        
        self.enableTool()
        logger.debug(f'From fileHistory: {os.path.basename(path)} encoding: {enc}')
        self.SetStatusText(os.path.basename(path))
        event.Skip()
        
    def onCyrToANSI(self, event):
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)
            
        if len(self.multiFile) >= 1:
            self.multipleTools()
            self.cyrToANSI_multiple()
        else:        
        
            if os.path.isfile('resources\\var\\droped0.pkl'):
                with open('resources\\var\\droped0.pkl', 'rb') as f:
                    dp = pickle.load(f)
                if len(dp) > 1:
                    return        
            with open('resources\\var\\path0.pkl', 'rb') as p:
                path = pickle.load(p)
            with open('resources\\var\\enc0.pkl', 'rb') as e:
                entered_enc = pickle.load(e)
            self.enchistory[path] = entered_enc            
    
            entered_enc = self.encAction(path)
            self.pre_suffix = 'lat_ansi'
            self.newEnc = 'windows-1250'
            t_enc = 'utf-8'
            utf_tmpFile = path+'.TEMP_UTF'
            
            self.orig_path = path + '.orig'
            if not os.path.isfile(self.orig_path):
                shutil.copy(path, self.orig_path)
            #else:
                #shutil.copy(self.orig_path, path)
                
            fproc = FileProcessed(entered_enc, path)
            
            text = fproc.getContent()
            if text:
                text = text.replace('?', '¬')
            writeTempStr(utf_tmpFile, text, entered_enc)
            
            utfcyproc = Preslovljavanje(enc=t_enc, path=utf_tmpFile)
            text = utfcyproc.writeToFile(text)
            text = utfcyproc.getContent()
            text = utfcyproc.fixI(text)
            writeTempStr(utf_tmpFile, text, t_enc)
            utfcyproc.preLatin()
            utfcyproc.preProc(reversed_action=True)
            utfcyproc.changeLetters(reversed_action=True)
            text = utfcyproc.getContent()
            text = utfcyproc.rplStr(text)
            writeTempStr(utf_tmpFile, text, t_enc)
            ansi_cyproc = Preslovljavanje(self.newEnc, path)  #  Pise u path jer u SAVE se trazi path.
            ansi_cyproc.writeToFile(text)
            text = ansi_cyproc.getContent()
            error_text = utfcyproc.checkFile(self.orig_path, path, multi=False)
            text = self.fileErrors(path, self.newEnc)  # Ovde se vrate znakovi pitanja i ponovo upisu u fajl.
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
            self.SetStatusText(os.path.basename(path))
            self.save.Enable(True)
            self.save_as.Enable(True)
            self.close.Enable(True)
            self.toolBar1.EnableTool(1010, True)  # Save
            self.reload.Enable(True)
            self.reloaded = 0
            self.previous_action['cyrToANSI'] = self.newEnc
        event.Skip()
    
    def cyrToANSI_multiple(self):
        self.text_1.SetValue("")
        self.text_1.SetValue("Files Processed:\n")
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)        
        
        self.pre_suffix = 'lat_ansi'
        self.newEnc = 'windows-1250'
        t_enc = 'utf-8'
        
        for key, value in self.multiFile.items():
            path=key
            entered_enc=value        
            utf_tmpFile = path+'.TEMP_UTF'
        
            fproc = FileProcessed(entered_enc, path)
            
            text = fproc.getContent()
            if text:
                text = text.replace('?', '¬')
            writeTempStr(utf_tmpFile, text, entered_enc)
            
            utfcyproc = Preslovljavanje(enc=t_enc, path=utf_tmpFile)
            text = utfcyproc.writeToFile(text)
            text = utfcyproc.getContent()
            text = utfcyproc.fixI(text)
            writeTempStr(utf_tmpFile, text, t_enc)
            utfcyproc.preLatin()
            utfcyproc.preProc(reversed_action=True)
            utfcyproc.changeLetters(reversed_action=True)
            text = utfcyproc.getContent()
            text = utfcyproc.rplStr(text)
            writeTempStr(utf_tmpFile, text, t_enc)
            
            nam, b = fproc.newName(path, self.pre_suffix, self.real_dir, True)
            newF = '{0}{1}'.format(os.path.join(self.real_dir, nam), b)            
            
            ansi_cyproc = Preslovljavanje(self.newEnc, newF)  #  Pise u path jer u SAVE se trazi path.
            ansi_cyproc.writeToFile(text)
            self.text_1.AppendText('\n')
            self.text_1.AppendText(os.path.basename(newF))
            error_text = ansi_cyproc.checkFile(path, newF, multi=True)
            if error_text:
                ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
                ErrorDlg.ShowModal()
                self.Error_Text = error_text
                outf = newF + '.error.log'
                showMeError(newF, outf, self.newEnc)
                text = ansi_cyproc.getContent()
                text = text.replace('¬', '?')
                writeTempStr(newF, text, self.newEnc)
                ansi_cyproc.unix2DOS()
            text = ansi_cyproc.getContent()
            text = text.replace('¬', '?')
            writeTempStr(newF, text, self.newEnc)
            ansi_cyproc.unix2DOS()
            self.SetStatusText('Processing multiple files')
            text = utfcyproc.getContent()
            text = text.replace('¬', '?')
            writeTempStr(utf_tmpFile, text, t_enc)
            utfcyproc.unix2DOS()
        self.multipleTools()
        self.reloaded = 0
        self.previous_action['cyrToANSI_multiple'] = self.newEnc
        self.SetStatusText('Multiple files done.')
        
    def onCyrToUTF(self, event):
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as f:
                dp = pickle.load(f)
            if len(dp) > 1:
                return        
        with open('resources\\var\\path0.pkl', 'rb') as p:
            path = pickle.load(p)
        with open('resources\\var\\enc0.pkl', 'rb') as e:
            entered_enc = pickle.load(e)
        self.enchistory[path] = entered_enc        
            
        
        entered_enc = self.encAction(path)
        
        self.pre_suffix = 'lat_utf8'
        
        if self.preferences.IsChecked(1011):
            self.newEnc = 'utf-8-sig'
        else:
            self.newEnc = 'utf-8'
        t_enc = 'utf-8'
        
        self.orig_path = path + '.orig'
        if not os.path.isfile(self.orig_path):
            shutil.copy(path, self.orig_path)
        
        fproc = FileProcessed(entered_enc, path)
        
        text = fproc.getContent()
        if text:
            text = text.replace('?', '¬')
        writeTempStr(path, text, entered_enc)
        
        cyproc = Preslovljavanje(self.newEnc, path)
        text = cyproc.writeToFile(text)
        text = cyproc.fixI(text)
        writeTempStr(path, text, self.newEnc)
        cyproc.preProc(reversed_action=True)
        cyproc.changeLetters(reversed_action=True)
        text = cyproc.getContent()
        text = cyproc.writeToFile(text)
        text = cyproc.rplStr(text)
        writeTempStr(path, text, self.newEnc)
        error_text = cyproc.checkFile(self.orig_path, path, multi=False)
        text = self.fileErrors(path, self.newEnc)
        if error_text:
            ErrorDlg = wx.MessageDialog(self, error_text, "SubConverter", wx.OK | wx.ICON_ERROR)
            ErrorDlg.ShowModal()
            self.Error_Text = error_text
        self.SetStatusText(os.path.basename(path))
        self.save.Enable(True)
        self.save_as.Enable(True)
        self.close.Enable(True)
        self.toolBar1.EnableTool(1010, True)  # Save
        self.reload.Enable(True)
        self.reloaded = 0
        self.previous_action['cyrToUTF'] = self.newEnc
        event.Skip()
        
    def onFixSubs(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files ') and len(tval) > 0 and self.save.IsEnabled() and len(self.undoAction) > 0 and self.reloaded == 0:
            dl = self.ShowDialog()
            if dl == False:
                return
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as f:
                dp = pickle.load(f)
            if len(dp) > 1:
                return        
        if os.path.isfile('resources\\var\\droped0.pkl'):
            with open('resources\\var\\droped0.pkl', 'rb') as d:
                droped_files = pickle.load(d)
            self.multiFile.clear()
            self.multiFile.update(droped_files)        
        if len(self.multiFile) >= 1:
            self.multipleTools()
            # self.toUTF_multiple()
        else:
            if os.path.isfile('resources\\var\\path0.pkl'):
                with open('resources\\var\\path0.pkl', 'rb') as p:
                    path = pickle.load(p)          # path je u tmp/ folderu
                with open('resources\\var\\enc0.pkl', 'rb') as e:
                    entered_enc = pickle.load(e)
                self.enchistory[path] = entered_enc
            else:
                text = self.text_1.GetValue()
                path = 'tmp\\Untitled.srt'
                if not os.path.isfile(path):
                    open(path, 'a').close()
                writeTempStr(path, text, 'utf-8')
                self.pre_suffix = 'utf8'                           # path je u tmp/ folderu
        
        with open('resources\\var\\rpath0.pkl', 'rb') as r:
            rpath = pickle.load(r)
            
        try:
            with shelve.open('resources\\var\\dialog_settings.db', flag='writeback') as  sp:
                ex = sp['key1']
                cb1_s = ex['state1']; cb2_s = ex['state2']; cb3_s = ex['state3']
                cb4_s = ex['state4']; cb5_s = ex['state5']; cb6_s = ex['state6']; cb7_s = ex['state7']; cb8_s = ex['state8']
        except IOError as e:
            logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as e: #handle other exceptions such as attribute errors
            logger.debug("FixSubtitle, unexpected error:", sys.exc_info()[0:2])
            
        entered_enc = self.encAction(path)
        self.pre_suffix = 'fixed'
        self.newEnc = entered_enc   # VAZNO za Save funkciju
        
        
        subs = pysrt.open(path, encoding=entered_enc)
        if len(subs) == 0:
            logger.debug("Fixer: No subtitles found.")
        else:
            fproc = TextProcessing(entered_enc, path)
            fproc.remove_bom_inplace()
            
            def chg(filein, kode):
                subs = pysrt.open(filein, kode)
                N = 0
                for first, second in zip(subs, subs[1:]):  
                    t1 = first.end.ordinal
                    t2 = second.start.ordinal
                    if t1 > t2 or t2 - t1 < 85:
                        N += 1
                return N
        
            def rpt():
                m = 0; s1 = 0
                while True:
                    x, y = fixGaps(filein=path, kode=entered_enc)
                    m += x
                    s1 += y
                    if x == 0:
                        break
                return m, s1            
        
            if cb1_s == True:
                if not cb8_s == True:
                
                    pn = chg(filein=path, kode=entered_enc)
                    if pn > 0:
                        m, s1 = rpt()
                    else:
                        m = 0; s1 = 0
                    fixLast(infile=path, kode=entered_enc)
                else:
                    logger.debug('Fixer: Remove gaps not enabled.')
            try:
                with open(path, 'r', encoding=entered_enc) as f:
                    textis = srt.parse(f.read())
                    outf = srt.compose(textis)
            except IOError as e:
                logger.debug("FixSubtitle, I/O error({0}): {1}".format(e.errno, e.strerror))
            except: #handle other exceptions such as attribute errors
                logger.debug("FixSubtitle, unexpected error: {}".format(sys.exc_info()[0:2]))
            if format(sys.exc_info()[0]) == "<class 'srt.SRTParseError'>":
                logger.debug('SRTParseError, error is harmless.')           
            else:
                if len(outf) > 0:
                    writeTempStr(inFile=path, text=outf, kode=entered_enc)
                        
            fproc.rm_dash()
            fproc.unix2DOS()
            text = fproc.getContent()
            self.text_1.SetValue(text)
            # writeTempStr(path, text, entered_enc)
        
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
                        sDlg = wx.MessageDialog(self, 'Subtitle fix\n\nPopravljenih gapova među linijama ukupno: {}\n{}'
                                                        .format(m, m1), 'SubConverter', wx.OK | wx.ICON_INFORMATION)
                        sDlg.ShowModal()
        self.previous_action['FixSubtitle'] = self.newEnc
        self.SetStatusText(os.path.basename(path))
        self.save.Enable(True)
        self.save_as.Enable(True)
        self.close.Enable(True)
        self.toolBar1.EnableTool(1010, True)  # Save
        self.reload.Enable(True)
        self.reloaded = 0        
        event.Skip()
    
    def encAction(self, path):
        if self.previous_action:
            actions = ['toCYR', 'toUTF', 'toANSI', 'Transcribe', 'repSpec', 'Cleanup', 'cyrToANSI', 'cyrToUTF', 'FixSubtitle', 'Merger']
            for a in actions:
                try:
                    entered_enc = self.previous_action.pop(a)
                except Exception as e:
                    logger.debug(f"Searching for key: {sys.exc_info()[1]}")
                else:
                    logger.debug(f"New entered_enc: {entered_enc}.")
                    return entered_enc
        else:
            entered_enc = self.enchistory[path]
            return entered_enc
      
    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        # print(keycode)
        if keycode <= 98 and not keycode == 88 and not keycode == 13:
            self.undohist.append(self.text_1.GetValue())
            self.modify = True
            self.toolBar1.EnableTool(1010, True)
            self.save.Enable(True)
            self.save_as.Enable(True)
            self.export_zip.Enable(True)            
        else:
            pass
        if len(self.undohist) >= 30: self.undohist=self.undohist[1:]
        # print(self.undohist)
        # print(self.modify)
        self.undo.Enable(True)
        self.toolBar1.EnableTool(101, True)
        # self.redo.Enable(True)
        # self.clear.Enable(True)
        event.Skip()
        
    def OnTextGetSelection(self, event):
        self.text_1.FindFocus()
        if self.text_1.GetStringSelection():
            start, end = self.text_1.GetSelection()
            
        event.Skip()
    
    def OnUpdateEditMenu(self, event):
        event_id = event.GetId()
        sel = self.text_1.GetSelection()
        has_sel = sel[0] != sel[1]
        if event_id in (wx.ID_COPY, wx.ID_CUT):
            event.Enable(has_sel)
        else:
            
            event.Skip()
        
    
    def OnUndo(self, event):
        self.redohist.append(self.text_1.GetValue())
        self.text_1.Undo()
        self.redo.Enable(True)
        #try:
            ## self.text_1.ShowNativeCaret(False)
            #self.redohist.append(self.text_1.GetValue())
            #place=self.text_1.GetInsertionPoint() - 1
            #p1 = self.text_1.GetInsertionPoint() + 1
            #self.text_1.SetInsertionPoint(p1)
            #self.text_1.SetValue(self.undohist[len(self.undohist)-1])
            #self.text_1.SetInsertionPoint(place)
        #except:
            #logger.debug('List undohist out of range.')
        
        #self.undohist=self.undohist[:-1] # minus poslednj element
        #if len(self.redohist) >= 30: self.redohist=self.redohist[1:]  # kada se doda sledeci umanji se za 1 ako je vise od limita
        #if len(self.undohist) == 0:
            #self.paste.Enable(False)
            #self.undo.Enable(False)
            #self.toolBar1.EnableTool(101, False)
        event.Skip()
        
    def OnRedo(self, event):
        place=self.text_1.GetInsertionPoint()
        try:
            self.text_1.SetValue(self.redohist[len(self.redohist)-1])
        except:
            logger.debug('List redohist out of range')
        self.text_1.SetInsertionPoint(place)
        self.redohist=self.redohist[:-1]
        if len(self.redohist) == 0:
            self.redo.Enable(False)
        event.Skip()
    
    def OnClear(self, event):
        if self.text_1.GetStringSelection():
            start, end = self.text_1.GetSelection()        
            self.text_1.Replace(start, end, "")
        event.Skip()
    
    def OnCut(self, event):
        self.text_1.Cut()
        self.paste.Enable(True)
        event.Skip()

    def OnPaste(self, event):
        self.text_1.FindFocus()
        self.text_1.Paste()
        event.Skip()
        
    def OnCopy(self, event):
        self.text_1.Copy()
        self.paste.Enable(True)
        event.Skip()
        
    def onAbout(self, event):
        text = u"SubConverter\n\nJednostavna wxPython aplikacija \nza konvertovanje srt i txt fajlova\ni transkripciju engleskih imena i pojmova.\n\nProgram ima ove opcije:\n-Preslovljavanje latinice u ćirilicu i promena kodnog rasporeda.\n-Konvertovanje unikode u ANSI format.\n-Konvertovanje ANSI u unikode.\n-Default izlazni kodeci su cp1250, 1251 i utf-8.\n-Zamena engleskih imena u titlu odgovarajućim iz rečnika.\n Default izlazni kodek je UTF-8.\n-Mogućnost dodavanja novih definicija za transkripciju u rečnicima.\n-Program konvertuje titlove sa ćiriličnim pismom u latinicu.\n\nAutor: padovaSR\nhttps://github.com/padovaSR\nLicense: GNU GPL v2"
        AboutDlg = wx.MessageDialog(self, text, "SubConverter {}".format(VERSION), wx.OK | wx.ICON_INFORMATION)
        AboutDlg.ShowModal()
        event.Skip()
        
    def removeFiles(self, event):
        if os.listdir('tmp'):
            file_paths = glob.glob('tmp\*.*')
            fileData = {}
            for fname in file_paths:
                fileData[fname] = os.stat(fname).st_mtime
                
            sortedFiles = sorted(fileData.items(), key=itemgetter(1))
            
            delete = len(sortedFiles) - 34
            for x in range(0, delete):
                os.remove(sortedFiles[x][0])
                # print(sortedFiles[x][0])
        event.Skip()    

    def onChoice(self, event):
        ctrl = event.GetEventObject()
        value = ctrl.GetValue()
        uEnkode = value
        with open('resources\\var\\obsE.pkl', 'wb') as f:
            pickle.dump(uEnkode, f)        
        event.Skip()
    
    def utfSetting(self, event):
        if self.preferences.IsChecked(1012):
            item_txt = 'txt'
        else:
            item_txt = 'srt'
        with open('resources\\var\\tcf.pkl', 'wb') as tf:
            pickle.dump(item_txt, tf)
            
        if self.preferences.IsChecked(1011):
            item = 'Checked'
        else:
            item = 'NotChecked'
        with open('resources\\var\\bcf.pkl', 'wb') as fb:
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
            with shelve.open('resources\\var\\dialog_settings.db', flag='writeback') as s:
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
    
    def onQuit(self, event):
        tval = self.text_1.GetValue()
        if not tval.startswith('Files List:') and len(tval) > 0 and self.save.IsEnabled():
            dl1 = wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO, self)
            if dl1 == wx.NO:
                return
            else:
                self.Destroy()
        else:
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
        
# end of class MyFrame

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        if os.path.isfile('resources\\var\\r_text0.pkl'):
            os.remove('resources\\var\\r_text0.pkl')
        if os.path.isfile('resources\\var\\droped0.pkl'):
            os.remove('resources\\var\\droped0.pkl')
        if os.path.exists('resources\\LatCyr.map.cfg'):
            os.remove('resources\\LatCyr.map.cfg')
        if os.path.exists('resources\\var\\path0.pkl'):
            os.remove('resources\\var\\path0.pkl')
        if os.path.isfile('resources\\var\\rpath0.pkl'):
            os.remove('resources\\var\\rpath0.pkl')
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')        
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
