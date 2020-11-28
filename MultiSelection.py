#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.0.0a9; modified by padovaSR
#
import os
from pathlib import Path, PurePath

import wx



class MultiFiles(wx.Dialog):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.SetSize((560, 498))
        
        self.SetTitle("Select Files")
        
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(os.path.join("resources","icons","system-run.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        self.choices = ["Title_Sample1.srt", "Sample_2.srt", "Title_3.srt"]
        
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.sizer_3 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_1.Add(self.sizer_3, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Select directory")
        self.sizer_3.Add(label_1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
        
        self.dp0 = wx.DirPickerCtrl(self, style=wx.DIRP_USE_TEXTCTRL)
        self.dp0.SetTextCtrlProportion(2)
        self.sizer_3.Add(self.dp0, 0, wx.ALL|wx.EXPAND, 6)
        
        self.sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_3.Add(self.sizer_4, 0, wx.EXPAND, 0)

        self.checkbox_1 = wx.CheckBox(self, wx.ID_ANY, "*.srt", style=wx.CHK_2STATE)
        self.checkbox_1.SetValue(1)
        self.sizer_4.Add(self.checkbox_1, 0, wx.ALL, 6)

        self.checkbox_2 = wx.CheckBox(self, wx.ID_ANY, "*.sub", style=wx.CHK_2STATE)
        self.sizer_4.Add(self.checkbox_2, 0, wx.ALL, 6)

        self.checkbox_3 = wx.CheckBox(self, wx.ID_ANY, "*.txt", style=wx.CHK_2STATE)
        self.sizer_4.Add(self.checkbox_3, 0, wx.ALL, 6)
        
        self.checkbox_6 = wx.CheckBox(self, wx.ID_ANY, "*.zip", style=wx.CHK_2STATE)
        self.sizer_4.Add(self.checkbox_6, 0, wx.ALL, 6)

        self.checkbox_4 = wx.CheckBox(self, wx.ID_ANY, "*.* All Files", style=wx.CHK_2STATE)
        self.sizer_4.Add(self.checkbox_4, 0, wx.ALL, 6)
        
        self.checkbox_5 = wx.CheckBox(self, wx.ID_ANY, "Scan Subfolders", style=wx.CHK_2STATE)
        self.checkbox_5.SetValue(1)
        self.sizer_4.Add(self.checkbox_5, 0, wx.ALL, 6)

        self.list_box = wx.CheckListBox(self, wx.ID_ANY, choices=self.choices, style=wx.LB_EXTENDED)
        self.sizer_3.Add(self.list_box, 1, wx.LEFT|wx.RIGHT|wx.TOP | wx.EXPAND, 6)

        sizer_2 = wx.StdDialogButtonSizer()
        self.sizer_1.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 6)
        
        self.select_all = wx.CheckBox(self, wx.ID_ANY, "Select all", style=wx.CHK_2STATE)
        sizer_2.Add(self.select_all, 0, wx.ALIGN_CENTER_VERTICAL| wx.LEFT, 0)
        
        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(self.sizer_1)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
        self.Centre()
        
        self.path = None
        self.checkBoxList = [self.checkbox_1, self.checkbox_2, self.checkbox_3, self.checkbox_6]
        
        self.Bind(wx.EVT_DIRPICKER_CHANGED, self.OnPickFileDir, self.dp0)
        self.Bind(wx.EVT_CHECKBOX, self.OnPickFileDir, self.checkbox_5)
        self.Bind(wx.EVT_CHECKBOX, self.EvtChBox, self.select_all)
        self.Bind(wx.EVT_CHECKBOX, self.disableCheckBox, self.checkbox_4)
        self.Bind(wx.EVT_CLOSE, self.onCancel, self.button_CANCEL)
        for e in self.checkBoxList: self.Bind(wx.EVT_CHECKBOX, self.disableCheckBox, e)
        
        
    def OnPickFileDir(self, event):
        ''''''
        if event.Id == self.dp0.Id: self.path = event.GetPath()
        self.choices.clear()
        if self.path:
            files = Path(self.path).iterdir()    ## List of files only
            for x in files:
                if x.is_file(): self.choices.append(str(x))
                else:
                    if self.checkbox_5.IsChecked():
                        sfiles = Path(x).iterdir()
                        for file in sfiles:
                            if file.is_file():
                                self.choices.append(str(file))
                            else:
                                dfiles = Path(file).iterdir()
                                for f in dfiles:
                                    if f.is_file(): self.choices.append(str(f))
        self.populateListBox()
        self.button_OK.SetFocus()
        event.Skip()
        
    def getSuffix(self, infile):
        return PurePath.suffix(infile)
    
    def populateListBox(self):
        self.list_box.Clear()
        self.list_box.InsertItems(self.choices, 0)
        
    def GetSelections(self):
        return self.list_box.GetSelections()

    def EvtChBox(self, event):
        state = self.select_all.IsChecked()
        for i in range(self.list_box.GetCount()):
            self.list_box.Check(i, state)
        event.Skip()
    
    def disableCheckBox(self, event):
        ''''''
        if event.Id == self.checkbox_4.Id:
            if self.checkbox_4.IsChecked():
                for c in self.checkBoxList:
                    c.SetValue(0)
        else:
            if any(x.IsChecked() for x in self.checkBoxList):
                self.checkbox_4.SetValue(0)
        event.Skip()
    
    def onCancel(self, event):
        self.Destroy()
        
        
class MyApp(wx.App):
    def OnInit(self):
        self.dialog = MultiFiles(None, wx.ID_ANY)
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
