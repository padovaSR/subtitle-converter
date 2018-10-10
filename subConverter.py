#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# generated by wxGlade 0.8.0b1

import wx

import os
import sys
import zipfile
import re
import textwrap
import pysrt
from na_functions import fileOpened
from merger_settings import Settings
from FixSettings import fixerSettings

VERSION = 'v0.5.5.2'

class RedirectTextCtrl(wx.TextCtrl):
    def __init__(self, my_text_ctrl):
        self.out = my_text_ctrl
        
    def write(self,string):
        wx.CallAfter(self.out.WriteText, string)
        
class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    def OnDropFiles(self, x, y, filenames):
        for name in filenames:
            fzip = fileOpened()
            if zipfile.is_zipfile(name) == True:
                print('ZIP archive: {}'.format(os.path.basename(name)))
                outfile = fzip.isCompressed(infile=name)
                if outfile:
                    #
        return True

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.window_1 = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.window_1_pane_1 = wx.Panel(self.window_1, wx.ID_ANY)
        self.text_ctrl_1 = wx.TextCtrl(self.window_1_pane_1, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_RICH2)
        dt = FileDrop(self.text_ctrl_1)
        self.text_ctrl_1.SetDropTarget(dt)
        self.window_1_pane_2 = wx.Panel(self.window_1, wx.ID_ANY)
        self.text_ctrl_2 = wx.TextCtrl(self.window_1_pane_2, wx.ID_ANY, "", style=wx.TE_BESTWRAP | wx.TE_MULTILINE | wx.TE_READONLY)
        self.wildcard = "SubRip (*.zip; *.srt)|*.zip; *.srt|MicroDVD (*.sub)|*.sub|Text File (*.txt)|*.txt|All Files (*.*)|*.*"
        
        # Tool Bar
        self.frame_toolbar = wx.ToolBar(self, -1, style=wx.TB_3DBUTTONS | wx.TB_HORIZONTAL)
        self.SetToolBar(self.frame_toolbar)
        self.frame_toolbar.AddTool(1001, "open", wx.Bitmap("resources\\icons\\Open1.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Open File", "Otvori fajl")
        self.frame_toolbar.AddTool(1002, "cyrillic", wx.Bitmap("resources\\icons\\Cyrillic.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Conver to cyrillic", "Konvertuje u cirilicu")
        self.frame_toolbar.AddTool(1003, "ansi", wx.Bitmap("resources\\icons\\ANSI.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Convert to ANSI", "Konveruje u ANSI")
        self.frame_toolbar.AddTool(1004, "unicode", wx.Bitmap("resources\\icons\\UTF8.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Convert to unicode", "KOnveruje u unikode")
        self.frame_toolbar.AddTool(1005, "transkripcija", wx.Bitmap("resources\\icons\\transkribuj.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Transcibe subtitles", "Transkripcija")
        self.frame_toolbar.AddTool(1006, "specijal", wx.Bitmap("resources\\icons\\Special.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Special replace", "Zamena i brisanje ")
        self.frame_toolbar.AddTool(1007, "info", wx.Bitmap("resources\\icons\\Help-file1.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Open the about dialog", "Informacije o programu")
        self.frame_toolbar.AddTool(1008, "exit", wx.Bitmap("resources\\icons\\Exit.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "Exit", "Zatvori program")
        self.frame_toolbar.AddSeparator()
    
        comboBox1Choices = [ u"deafult", u"cyr to latin utf8", u"cyr to latin ansi" ]
        self.comboBox1 = wx.ComboBox(self.frame_toolbar, wx.ID_ANY, u"auto", wx.DefaultPosition, wx.Size( 122,25 ), comboBox1Choices, wx.CB_READONLY)
        self.comboBox1.SetFont( wx.Font( 9, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft Sans Serif" ))
        self.comboBox1.SetSelection(0)
        self.comboBox1.SetToolTip(u"Izbor transliterizacije\ni izlaznog kodiranja")
        self.frame_toolbar.AddControl(self.comboBox1)        
        self.frame_toolbar.AddSeparator()
        
        comboBox2Choices = [ u"auto", u"windows-1250", u"windows-1251", u"windows-1252", u"utf-8", u"utf-16le", u"utf-32", u"iso-8859-5", u"latin", u"latin2" ]
        self.comboBox2 = wx.ComboBox(self.frame_toolbar, wx.ID_ANY, u"auto", wx.DefaultPosition, wx.Size( 122,25 ), comboBox2Choices, wx.CB_READONLY)
        self.comboBox2.SetSelection(0)
        self.comboBox2.SetFont( wx.Font( 9, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft Sans Serif" ))
        self.comboBox2.SetToolTip(u"Izbor enkodiranja ulaznog\nfajla. Ako je poznato, ili\nnije automatski obrađeno.")
        self.frame_toolbar.AddControl(self.comboBox2)
        self.frame_toolbar.AddSeparator()
    
        self.checkBox1 = wx.CheckBox(self.frame_toolbar, wx.ID_ANY, "cleanup", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.checkBox1.SetToolTip("Clenup subtitle file\nremove HI")
        self.checkBox1.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Microsoft Sans Serif" ))
        self.frame_toolbar.AddControl(self.checkBox1)        
        
        # Tool Bar end
        self.frame_statusbar = self.CreateStatusBar(1, wx.STB_DEFAULT_STYLE)
        
        # redirect text here
        redir = RedirectText(self.text_ctrl_2)
        sys.stdout = redir
        
        # Menu Bar
        self.frame_menubar = wx.MenuBar()
        self.File = wx.Menu()
        self.frame_menubar.open = self.File.Append(wx.NewId(), "&Open\tCTRL+O", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.openFile, id=self.frame_menubar.open.GetId())
        self.File.AppendSeparator()
        self.frame_menubar.next = self.File.Append(wx.NewId(), "&Next...\tALT+E", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.openNext, id=self.frame_menubar.next.GetId())
        self.File.AppendSeparator()
        self.File.Append(1009, "Exit\tCTRL+Q", "Zatvori program\tCTRL+Q", wx.ITEM_NORMAL)
        self.frame_menubar.Append(self.File, "File")
        self.actions = wx.Menu()
        self.frame_menubar.cyr = self.actions.Append(wx.NewId(), "&ToCyrillic\tCTRL+Y", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.toCyrillic, id=self.frame_menubar.cyr.GetId())
        self.frame_menubar.ansi = self.actions.Append(wx.NewId(), "&ToANSI\tALT+S", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.toANSI, id=self.frame_menubar.ansi.GetId())
        self.frame_menubar.unicode = self.actions.Append(wx.NewId(), "&ToUNICODE\tALT+D", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.toUTF, id=self.frame_menubar.unicode.GetId())
        self.frame_menubar.transkrib = self.actions.Append(wx.NewId(), "&Transcribe\tALT+N", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.transcribe, id=self.frame_menubar.transkrib.GetId())
        self.frame_menubar.special = self.actions.Append(wx.NewId(), "&SpecReplace\tALT+C", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.replaceSpecial, id=self.frame_menubar.special.GetId())
        self.frame_menubar.cleanup = self.actions.Append(wx.NewId(), "&Cleanup\tALT+K", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onClean, id=self.frame_menubar.cleanup.GetId())
        self.actions.AppendSeparator()
        self.frame_menubar.fix = self.actions.Append(wx.NewId(), "&FixSubtitle\tALT+F", "Ukloni greške u\nformatiranju titla", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onFix, id=self.frame_menubar.fix.GetId())
        self.actions.AppendSeparator()
        self.frame_menubar.merg = self.actions.Append(wx.NewId(), "&Merger\tCTRL+M", "Merge subtitle lines", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onMergeSubs, id=self.frame_menubar.merg.GetId())
        self.frame_menubar.Append(self.actions, "Actions")        
        self.edit = wx.Menu()
        self.frame_menubar.b = self.edit.Append(1011, "&Create backup", "Create backup copy\nof working file", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.onCreateBackup, id=1011)
        self.edit.AppendSeparator()
        self.frame_menubar.utf = self.edit.Append(1012, "&BOM_UTF-8", "Default for utf-8", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.def_UTF, id=1012)
        self.edit.AppendSeparator()
        self.frame_menubar.fixer = self.edit.Append(wx.NewId(), "&FixSubtitle", "FixSubtitle settings", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onFixerSettings, id=self.frame_menubar.fixer.GetId())
        self.edit.AppendSeparator()
        self.frame_menubar.merger = self.edit.Append(wx.NewId(), "&Merger", "Merger settings", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onSettings, id=self.frame_menubar.merger.GetId())
        self.frame_menubar.Append(self.edit, "Preferences")
        self.Help = wx.Menu()
        self.frame_menubar.h = self.Help.Append(wx.NewId(), "&About\tCTRL+I", "Informacije o programu", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.aboutProgram, id=self.frame_menubar.h.GetId())
        self.frame_menubar.Append(self.Help, "Help")
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TOOL, self.openFile, id=1001)
        self.Bind(wx.EVT_TOOL, self.toCyrillic, id=1002)
        self.Bind(wx.EVT_TOOL, self.toANSI, id=1003)
        self.Bind(wx.EVT_TOOL, self.toUTF, id=1004)
        self.Bind(wx.EVT_TOOL, self.transcribe, id=1005)
        self.Bind(wx.EVT_TOOL, self.replaceSpecial, id=1006)
        self.Bind(wx.EVT_TOOL, self.aboutProgram, id=1007)
        self.Bind(wx.EVT_TOOL, self.exitProg, id=1008)
        # end wxGlade
        self.text_ctrl_1.Bind(wx.EVT_TEXT, self.updateStatus, id=-1)
        
    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle('Subtitle Converter {}'.format(VERSION))
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("resources\\icons\\subConvert.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetFocus()
        self.text_ctrl_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI"))
        self.text_ctrl_1.SetFocus()
        self.text_ctrl_2.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI"))
        self.window_1.SetMinimumPaneSize(20)
        self.frame_toolbar.SetToolBitmapSize((16, 15))
        self.frame_toolbar.SetMargins((0, 0))
        self.frame_toolbar.SetToolPacking(1)
        self.frame_toolbar.SetToolSeparation(5)
        self.frame_toolbar.Realize()
        self.frame_statusbar.SetStatusWidths([-1])

        # statusbar fields
        frame_statusbar_fields = ["frame_statusbar"]
        for i in range(len(frame_statusbar_fields)):
            self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_2.Add(self.text_ctrl_1, 1, wx.ALL | wx.EXPAND, 1)
        self.window_1_pane_1.SetSizer(self.sizer_2)
        self.sizer_3.Add(self.text_ctrl_2, 1, wx.ALL | wx.EXPAND, 1)
        self.window_1_pane_2.SetSizer(self.sizer_3)
        self.window_1.SplitHorizontally(self.window_1_pane_1, self.window_1_pane_2, 369)
        sizer_1.Add(self.window_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.SetSizeHints(self)
        self.Layout()
        self.SetSize((702, 639))
        # end wxGlade
    
    # Update Status Bar  
    def updateStatus(self, event):
        with open('resources\\var\\path0.pickle', 'rb') as pickl_file:
            path = pickle.load(pickl_file)
        self.SetStatusText(os.path.basename(path))
        event.Skip()

    def openFile(self, event):  # wxGlade: MyFrame.<event_handler>
        dlgOpen = wx.FileDialog(self, "Open file to convert", style=wx.FD_OPEN, wildcard=self.wildcard) # creates the Open File dialog
        if dlgOpen.ShowModal() == wx.ID_OK:
            self.filepath = dlgOpen.GetPath() # Get the file location
            path = self.filepath
            fzip = fileOpened()
            if zipfile.is_zipfile(path) == True:
                print('ZIP archive: {}'.format(os.path.basename(path)))
                outfile = fzip.isCompressed(infile=path)
                if outfile:
                    #
                    #
                    self.SetStatusText(os.path.basename(outfile))
            elif zipfile.is_zipfile(path) == False:
                #
                #
                self.SetStatusText(os.path.basename(path))
            dlgOpen.Destroy()
        else:
            dlgOpen.Destroy()
        event.Skip()

    def toCyrillic(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'toCyrillic' not implemented!")
        event.Skip()

    def toANSI(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'toANSI' not implemented!")
        event.Skip()

    def toUTF(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'toUTF' not implemented!")
        event.Skip()

    def fixM(self, infile, kode):
        subs = pysrt.open(infile, encoding=kode)
        if len(subs) > 0:
            for_rpl = re.compile(r'^((.*?\n.*?){1})\n')
            new_e = pysrt.SubRipFile()
            for i in subs:
                t = i.text
                if t.count('\n') == 0 and t.count(' ') > 2 and len(t) >= 30:
                    nw = round(len(t) / 2) + 1
                    if re.findall(r'<[^<]*>', t):
                        nw = nw + 4            
                    if len(t) < 30:
                        nw = 30
                    if len(t) >= 30 and len(t) < 36:
                        nw = round(len(t) / 2)
                        n = textwrap.fill(t, width=nw)
                        n = f_rpl.sub(r'\1 ', n)
                    if n.count('\n') == 2:
                        nn = round(len(t.split('\n')[-1]) / 2) + 1
                        n = textwrap.fill(n, width=nw)
                        n = f_rpl.sub(r'\1 ', n)
                        sub = pysrt.SubRipItem(i.index, i.start, i.end, n)
                        n = textwrap.fill(n, width=nw+nn)
                        if n.count('\n') == 2:
                            n = f_rpl.sub(r'\1 ', n)
                            new_e.append(sub)
                    else:
                        sub = pysrt.SubRipItem(i.index, i.start, i.end, n)
                        new_e.append(sub)
                else:
                    sub = pysrt.SubRipItem(i.index, i.start, i.end, t)
                    new_e.append(sub)
            new_e.clean_indexes()
            new_e.save(infile, encoding=kode)
    
    def transcribe(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'transcribe' not implemented!")
        event.Skip()

    def replaceSpecial(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'replaceSpecial' not implemented!")
        event.Skip()
        
    def onSettings(self, event):
        settings_dialog = Settings(None, -1, "")
        settings_dialog.ShowModal()
        event.Skip()
        
    def onFixerSettings(self, event):
        fix_dialog = fixerSettings(None)
        fix_dialog.ShowModal()
        event.Skip()

    def aboutProgram(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'aboutProgram' not implemented!")
        event.Skip()

    def exitProg(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'exitProg' not implemented!")
        event.Skip()

# end of class MyFrame

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
    
