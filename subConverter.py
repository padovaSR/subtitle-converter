#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# generated by wxGlade 0.8.0b1

import wx

from wx.lib.pubsub import pub
import os
import sys
import zipfile
from na_functions import fileOpened

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
                pub.sendMessage('dnd', filepath=os.path.basename(outfile))
            
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

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("frame")
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

    def openFile(self, event):  # wxGlade: MyFrame.<event_handler>
        dlgOpen = wx.FileDialog(self, "Open file to convert", style=wx.FD_OPEN, wildcard=self.wildcard) # creates the Open File dialog
        if dlgOpen.ShowModal() == wx.ID_OK:
            self.filepath = dlgOpen.GetPath() # Get the file location
            path = self.filepath
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

    def transcribe(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'transcribe' not implemented!")
        event.Skip()

    def replaceSpecial(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'replaceSpecial' not implemented!")
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
    
