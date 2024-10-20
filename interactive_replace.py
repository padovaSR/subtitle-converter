#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.0.0a9; modified by padovaSR
#
import os
from os.path import join 
import re
import srt
from srt import Subtitle
from collections import defaultdict 
from resources.DictHandle import Dictionaries
from settings import WORK_TEXT, I_PATH, MAIN_SETTINGS
import logging.config

import wx


logger = logging.getLogger(__name__)


def getSubs(filein):
    """"""
    with open(filein, "r", encoding="utf-8") as f:
        return f.read()
    

class FindReplace(wx.Dialog):
    def __init__(self, parent, subtitles=[]):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.RESIZE_BORDER)
        
        try:
            size = MAIN_SETTINGS["ReplaceDialog"]
            self.SetSize((size["W"], size["H"]))
        except:
            self.SetSize((540, 621))
        self.SetTitle("Find-Replace manually")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(join(I_PATH,"edit-find-replace.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        SetFont = Dictionaries().dict_fromFile(join("resources", "var", "I_dialog.conf"), "=")
        tFont = defaultdict(str)
        tFont.update(SetFont)        

        sizer_2 = wx.BoxSizer(wx.VERTICAL)

        self.label_1 = wx.StaticText(self, wx.ID_ANY, "Replace from dictionary")
        self.label_1.SetFont(
            wx.Font(
                9,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                "Segoe UI",
            )
        )
        sizer_2.Add(self.label_1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)

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
        self.filePicker.SetMinSize((500, 24))
        self.filePicker.SetInitialDirectory(os.path.join(os.getcwd(), "dictionaries"))
        self.filePicker.SetToolTip(" \n Find dictionary \n ")
        self.filePicker.SetPath(os.path.abspath("dictionaries/Dictionary-1.txt"))
        self.dname = self.filePicker.GetPath()        
        sizer_2.Add(self.filePicker, 0, wx.ALL | wx.EXPAND, 8)        
        
        t_font1 = wx.Font(
                int(tFont["fontSize"]),
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                tFont["TextFont"],
            )        
        self.text_1 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.text_1.SetMinSize((500, 25))
        self.text_1.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                "Franklin Gothic Medium",
            )
        )
        self.text_1.SetForegroundColour("BLUE")
        self.text_1.SetToolTip("Enter text for search")
        sizer_2.Add(self.text_1, 0, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
                
        self.text_2 = wx.TextCtrl(
            self,
            wx.ID_ANY,
            "",
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_RICH,
        )
        self.text_2.SetMinSize((500, 350))
        self.text_2.SetFont(t_font1)
        self.text_2.SetToolTip(" Text modification \n is supported ")
        sizer_3.Add(self.text_2, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT, 8)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 5)

        self.button_0 = wx.Button(self, wx.ID_ANY, "Find")
        self.button_0.SetMinSize((75, 23))
        self.button_0.SetToolTip("F3 key \nFind in text")
        sizer_4.Add(self.button_0, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 1)

        self.button_1 = wx.Button(self, wx.ID_ANY, "Accept")
        self.button_1.SetMinSize((75, 23))
        self.button_1.SetToolTip("TAB key \nAccept text")
        sizer_4.Add(self.button_1, 0, wx.ALL, 1)

        self.button_2 = wx.Button(self, wx.ID_ANY, "Replace all")
        self.button_2.SetMinSize((75, 23))
        self.button_2.SetToolTip("Ctrl+L  \nAll occurrences")
        sizer_4.Add(self.button_2, 0, wx.ALL, 1)

        self.button_3 = wx.Button(self, wx.ID_ANY, "Ignore")
        self.button_3.SetMinSize((75, 23))
        self.button_3.SetToolTip("Ctrl+I \nIgnore the replacement")
        sizer_4.Add(self.button_3, 0, wx.ALL, 1)

        self.button_4 = wx.Button(self, wx.ID_ANY, "Ignore all")
        self.button_4.SetMinSize((75, 23))
        sizer_4.Add(self.button_4, 0, wx.ALL, 1)
        
        self.button_add = wx.Button(self, wx.ID_ADD, "")
        self.button_add.SetMinSize((75, 23))
        self.button_add.SetToolTip("Shift+C keys \nAdd selected \nto dictionary")
        sizer_4.Add(self.button_add, 0, wx.ALL, 1)        

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetMinSize((75, 23))
        self.button_OK.SetToolTip("Accept all the changes \nand exit dialog")
        sizer_4.Add(self.button_OK, 0, wx.ALL, 1)

        self.button_6 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_6.SetMinSize((75, 23))
        sizer_4.Add(self.button_6, 0, wx.ALL, 1)
        
        t_font2 = wx.Font(
                int(tFont["fontSize2"]),
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                tFont["Text2Font"],
            )        
        self.text_3 = wx.TextCtrl(
            self,
            wx.ID_ANY,
            "",
            style=wx.TE_MULTILINE
            | wx.TE_CENTER
            | wx.TE_NO_VSCROLL
            | wx.TE_NOHIDESEL
            | wx.TE_PROCESS_ENTER
            | wx.TE_RICH2,
        )
        self.text_3.SetMinSize((500, 89))
        self.text_3.SetFont(t_font2)
        self.text_3.SetToolTip(" Text modification \n is supported ")
        sizer_2.Add(self.text_3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_1, 0, wx.EXPAND, 0)        
        
        self.text_ADD = wx.TextCtrl(
            self,
            wx.ID_ANY,
            "",
            style=wx.TE_NOHIDESEL | wx.TE_NO_VSCROLL | wx.TE_PROCESS_ENTER | wx.TE_RICH,
        )
        self.text_ADD.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                0,
                "Franklin Gothic Medium",
            )
        )
        self.text_ADD.SetToolTip("Enter text")
        sizer_1.Add(self.text_ADD, 1, wx.ALL | wx.EXPAND, 8)
        self.button_dict = wx.Button(self, wx.ID_ANY, "OK")
        self.button_dict.SetMinSize((68, 28))
        self.button_dict.Enable(False)
        self.button_dict.SetDefault()
        sizer_1.Add(self.button_dict, 0, wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM | wx.TOP, 8)

        self.button_cancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.button_cancel.SetMinSize((68, 28))
        self.button_cancel.Enable(False)
        sizer_1.Add(self.button_cancel, 0, wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM | wx.RIGHT | wx.TOP, 8)        
        
        self.SetSizer(sizer_2)
        #sizer_2.SetSizeHints(self)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_6.GetId())

        self.Layout()
        self.Centre()
        
        ############################################################################################

        self.Ignored = []
        self.ReplacedAll = []
        self.Replaced = []
        self.new_subs = []
        self.new_d = {}
        self.find = []
        #self.default_subs = getSubs("test.srt")
        self.default_subs = srt.compose(subtitles)
        
        ## Events ##################################################################################
        self.filePicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.FileChanged, self.filePicker)
        self.text_1.Bind(wx.EVT_TEXT, self.Text1, self.text_1)
        self.Bind(wx.EVT_BUTTON, self.onFind, self.button_0)
        self.Bind(wx.EVT_BUTTON, self.onReplace, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.onReplaceAll, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.onIgnore, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.onIgnoreAll, self.button_4)
        self.Bind(wx.EVT_BUTTON, self.onOK, self.button_OK)
        self.Bind(wx.EVT_BUTTON, self.addSelected, self.button_add)
        self.text_ADD.Bind(wx.EVT_TEXT, self.textAdded, self.text_ADD)
        self.Bind(wx.EVT_BUTTON, self.addOK, self.button_dict)
        self.Bind(wx.EVT_BUTTON, self.addCANCEL, self.button_cancel)
        self.Bind(wx.EVT_SIZE, self.size_frame, id=-1)
        ############################################################################################
        entries = [wx.AcceleratorEntry() for i in range(5)]
        entries[0].Set(wx.ACCEL_NORMAL, wx.WXK_F3, self.button_0.GetId())
        entries[1].Set(wx.ACCEL_NORMAL, wx.WXK_TAB, self.button_1.GetId())
        entries[2].Set(wx.ACCEL_CTRL, ord("L"), self.button_2.GetId())
        entries[3].Set(wx.ACCEL_CTRL, ord("I"), self.button_3.GetId())
        entries[4].Set(wx.ACCEL_SHIFT, ord("C"), self.button_add.GetId())
        accel_tbl = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel_tbl)        
        ############################################################################################
        
        self.wdict = Dictionaries().dict_fromFile(self.dname, "=>")
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
            logger.debug("Iterator was empty")
        finally:
            p = "="*20
            self.text_3.SetValue(f"{p}\nEnd of subtitles reached\n{p}")
        try:
            t1 = list(set(r1.findall(sub.content)))
            newd = {}
            self.text_1.Clear()
            for i in range(len(t1)):
                self.text_1.AppendText(f"{t1[i]} ")
                v = wdict[t1[i]]
                newd[t1[i]] = v
            for k, v in newd.items():
                ctext = re.compile(r'\b'+k+r'\b')
                sub.content = ctext.sub(v, sub.content)
            self.text_3.SetValue(sub.content)
            self.text_3.SetFocus()
            for v in newd.values():
                self.textStyle(self.text_3, sub.content, "RED", "", v)
            if t1:
                changed = Subtitle(sub.index, sub.start, sub.end, sub.content)
                self.Replaced.append(changed)
                for v in newd.values(): self.ReplacedAll.append(v)
                self.new_d = newd
            else:
                self.text_2.AppendText(self.composeSub(sub))
            return c
        except Exception as e:
            logger.debug(f"Error: {e}")
            
    def composeSub(self, sub):
        """"""
        start = srt.timedelta_to_srt_timestamp(sub.start)
        end = srt.timedelta_to_srt_timestamp(sub.end)
        return f"{sub.index}\n{start} --> {end}\n{sub.content}\n\n"
        
    def FileChanged(self, event):
        """"""
        self.filePicker.SetPath(self.filePicker.GetPath())
        self.dname = self.filePicker.GetPath()
        wdict = Dictionaries().dict_fromFile(self.dname, "=>")
        self.subs = srt.parse(self.default_subs)
        self.wdict = self.clearDict(wdict, srt.compose(self.subs, reindex=False))
        self.text_2.Clear()
        self.Replaced.clear()
        self.onReplace(event)
        event.Skip()

    def textStyle(self, tctrl, text, st1, st2, w=r""):
        """"""
        x = re.compile(r"\b"+w+r"\b")
        for m in re.finditer(x, text):
            tctrl.SetStyle(m.start(), m.end(), wx.TextAttr(st1, st2))
            
    def replaceCurrent(self):
        """"""
        if self.Replaced:
            text = self.text_3.GetValue()
            sub = self.Replaced[0]
            changed = Subtitle(sub.index, sub.start, sub.end, text)
            self.text_2.AppendText(self.composeSub(changed))
            self.Replaced.clear()
            self.new_subs.append(changed)
            self.default_subs = self.GetText()
            
    def onReplace(self, event):
        ''''''
        self.replaceCurrent()
        while not self.Replaced:
            c = self.getValues(self.subs)
            if c is None or not c:
                break
        for x in set(self.ReplacedAll):
            self.textStyle(self.text_2, self.text_2.GetValue(), "RED", "YELLOW", x)
        self.text_3.SetInsertionPointEnd()
        self.text_2.SetFocus()
        self.text_3.SetFocus()
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

    def getReplaced(self):
        """"""
        return self.ReplacedAll
    
    def onOK(self, event):
        """"""
        current_text = self.GetText()
        WORK_TEXT.truncate(0)
        WORK_TEXT.write(current_text)
        WORK_TEXT.seek(0)
        self.EndModal(True)
        self.Destroy()
    
    def onIgnore(self, event):
        ''''''
        for i in self.text_1.GetValue().split():
            self.Ignored.append(i.strip())
        self.Replaced.clear()
        self.onReplace(event)
        event.Skip()

    def onIgnoreAll(self, event):
        try:
            for i in self.text_1.GetValue().split():
                self.Ignored.append(i.strip())
            for k in set(self.Ignored):
                self.wdict.pop(k)
        except (KeyError, Exception) as e:
            logger.debug(f"IgnoreAll: {e}")
        self.Replaced.clear()
        self.onReplace(event)        
        event.Skip()
    
    def clearDict(self, _dict, _subs):
        """
        Filters a dictionary to include only the keys found in the given subtitles string.
        Parameters:
            _dict (dict): The dictionary to filter.
            _subs (str): The string of subtitles to search for dictionary keys.
        Returns:
            dict: A new dictionary containing only the key-value pairs where keys were found in the subtitles.
        """
        filtered_dict = {}

        # Compile the regex pattern to find keys in the subtitles
        pattern = re.compile(
                r"\b(" + "|".join(map(re.escape, _dict.keys())) + r")\b"
            )

        # Find all matches of dictionary keys in the subtitles
        matches = pattern.findall(_subs)

        # Create a new dictionary with only the matched keys
        for match in matches:
            if match in _dict:
                filtered_dict[match] = _dict[match]

        # Parse the default subtitles
        try:
            self.subs = srt.parse(self.default_subs, ignore_errors=True)
        except Exception as e:
            logger.debug(f"Error parsing subtitles: {e}")
            self.subs = None

        return filtered_dict    
    
    def GetText(self):
        """"""
        n_subs = list(srt.parse(self.text_2.GetValue(), True))
        d_subs = list(srt.parse(self.default_subs, True))
        for x in self.new_subs:
            for i in d_subs:
                if i.index == x.index and i.content != x.content:
                    d_subs[d_subs.index(i)] = x
        for x in n_subs:
            for i in d_subs:
                if i.index == x.index and i.content != x.content:
                    d_subs[d_subs.index(i)] = x        
        return srt.compose(d_subs)
    
    def Text1(self, event):
        """"""
        self.find = []
        t_end = len(self.text_2.GetValue())
        self.text_2.SetStyle(0, t_end, self.text_2.GetDefaultStyle())
        event.Skip()
        
    def onFind(self, event):
        """"""
        if not self.find:
            s = self.text_1.GetValue()
            text2 = self.text_2.GetValue()
            new = [(m.start(), m.end()) for m in re.finditer(re.compile(r"\b"+s+r"\b"), text2)]
            self.find=iter(new)
        try:
            p = next(self.find)
            self.text_2.SetStyle(p[0], p[1], wx.TextAttr("BLACK", "LIGHT BLUE"))
            self.text_2.SetInsertionPoint(p[1])
        except StopIteration:
            logger.debug("Iterator exhausted")
            self.find = []
        event.Skip()
    

    def addSelected(self, event):
        '''button_add event'''
        p = self.text_3.GetSelection()
        if p[0] is p[1]:
            wx.MessageBox(
                f"ValueError\n\n" f"Ništa nije selektovano",
                "Interactive Replace")
        else:
            text = self.text_3.GetValue()[p[0] : p[1]]
            self.text_ADD.SetValue(f"{text}=>")
            self.text_ADD.SetFocus()
            self.text_ADD.SetInsertionPointEnd()
        event.Skip()

    def textAdded(self, event):
        '''EVT_TEXT text.aADD'''
        if self.text_ADD.IsModified():
            self.textStyle(self.text_ADD, self.text_ADD.GetValue(), "GREY","","=>")
            self.button_dict.Enable()
            self.button_cancel.Enable()
        event.Skip()
        
    def addOK(self, event):
        '''Button_dict event'''
        current_dict = self.filePicker.GetPath()
        with open(current_dict, "a", encoding="utf-8") as dict_file:
            dict_file.write(f"\n{self.text_ADD.GetValue().strip()}")
        self.text_ADD.Clear()
        self.button_dict.Enable(False)
        self.button_cancel.Enable(False)
        self.text_3.SetFocus()
        event.Skip()

    def addCANCEL(self, event):
        '''Button event'''
        self.text_ADD.Clear()
        self.button_dict.Enable(False)
        self.button_cancel.Enable(False)
        self.text_3.SetFocus()
        event.Skip()
        
    def size_frame(self, event):
        """"""
        width, height = event.GetSize()
        MAIN_SETTINGS["ChoiceDialog"] = {"W": width, "H": height}
        event.Skip()    
        
    
class MyApp(wx.App):
    def OnInit(self):
        self.dialog = FindReplace(None, wx.ID_ANY)
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
