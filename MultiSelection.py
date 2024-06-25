#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.1.0pre
# Modified by padovaSR

#import sys
import os
from os.path import join, splitext, normpath
import wx

from settings import FILE_SETTINGS

import logging.config
logger = logging.getLogger(__name__)

class MyFileDropTarget(wx.TextDropTarget):
    def __init__(self, text_ctrl, dialog):
        wx.TextDropTarget.__init__(self)
        self.text_ctrl = text_ctrl
        self.dialog = dialog

    def OnDropText(self, x, y, data):
        self.dialog.folder_path = data  # Store the path in the dialog
        self.dialog.OnFolderDropped(data)  # Handle the dropped folder
        return True

class MultiFiles(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="Select files",
            pos=wx.DefaultPosition,
            style=wx.CLOSE_BOX
            | wx.DEFAULT_DIALOG_STYLE
            | wx.MAXIMIZE_BOX
            | wx.MINIMIZE_BOX
            | wx.RESIZE_BORDER,
        )
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(
            wx.Bitmap(join("resources","icons","icon_d.png"), wx.BITMAP_TYPE_ANY)
        )
        self.SetIcon(_icon)        
        try:
            width = FILE_SETTINGS["MultiFiles"]["W"]
            height = FILE_SETTINGS["MultiFiles"]["H"]
            self.SetSize(width, height)
        except:
            self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
            
        self.choices = []

        Sizer1 = wx.BoxSizer(wx.VERTICAL)
        Sizer_top = wx.BoxSizer(wx.HORIZONTAL)

        self.Label_1 = wx.StaticText(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_LEFT,
        )
        self.Label_1.Wrap(-1)

        self.Label_1.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Franklin Gothic Medium",
            )
        )
        Sizer1.Add(self.Label_1, 0, wx.EXPAND|wx.LEFT|wx.TOP, 5)
        #self.Label_1.SetLabel(f"\u2009{self.get_current_user()}")

        self.checkbox_5 = wx.CheckBox(self, wx.ID_ANY, "Skeniraj subfoldere", style=wx.CHK_2STATE)
        self.checkbox_5.SetValue(0)
        Sizer_top.Add((2, 10), 0, wx.EXPAND, 0)
        Sizer_top.Add(self.checkbox_5, 0, wx.ALL, 5)
        
        self.checkbox_1 = wx.CheckBox(self, wx.ID_ANY, "*.srt", style=wx.CHK_2STATE)
        self.checkbox_1.SetValue(1)
        Sizer_top.Add(self.checkbox_1, 0, wx.ALL, 6)

        self.checkbox_2 = wx.CheckBox(self, wx.ID_ANY, "*.sub", style=wx.CHK_2STATE)
        Sizer_top.Add(self.checkbox_2, 0, wx.ALL, 6)

        self.checkbox_3 = wx.CheckBox(self, wx.ID_ANY, "*.txt", style=wx.CHK_2STATE)
        Sizer_top.Add(self.checkbox_3, 0, wx.ALL, 6)

        self.checkbox_4 = wx.CheckBox(self, wx.ID_ANY, "*.zip", style=wx.CHK_2STATE)
        Sizer_top.Add(self.checkbox_4, 0, wx.ALL, 6)
        
        Sizer1.Add(Sizer_top, 0, wx.EXPAND)

        Sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        try:
            self.splitter_pos = FILE_SETTINGS["MultiFiles"]["splitter"]
        except:
            self.splitter_pos = 237
        self.splitter1 = wx.SplitterWindow(
            self, wx.ID_ANY, style=wx.SP_3D|wx.SP_3DSASH|wx.SP_LIVE_UPDATE
        )
        self.splitter1.SetSashGravity(0.3)
        
        self.panel1 = wx.Panel(
            self.splitter1,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL,
        )
        Sizer3 = wx.BoxSizer(wx.VERTICAL)
        try:
            selected_directory = FILE_SETTINGS["MultiFiles"]["Selected"]
        except:
            selected_directory = self.get_current_user()
        self.Label_1.SetLabel(f"{selected_directory}")
        self.genericDirCtrl = wx.GenericDirCtrl(
            self.panel1,
            wx.ID_ANY,
            selected_directory,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.DIRCTRL_3D_INTERNAL | wx.DIRCTRL_DIR_ONLY | wx.FULL_REPAINT_ON_RESIZE,
            u"Srt files(*.srt)|*.srt|All files (*.*)|*.*",
            0,
        )

        self.genericDirCtrl.ShowHidden(False)
        Sizer3.Add(self.genericDirCtrl, 1, wx.EXPAND | wx.ALL, 5)

        self.panel1.SetSizer(Sizer3)
        self.panel1.Layout()
        Sizer3.Fit(self.panel1)
        self.panel2 = wx.Panel(
            self.splitter1,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL,
        )
        Sizer4 = wx.BoxSizer(wx.VERTICAL)

        self.list_box = wx.CheckListBox(
            self.panel2, wx.ID_ANY, choices=self.choices, style=wx.LB_EXTENDED
        )        
        self.list_box.SetToolTip("Drag and drop directory here")
        self.list_box.DragAcceptFiles(True)
        
        Sizer4.Add(self.list_box, 1, wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM, 5)

        self.panel2.SetSizer(Sizer4)
        self.panel2.Layout()
        Sizer4.Fit(self.panel2)
        self.splitter1.SplitVertically(self.panel1, self.panel2, 260)
        Sizer2.Add(self.splitter1, 1, wx.EXPAND, 5)
        
        # Set the position of the splitter
        wx.CallAfter(self.set_splitter_position)
        
        Sizer1.Add(Sizer2, 1, wx.EXPAND, 5)

        self.Label_2 = wx.StaticText(
            self,
                wx.ID_ANY,
                f"Broj fajlova: {self.list_box.GetCount()} ",
                wx.DefaultPosition,
                wx.DefaultSize,
                wx.ALIGN_LEFT,
        )
        self.Label_2.Wrap(-1)
        
        self.Label_3 = wx.StaticText(
            self,
                wx.ID_ANY,
                f"Selektovanih fajlova: {self.list_box.GetCount()} ",
                wx.DefaultPosition,
                wx.DefaultSize,
                wx.ALIGN_LEFT,
        )
        self.Label_2.Wrap(-1)        

        self.select_all = wx.CheckBox(
            self, wx.ID_ANY, "Selektuj sve", style=wx.CHK_2STATE
        )        
        Sizer5 = wx.StdDialogButtonSizer()
        Sizer5.Add((2, 10), 0, wx.EXPAND, 0)
        Sizer5.Add(self.select_all, 0, wx.LEFT, 5)
        Sizer5.Add((100, 10), 0, wx.EXPAND, 5)
        Sizer5.Add(self.Label_2, 0, wx.LEFT, 5)
        Sizer5.Add((100, 10), 0, wx.EXPAND, 0)
        Sizer5.Add(self.Label_3, 0, wx.LEFT, 5)
        Sizer5.AddStretchSpacer(1)
        self.Sizer5_OK = wx.Button(self, wx.ID_OK)
        Sizer5.AddButton(self.Sizer5_OK)
        self.Sizer5_Cancel = wx.Button(self, wx.ID_CANCEL)
        Sizer5.AddButton(self.Sizer5_Cancel)
        Sizer5.Realize()

        Sizer1.Add(Sizer5, 0, wx.BOTTOM | wx.EXPAND | wx.RIGHT, 5)

        self.SetSizer(Sizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # Set the drop target only for the first text control
        drop_target = MyFileDropTarget(self.list_box, self)
        self.list_box.SetDropTarget(drop_target)

        self.current_path = selected_directory
        self.SF = {}
        self.checkBoxList = [
                self.checkbox_1,
                self.checkbox_2,
                self.checkbox_3,
                self.checkbox_4
            ]
        self.sEntry = {
                self.checkbox_1: ".srt",
                self.checkbox_2: ".sub",
                self.checkbox_3: ".txt",
                self.checkbox_4: ".zip",
            }        
        
        # Connect Events
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag, self.genericDirCtrl.GetTreeCtrl())
        self.splitter1.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.GetsplitterPosition)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onFileActivated, self.genericDirCtrl.GetTreeCtrl())
        self.Bind(wx.EVT_CHECKBOX, self.populate_list, self.checkbox_5)
        self.Bind(wx.EVT_CHECKBOX, self.disableCheckBox, self.checkbox_5)
        self.list_box.Bind(wx.EVT_CHECKLISTBOX, self.on_item_checked)
        self.select_all.Bind(wx.EVT_CHECKLISTBOX, self.on_item_checked)
        self.select_all.Bind(wx.EVT_CHECKBOX, self.on_select_all)
        self.Sizer5_Cancel.Bind(wx.EVT_BUTTON, self.onCancel)
        self.Sizer5_OK.Bind(wx.EVT_BUTTON, self.onOK)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        for e in self.checkBoxList:
            self.Bind(wx.EVT_CHECKBOX, self.disableCheckBox, e)        

    def GetsplitterPosition(self, event):
        self.splitter_pos = self.splitter1.GetSashPosition()
        event.Skip()

    def set_splitter_position(self):
        self.splitter1.SetSashPosition(self.splitter_pos)    
    
    def OnBeginDrag(self, event):
        item = event.GetItem()
        tree = self.genericDirCtrl.GetTreeCtrl()
        path = self.genericDirCtrl.GetPath(item)
        
        if os.path.isdir(path):  # Check if the item is a directory
            tdo = wx.TextDataObject(path)
            tds = wx.DropSource(tree)
            tds.SetData(tdo)
            tds.DoDragDrop(True)
        else:
            event.Skip()

    def OnFolderDropped(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.Label_1.SetLabel(path)
            self.getFiles()
            self.list_box.Clear()
            if self.choices:
                self.list_box.InsertItems(self.choices, 0)        
                # Update the selected count label
                self.update_selected_count()            

    def onFileActivated(self, event):
        item = event.GetItem()
        path = self.genericDirCtrl.GetPath(item)
        self.Label_1.SetLabel(path)
        if os.path.isdir(path):
            self.current_path = path
            self.populate_list(event)            
        event.Skip()

    def on_select_all(self, event):
        '''Check or uncheck all items in the CheckListBox based on the state
        of the Select All checkbox'''
        checkbox_state = self.select_all.IsChecked()
        for i in range(self.list_box.GetCount()):
            self.list_box.Check(i, checkbox_state)
        self.update_selected_count()
        event.Skip()

    def on_item_checked(self, event):
        ''''''
        self.update_selected_count()
        event.Skip()

    def update_selected_count(self):
        '''Update the label with the number of selected items'''
        selected_count = sum(
            1 for i in range(self.list_box.GetCount()) if self.list_box.IsChecked(i)
        )
        self.Label_3.SetLabel(f"Selektovanih fajlova: {selected_count}")
        self.Label_2.SetLabel(f"Broj fajlova: {self.list_box.GetCount()}")
        
    def getFiles(self):
        ''''''
        self.SF = [self.sEntry[x] for x in self.checkBoxList if x.IsChecked()]
        self.choices.clear()
        if self.current_path:
            if self.checkbox_5.IsChecked():
                for r, d, sfiles in os.walk(self.current_path):
                    for file in sfiles:
                        current_file = join(r, file)
                        if self.SF and self.getSuffix(current_file) in self.SF:
                            if any(current_file.endswith(x.lower()) for x in self.SF):
                                self.choices.append(current_file)
            else:
                with os.scandir(self.current_path) as files:
                    for x in files:
                        if x.is_file():
                            current_file = join(self.current_path, x)
                            if self.SF and self.getSuffix(current_file) in self.SF:
                                if any(current_file.endswith(x.lower()) for x in self.SF):
                                    self.choices.append(current_file)
            self.Sizer5_OK.SetFocus()
        
    def getSuffix(self, infile):
        return splitext(infile)[-1]    
    
    def GetSelectedFiles(self):
        ''''''
        selections = self.list_box.GetCheckedItems()
        return [self.choices[x] for x in selections]
    
    def disableCheckBox(self, event):
        ''''''
        if event.Id == self.checkbox_5.Id:
            self.select_all.SetValue(0)
        else:
            if any(x.IsChecked() for x in self.checkBoxList):
                self.select_all.SetValue(0)
                self.populate_list(event)
        event.Skip()    
    
    def populate_list(self, event):
        ''''''
        self.getFiles()
        self.list_box.Clear()
        if self.choices:
            self.list_box.InsertItems(self.choices, 0)        
            # Update the selected count label
            self.update_selected_count()
        event.Skip()
        
    def get_current_user(self):
        try:
            return os.path.expanduser("~")
        except Exception:
            return "Unknown"        

    def writeSettings(self):
        """"""
        # Get current directory and the size of the frame 
        size = self.GetSize()
        width = size.GetWidth()
        height = size.GetHeight()
        current_dir = normpath(self.Label_1.GetLabel())
        # Update the MAIN_SETTINGS_SETTINGS dictionary
        FILE_SETTINGS["MultiFiles"] = {"W": width, "H": height, "splitter": self.splitter_pos, "Selected": current_dir}    

    def onCancel(self, event):
        self.writeSettings()
        self.Destroy()
        event.Skip()
        
    def onOK(self, event):
        self.writeSettings()
        #self.Destroy()
        event.Skip()
        
    def onClose(self, event):
        self.writeSettings()
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        self.dialog = MultiFiles(None)
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        #self.dialog.Destroy()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()