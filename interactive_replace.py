#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.0.0a9; modified by padovaSR
#

import os
import re
import srt
from srt import Subtitle
from pydispatch import dispatcher 
from collections import defaultdict 
from zamenaImena import dict_fromFile 
from settings import WORK_TEXT 
import logging.config

import wx


logger = logging.getLogger(__name__)


def getSubs(filein):
    """"""
    with open(filein, "r", encoding="utf-8") as f:
        return f.read()
    

class FindReplace(wx.Dialog):
    def __init__(self, parent, subtitles=[]):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.subtitles = subtitles
        subtitles = self.subtitles
        
        self.dname = r""
        
        self.SetSize((525, 400))
        self.SetTitle("Find-Replace from dictionary")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(
            wx.Bitmap(
                os.path.join("resources", "icons", "system-run.png"), wx.BITMAP_TYPE_ANY
            )
        )
        self.SetIcon(_icon)
        
        SetFont = dict_fromFile(os.path.join("resources", "var", "dialog_font.conf"), "=")
        tFont = defaultdict(str)
        tFont.update(SetFont)
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        label_1 = wx.StaticText(
            self, wx.ID_ANY, f"Replace from dictionary:  {self.dname}", style=wx.ALIGN_LEFT
        )
        label_1.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                tFont["LabelFont"], 
            )
        )
        sizer_1.Add(label_1, 0, wx.EXPAND | wx.LEFT | wx.TOP, 6)

        t_font = wx.Font(
                int(tFont["fSize"]),
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                tFont["TextFont"],
            )

        self.text_1 = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE|wx.TE_NO_VSCROLL|wx.TE_RICH)
        self.text_1.SetFont(t_font)
        sizer_1.Add(self.text_1, 0, wx.ALL | wx.EXPAND, 5)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)

        self.text_2 = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE|wx.TE_RICH)
        self.text_2.SetFont(t_font)
        self.text_2.SetToolTip("Text modification is supported")
        self.text_2.SetFocus()
        sizer_2.Add(self.text_2, 1, wx.ALL | wx.EXPAND, 5)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(
            sizer_3, 0, wx.BOTTOM | wx.EXPAND | wx.RIGHT | wx.SHAPED | wx.TOP, 5
        )

        self.button_0 = wx.Button(self, wx.ID_ANY, "Find")
        self.button_0.SetMinSize((76, 25))
        sizer_3.Add(self.button_0, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)

        self.button_1 = wx.Button(self, wx.ID_REPLACE, "Accept")
        self.button_1.SetMinSize((76, 25))
        self.button_1.SetDefault()
        sizer_3.Add(self.button_1, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)

        self.button_2 = wx.Button(self, wx.ID_ANY, "Replace all")
        self.button_2.SetMinSize((76, 25))
        sizer_3.Add(self.button_2, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)

        self.button_3 = wx.Button(self, wx.ID_ANY, "Ignore")
        self.button_3.SetMinSize((76, 25))
        sizer_3.Add(self.button_3, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)

        self.button_4 = wx.Button(self, wx.ID_ANY, "Ignore all")
        self.button_4.SetMinSize((76, 25))
        sizer_3.Add(self.button_4, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        
        self.button_5 = wx.Button(self, wx.ID_ANY, "Show text")
        self.button_5.SetMinSize((76, 25))
        sizer_3.Add(self.button_5, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)        

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetMinSize((76, 25))
        sizer_3.Add(self.button_OK, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)        
        
        self.button_7 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_7.SetMinSize((76, 25))
        sizer_3.Add(self.button_7, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)

        self.filePicker = wx.FilePickerCtrl(
            self,
            wx.ID_ANY,
            "",
            "Select a file",
            "Text File (*.txt)|*.txt|All Files (*.*)|*.*",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.FLP_DEFAULT_STYLE,
        )
        self.filePicker.SetInitialDirectory(os.path.join(os.getcwd(), "dicitionaries"))
        self.filePicker.SetToolTip(" \n Find dictionary \n ")
        self.filePicker.SetPath(os.path.abspath("dictionaries/Dictionary-1.txt"))
        self.dname = self.filePicker.GetPath()
        sizer_1.Add(self.filePicker, 0, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        self.SetSizer(sizer_1)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_7.GetId())

        self.Layout()
        self.Centre()

        ############################################################################################

        self.Ignored = []
        self.ReplacedAll = []
        self.Replaced = []
        self.new_subs = []
        # self.default_subs = getSubs("test.srt")
        self.default_subs = srt.compose(subtitles)
        self.new_d = {}
        
        ## Events ##################################################################################
        self.filePicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.FileChanged, self.filePicker)        
        self.Bind(wx.EVT_BUTTON, self.getValues, self.button_0)
        self.Bind(wx.EVT_BUTTON, self.onReplace, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.onReplaceAll, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.onIgnore, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.onIgnoreAll, self.button_4)
        self.Bind(wx.EVT_BUTTON, self.onShowText, self.button_5)
        self.Bind(wx.EVT_BUTTON, self.onOK, self.button_OK)
        ############################################################################################
        
        self.wdict = dict_fromFile(self.dname, "=>")
        self.subs = srt.parse(self.default_subs)
        self.wdict = self.clearDict(self.wdict, srt.compose(self.subs))
        self.getValues(self.subs)
        
    def getValues(self, iterator):
        """"""
        c = 0
        wdict = self.wdict
        r1 = re.compile(r"\b("+"|".join(map(re.escape, wdict.keys()))+r")\b")
        try:
            sub = next(iterator)
            c += 1
        except StopIteration:
            wdict = self.clearDict(wdict, srt.compose(self.new_subs, reindex=False))
            logger.debug(f"Iterator was empty")
        finally:
            p = "="*20
            self.text_2.SetValue(f"{p}\nEnd of subtitles reached!\n{p}")
        try:
            t1 = r1.findall(sub.content)
            t1 = list(set(t1))            
            newd = {}
            self.text_1.Clear()
            for i in range(len(t1)):
                self.text_1.AppendText(f"{t1[i]} ")
                v = wdict[t1[i]]
                newd[t1[i]] = v
            for k, v in newd.items():
                ctext = re.compile(r'\b'+k+r'\b')
                sub.content = ctext.sub(v, sub.content)
            self.text_2.SetValue(sub.content)
            for v in newd.values():
                for m in re.finditer(v, self.text_2.GetValue()):
                    self.text_2.SetStyle(m.start(), m.end(), wx.TextAttr("RED"))
            if t1:
                self.Replaced.append(Subtitle(sub.index, sub.start, sub.end, sub.content))
                for v in newd.values(): self.ReplacedAll.append(v)
                self.new_d = newd
                self.button_1.SetFocus()
            return c
        except Exception as e:
            logger.debug(f"Error: {e}")
            
    def FileChanged(self, event):
        """"""
        self.filePicker.SetPath(self.filePicker.GetPath())
        self.button_1.SetFocus()
        self.dname = self.filePicker.GetPath()
        wdict = dict_fromFile(self.dname, "=>")
        self.subs = srt.parse(self.default_subs)
        self.wdict = self.clearDict(wdict, srt.compose(self.subs, reindex=False))
        self.subs = srt.parse(self.default_subs)
        self.onReplace(event)
        event.Skip()

    def onShowText(self, event):
        ''''''
        self.replaceCurrent()
        self.text_1.Clear()
        self.text_2.Clear()
        self.text_2.SetValue(self.GetText())
        for x in self.Ignored:
            ctext = re.compile(r"\b"+x+r"\b")
            for m in re.finditer(ctext, self.text_2.GetValue()):
                self.text_2.SetStyle(m.start(), m.end(), wx.TextAttr(wx.BLUE))            
        for x in set(self.ReplacedAll):
            ctext = re.compile(r"\b"+x+r"\b")
            for m in re.finditer(ctext, self.text_2.GetValue()):
                self.text_2.SetStyle(m.start(), m.end(), wx.TextAttr(wx.RED, wx.YELLOW))
                self.text_2.SetInsertionPoint(m.end())
        self.button_1.SetLabelText("Continue")
        self.button_1.SetFocus()
        event.Skip()
    
    def replaceCurrent(self):
        """"""
        if self.Replaced:
            text = self.text_2.GetValue()
            sub = self.Replaced[0]
            self.Replaced.clear()
            self.new_subs.append(Subtitle(sub.index, sub.start, sub.end, text))
        
    def onReplace(self, event):
        ''''''
        self.replaceCurrent()
        self.button_1.SetLabelText("Accept")
        while len(self.Replaced) == 0:
            c = self.getValues(self.subs)
            if c == 0 or c is None:
                break
        event.Skip()

    def onReplaceAll(self, event):
        ''''''
        try:
            ctext = re.compile(r"\b("+"|".join(map(re.escape,self.new_d.keys()))+r")\b")
            self.default_subs = ctext.sub(lambda x: self.new_d[x.group()], self.default_subs)
            wsubs = srt.compose(self.subs, reindex=False)
            wsubs = ctext.sub(lambda x: self.new_d[x.group()], wsubs)
            for k, v in self.new_d.items():
                self.ReplacedAll.append(v)
                self.wdict.pop(k)
            self.subs = srt.parse(wsubs)
            self.onReplace(event)
        except Exception as e:
            logger.debug(f"Error: {e}")
        event.Skip()

    def onOK(self, event):
        """"""
        WORK_TEXT.truncate(0)
        WORK_TEXT.write(self.GetText())
        WORK_TEXT.seek(0)
        dispatcher.send("DIALOG", message=self.ReplacedAll)
        event.Skip()
    
    def onIgnore(self, event):
        ''''''
        for i in self.text_1.GetValue().split():
            self.Ignored.append(i.strip())
        self.Replaced.clear()
        self.onReplace(event)
        event.Skip()

    def onIgnoreAll(self, event):
        for i in self.text_1.GetValue().split():
            self.Ignored.append(i.strip())
        for k in self.Ignored: self.wdict.pop(k)
        self.Replaced.clear()
        self.onReplace(event)        
        event.Skip()
    
    def clearDict(self, _dict, _subs):
        """"""
        new_dict = {}
        robj1 = re.compile(r"\b("+"|".join(map(re.escape, _dict.keys()))+r")\b")
        t_out1 = robj1.findall(_subs)
        for i in t_out1:
            for k, v in _dict.items():
                if i == k:
                    new_dict[i] = v
        self.subs = srt.parse(self.default_subs)
        return new_dict
    
    def GetText(self):
        """"""
        d_subs = list(srt.parse(self.default_subs))
        for i in d_subs:
            for x in self.new_subs:
                if i.start == x.start and i.content == x.content:
                    d_subs.remove(i)
                if i.index == x.index:
                    try:
                        d_subs[d_subs.index(i)] = x
                    except:
                        d_subs.append(x)
        self.default_subs = srt.compose(d_subs)
        return self.default_subs

# end of class FindReplace

class MyApp(wx.App):
    def OnInit(self):
        self.dialog = FindReplace(None, wx.ID_ANY)
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
