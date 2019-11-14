#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.4
#
import pickle
import os
import logging

from settings import filePath
from zamenaImena import shortcutsKey

import wx


logger = logging.getLogger(__name__)

class ConverterFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ConverterFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        try:
            with open(filePath("resources","var","set_size.pkl"), "rb") as wf:
                size_dict = pickle.load(wf)
                w = size_dict["W"]
                h = size_dict["H"]
            self.SetSize((w, h))
        except Exception as e:
            logger.debug(f"SetSize error: {e}")
            self.SetSize((622, 573))
        
        # Menu Bar
        
        keyS = shortcutsKey
        
        self.frame_menubar = wx.MenuBar()
        self.file = wx.Menu()
        self.fopen = wx.MenuItem(self.file, wx.ID_OPEN, "&Open\t"+keyS["Open"], "Otvori fajl", wx.ITEM_NORMAL)
        self.fopen.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))

        self.file.Append(self.fopen)
        
        self.open_next = wx.MenuItem(self.file, wx.ID_ANY,
                                     "&Open next...\t"+keyS["Open next"], u"Otvori sačuvani fajl", wx.ITEM_NORMAL)
        self.open_next.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_GO_DIR_UP, wx.ART_MENU))
        self.file.Append(self.open_next)
        self.open_next.Enable(False)
        
        self.file.AppendSeparator()
        self.reload = wx.MenuItem(self.file, wx.ID_ANY,
                                  "&Reload file\t"+keyS["Reload file"], "Ponovo učitaj fajl", wx.ITEM_NORMAL)
        self.reload.SetBitmap(wx.Bitmap(filePath("resources", "icons", "reload.png"), wx.BITMAP_TYPE_ANY))
        self.file.Append(self.reload)
        self.reload.Enable(False)

        self.file.AppendSeparator()
        
        self.save = wx.MenuItem(self.file, wx.ID_SAVE, "&Save\t"+keyS["Save"], "Sačuvaj fajl", wx.ITEM_NORMAL)
        self.save.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU))
        self.file.Append(self.save)
        self.save.Enable(False)
        
        self.save_as = wx.MenuItem(self.file, wx.ID_SAVEAS,
                                   "&Save as...\t"+keyS["Save as"], "Sačuvaj fajl kao...", wx.ITEM_NORMAL)
        self.save_as.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU))
        self.file.Append(self.save_as)
        self.save_as.Enable(False)

        self.export_zip = wx.MenuItem(self.file, wx.ID_ANY,
                                      "&Export as ZIP\t"+keyS["Export as ZIP"], "Izvezi u zip formatu", wx.ITEM_NORMAL)
        self.export_zip.SetBitmap(wx.Bitmap(filePath("resources", "icons", "zip_file.png"), wx.BITMAP_TYPE_ANY))
        self.file.Append(self.export_zip)
        self.export_zip.Enable(False)
        
        self.file.AppendSeparator()

        self.close = wx.MenuItem(self.file, wx.ID_CLOSE, "&Close\t"+keyS["Close"], "Zatvori fajl", wx.ITEM_NORMAL)
        self.close.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_MENU))
        self.file.Append(self.close)
        self.close.Enable(False)

        self.file.AppendSeparator()

        # Submenu
        self.file_sub = wx.Menu()
        self.file_sub.Append(-1, "Recent files", "")
        self.file.Append(-1, "Recent", self.file_sub, "")

        self.file.AppendSeparator()
        # Submenu end        

        self.quit_program = wx.MenuItem(self.file, wx.ID_ANY, "&Quit\t"+keyS["Quit"], "Quit program", wx.ITEM_NORMAL)
        self.quit_program.SetBitmap(wx.Bitmap(filePath("resources", "icons", "application-exit.png"), wx.BITMAP_TYPE_ANY))
        self.file.Append(self.quit_program)
        self.frame_menubar.Append(self.file, u"File")
        
        # Edit menu -----------------------------------------------------------------------------------------------------------------------
        self.edit = wx.Menu()
        self.undo = wx.MenuItem(self.edit, wx.ID_UNDO, "&Undo\t"+keyS["Undo"], "Undo change", wx.ITEM_NORMAL)
        self.undo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_MENU))
        self.edit.Append(self.undo)
        self.undo.Enable(False)
        
        self.redo = wx.MenuItem(self.edit, wx.ID_REDO, "&Redo\t"+keyS["Redo"], "Redo change", wx.ITEM_NORMAL)
        self.redo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU))
        self.edit.Append(self.redo)
        self.redo.Enable(False)
        
        self.edit.AppendSeparator()
        
        self.cut = wx.MenuItem(self.edit, wx.ID_CUT, "&Cut\t"+keyS["Cut"], "Cut text", wx.ITEM_NORMAL)
        self.cut.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_MENU))
        self.edit.Append(self.cut)
        self.cut.Enable(False)
        
        self.copy = wx.MenuItem(self.edit, wx.ID_COPY, "&Copy\t"+keyS["Copy"], "Copy text", wx.ITEM_NORMAL)
        self.copy.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
        self.edit.Append(self.copy)
        self.copy.Enable(False)
        
        self.paste = wx.MenuItem(self.edit, wx.ID_PASTE, "&Paste\t"+keyS["Paste"], "Paste text", wx.ITEM_NORMAL)
        self.paste.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_MENU))
        self.edit.Append(self.paste)
        self.paste.Enable(False)
        
        self.edit.AppendSeparator()
        
        self.find = wx.MenuItem(self.edit, wx.ID_FIND, "&Find\t"+keyS["Find"], "Find text", wx.ITEM_NORMAL)
        self.find.SetBitmap(wx.Bitmap(filePath("resources", "icons", "search.png"), wx.BITMAP_TYPE_ANY))
        self.edit.Append(self.find)
        self.find.Enable(False)
        
        self.frame_menubar.Append(self.edit, "Edit")        
        
        # Actions   -----------------------------------------------------------------------------------------------------------------------
        self.action = wx.Menu()
        self.to_cyrillic = wx.MenuItem(self.action, wx.ID_ANY,
                                       "&ToCyrillic\t"+keyS["ToCyrillic"], "Konvertuje u ćirilicu", wx.ITEM_NORMAL)
        self.to_cyrillic.SetBitmap(wx.Bitmap(filePath("resources", "icons", "cyr-ltr.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.to_cyrillic)
        self.to_cyrillic.Enable(False)

        self.to_ansi = wx.MenuItem(self.action, wx.ID_ANY,
                                   "&ToANSI\t"+keyS["ToANSI"], "Konvertuje u ANSI", wx.ITEM_NORMAL)
        self.to_ansi.SetBitmap(wx.Bitmap(filePath("resources", "icons", "go-next.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.to_ansi)
        self.to_ansi.Enable(False)

        self.to_utf8 = wx.MenuItem(self.action, wx.ID_ANY,
                                   "&ToUTF\t"+keyS["ToUTF"], "Konvertuje u UTF", wx.ITEM_NORMAL)
        self.to_utf8.SetBitmap(wx.Bitmap(filePath("resources", "icons", "go-next.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.to_utf8)
        self.to_utf8.Enable(False)

        self.action.AppendSeparator()

        self.transcrib = wx.MenuItem(self.action, wx.ID_ANY,
                                     "&Transcribe\t"+keyS["Transcribe"], "Transcribe", wx.ITEM_NORMAL)
        self.transcrib.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_MENU))
        self.action.Append(self.transcrib)
        self.transcrib.Enable(False)

        self.specials = wx.MenuItem(self.action, wx.ID_ANY,
                                    "&SpecReplace\t"+keyS["SpecReplace"], "ReplaceSpecial definicije", wx.ITEM_NORMAL)
        self.specials.SetBitmap(wx.Bitmap(filePath("resources", "icons", "go-next.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.specials)
        self.specials.Enable(False)
       
        self.cleaner = wx.MenuItem(self.action, wx.ID_ANY,
                                   "&Cleanup\t"+keyS["Cleanup"], "Clean subtitle file", wx.ITEM_NORMAL)
        self.cleaner.SetBitmap(wx.Bitmap(filePath("resources", "icons", "edit-clear-all.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.cleaner)
        self.cleaner.Enable(False)

        self.action.AppendSeparator()
        self._regex = wx.MenuItem(self.action, wx.ID_ANY,
                                  "&CustomRegex\t"+keyS["CustomRegex"], "Apply Regex", wx.ITEM_NORMAL)
        self._regex.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_MENU))
        self.action.Append(self._regex)
        self._regex.Enable(False)
        
        self.action.AppendSeparator()

        self.cyr_to_ansi = wx.MenuItem(self.action, wx.ID_ANY, "&Cyr to latin ansi\t"+keyS["Cyr to latin ansi"],
                                       "Preslovljavanje cirilice u latinicu ansi", wx.ITEM_NORMAL)
        self.cyr_to_ansi.SetBitmap(wx.Bitmap(filePath("resources", "icons", "go-next.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.cyr_to_ansi)
        self.cyr_to_ansi.Enable(False)

        self.cyr_to_utf = wx.MenuItem(self.action, wx.ID_ANY, "&Cyr to latin utf8\t"+keyS["Cyr to latin utf8"],
                                      "Preslovljavanje cirilice u latinicu utf8", wx.ITEM_NORMAL)
        self.cyr_to_utf.SetBitmap(wx.Bitmap(filePath("resources", "icons", "go-next.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.cyr_to_utf)
        self.cyr_to_utf.Enable(False)

        self.action.AppendSeparator()
        
        self.fixer = wx.MenuItem(self.action, wx.ID_ANY,
                                 "&FixSubtitle\t"+keyS["FixSubtitle"], "Fix subtitle file", wx.ITEM_NORMAL)
        self.fixer.SetBitmap(wx.Bitmap(filePath("resources", "icons", "go-next.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.fixer)
        self.fixer.Enable(False)

        self.action.AppendSeparator()

        self.merger = wx.MenuItem(self.action, wx.ID_ANY, "&Merger\t"+keyS["Merger"], "Merge lines", wx.ITEM_NORMAL)
        self.merger.SetBitmap(wx.Bitmap(filePath("resources", "icons", "merge.png"), wx.BITMAP_TYPE_ANY))
        self.action.Append(self.merger)
        self.merger.Enable(False)

        self.frame_menubar.Append(self.action, u"Actions")

        # Preferences menu ----------------------------------------------------------------------------------------------------------------
        self.preferences = wx.Menu()
        self.bom_utf8 = wx.MenuItem(self.preferences, 1011,
                                    "&bom_utf-8\t"+keyS["bom_utf-8"], u"Default za unikode", wx.ITEM_CHECK)
        self.bom_utf8.SetBitmap(wx.NullBitmap)
        self.preferences.Append(self.bom_utf8)

        self.txt_utf8 = wx.MenuItem(self.preferences, 1012,
                                    "&txt_utf-8\t"+keyS["txt_utf-8"], u"Default fajl format unikode", wx.ITEM_CHECK)
        self.txt_utf8.SetBitmap(wx.NullBitmap)
        self.preferences.Append(self.txt_utf8)

        self.preferences.AppendSeparator()

        self.fonts = wx.MenuItem(self.preferences, wx.ID_ANY,
                                 "&Font settings\t"+keyS["Font settings"], "Font settings", wx.ITEM_NORMAL)
        self.fonts.SetBitmap(wx.Bitmap(filePath("resources", "icons", "preferences-font.png"), wx.BITMAP_TYPE_ANY))
        self.preferences.Append(self.fonts)

        self.preferences.AppendSeparator()

        self.fixer_settings = wx.MenuItem(self.preferences, wx.ID_ANY,
                                          "&FixerSettings\t"+keyS["FixerSettings"], wx.EmptyString, wx.ITEM_NORMAL)
        self.fixer_settings.SetBitmap(wx.Bitmap(filePath("resources", "icons", "dialog-settings.png"), wx.BITMAP_TYPE_ANY))
        self.preferences.Append(self.fixer_settings)

        self.preferences.AppendSeparator()
        
        self.shortcuts = wx.MenuItem(self.preferences, wx.ID_ANY, "&ShortcutEditor\t"+keyS["ShortcutEditor"], "Shortcut keys", wx.ITEM_NORMAL)
        self.shortcuts.SetBitmap(wx.Bitmap(filePath("resources", "icons", "input-keyboard.png"), wx.BITMAP_TYPE_ANY))
        self.preferences.Append(self.shortcuts)        
        
        self.preferences.AppendSeparator()

        self.merger_pref = wx.MenuItem(self.preferences, wx.ID_ANY,
                                       "&MergerSettings"+keyS["MergerSettings"], wx.EmptyString, wx.ITEM_NORMAL)
        self.merger_pref.SetBitmap(wx.Bitmap(filePath("resources", "icons", "merge-settings.png"), wx.BITMAP_TYPE_ANY))
        self.preferences.Append(self.merger_pref)
        self.frame_menubar.Append(self.preferences, u"Preferences")

        self.help = wx.Menu()
        self.about = wx.MenuItem(self.help, wx.ID_ANY, "&About\t"+keyS["About"], "O programu", wx.ITEM_NORMAL)
        self.about.SetBitmap(wx.Bitmap(filePath("resources", "icons", "help-about.png"), wx.BITMAP_TYPE_ANY))
        self.help.Append(self.about)
        
        self.help.AppendSeparator()
        
        self.manual = wx.MenuItem(self.help, wx.ID_ANY, "&Manual\t"+keyS["Manual"], "Manual", wx.ITEM_NORMAL)
        self.manual.SetBitmap(wx.Bitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_PAGE, wx.ART_MENU)))
        self.help.Append(self.manual)        

        self.frame_menubar.Append(self.help, u"Help")

        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end
        
        self.frame_statusbar = self.CreateStatusBar(1)
        
        # Tool Bar
        self.frame_toolbar = wx.ToolBar(self, -1, style=wx.TB_DEFAULT_STYLE)
        self.SetToolBar(self.frame_toolbar)
        self.frame_toolbar.AddTool(1001, "Open", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, wx.DefaultSize),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Open file", "Open file")
        self.frame_toolbar.AddTool(1010, "Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, wx.DefaultSize),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Save file", "Save file")

        self.frame_toolbar.AddSeparator()
        
        self.frame_toolbar.AddTool(101, "Undo_action", wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, wx.DefaultSize),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Undo action", "Undo action")
        self.frame_toolbar.AddTool(102, "Redo_action", wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR, wx.DefaultSize),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Redo action", "Redo Action")
        self.frame_toolbar.AddSeparator()

        self.frame_toolbar.AddTool(1002, "Cirilica", wx.Bitmap(filePath("resources","icons","cyrillic.png"), wx.BITMAP_TYPE_ANY),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "U cirilicu", "U cirilicu")
        self.frame_toolbar.AddTool(1003, "ANSI", wx.Bitmap(filePath("resources","icons","ANSI.png"), wx.BITMAP_TYPE_ANY),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "U ansi", "U ansi")
        self.frame_toolbar.AddTool(1004, "UTF", wx.Bitmap(filePath("resources","icons","UTF8.png"), wx.BITMAP_TYPE_ANY),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "U utf-8", "U utf-8")
        self.frame_toolbar.AddTool(1005, "Transcribe", wx.Bitmap(filePath("resources","icons","cyr-ltr.24.png"), wx.BITMAP_TYPE_ANY),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Transcribe", "Transcribe")
        self.frame_toolbar.AddTool(1006, "Special", wx.Bitmap(filePath("resources","icons","edit-find-replace.png"), wx.BITMAP_TYPE_ANY),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Replace speial", "Replace special")
        self.frame_toolbar.AddTool(1007, "Cleanup", wx.Bitmap(filePath("resources","icons","editclear.png"), wx.BITMAP_TYPE_ANY),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Cleanup", "Cleanup")
        
        self.frame_toolbar.AddTool(1008, "Quit", wx.Bitmap(filePath("resources","icons","application-exit.24.png"), wx.BITMAP_TYPE_ANY),
                                   wx.NullBitmap, wx.ITEM_NORMAL, "Exit", "Exit program")
        
        self.frame_toolbar.AddSeparator()
        
        comboBox1Choices = [u" auto", u" windows-1250", u" windows-1251", u" windows-1252", u" utf-8", u" utf-16", " utf-16le", u" utf-16be", 
                    u" utf-32", u" iso-8859-1", u" iso-8859-2", u" iso-8859-5", u" latin", u" latin2" ]        
                
        self.comboBox1 = wx.ComboBox(self.frame_toolbar, wx.ID_ANY, "combo1", wx.DefaultPosition, wx.DefaultSize,
                                     comboBox1Choices, wx.CB_DROPDOWN)
        
        self.comboBox1.SetToolTip( u"Kodiranje" )        
        self.frame_toolbar.AddControl( self.comboBox1 )
        self.comboBox1.SetSelection(0)         
        
        # Tool Bar end
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.text_1 = wx.TextCtrl(self.panel_1, wx.ID_ANY,
                                  "", style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.TE_RICH | wx.TE_WORDWRAP)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        # begin wxGlade: ConverterFrame.__set_properties
        self.SetTitle("frame")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(filePath("resources","icons","subConvert.ico"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetFocus()
        self.frame_statusbar.SetStatusWidths([-1])
        
        with open(filePath('resources', 'var', 'bcf.pkl'), 'rb') as bf:
            item = pickle.load(bf)
        if item == 'Checked':
            self.preferences.Check(1011, check=True)
        if os.path.exists(filePath('resources', 'var', 'tcf.pkl')):
            with open(filePath('resources', 'var', 'tcf.pkl'), 'rb') as tf:
                item_txt = pickle.load(tf)
            if item_txt == 'txt':
                self.preferences.Check(1012, check=True)        
    
        # statusbar fields
        frame_statusbar_fields = ["Subtitle Converter is ready"]
        for i in range(len(frame_statusbar_fields)):
            self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)
        self.frame_toolbar.SetMargins((0, 0))
        self.frame_toolbar.SetToolPacking(1)
        self.frame_toolbar.SetToolSeparation(5)
        self.frame_toolbar.Realize()
        self.text_1.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        self.text_1.SetToolTip("ToolTip")
        self.text_1.ShowNativeCaret(show=True)
        self.text_1.SetFocus()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ConverterFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.text_1, 1, wx.ALL | wx.EXPAND, 3)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def onNew(self, event):  
        event.Skip()

# end of class ConverterFrame

class MyApp(wx.App):
    def OnInit(self):
        self.frame = ConverterFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
