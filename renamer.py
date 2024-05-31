#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.1.0pre
# Modified by padovaSR

import os
import re
import shutil
import json
from os.path import basename, join, dirname, split, splitext, normpath
import wx


from settings import FILE_SETTINGS, settings_file

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
            
class CollectFiles:
    """"""
    RP = re.compile(r"\d{4}\w?\.?|(x|h)\.?26(4|5)|N(10|265)|ddp5\.1\.?|\b\w{2,}\b(?<!\d)|[ \.-]|(ION\d{2,3})|(?<=part[.\- ])\d+|s\d\d?e", re.I)
    
    subtitles = []
    def __init__(self, selected_folder=None):
        self.selected_folder = selected_folder
        
    def listFiles(self, ext):
        """"""
        folderIn = self.selected_folder
        subs_list = []
        vids_list = []
        self.subtitles.clear()
        with os.scandir(folderIn) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    if entry.name.lower().endswith(ext):
                        subs_list.append(entry.name)
                    if entry.name.lower().endswith((".mp4", ".mkv", ".avi")):
                        vids_list.append(entry.name)
            if not vids_list or not subs_list:
                dlg = wx.RichMessageDialog(
                    None,
                    "Missing File\n\nUnable to find video files.\nFile required as reference.",
                    "Renamer",
                    style=wx.OK,
                )
                if dlg.ShowModal() == wx.ID_OK:
                    dlg.Destroy()                
        return subs_list, vids_list    
    
    def reorderFiles(self, subs=[], vids=[]):
        """"""
        new_subs_list = []
        new_vids_list = []
        try:
            if len(subs) > 1 and len(vids) > 1:
                for pair in zip(subs, vids):
                    a = int(re.match(r"\d{1,2}", self.RP.sub("", pair[0])).group(0))
                    b = int(re.match(r"\d{1,2}", self.RP.sub("", pair[1])).group(0))
                    a = max(0, a - 1)
                    b = max(0, b - 1)
                    
                    # Extend the lists if necessary
                    while len(new_subs_list) <= a:
                        new_subs_list.append(None)
                    while len(new_vids_list) <= b:
                        new_vids_list.append(None)
                    while len(self.subtitles) <= a:
                        self.subtitles.append(None)
                
                    # Insert elements into new lists
                    new_subs_list[a] = pair[0]
                    new_vids_list[b] = pair[1]
                    self.subtitles[a] = normpath(join(self.selected_folder, pair[0]))
                # Remove trailing None elements
                new_subs_list = [x for x in new_subs_list if x is not None]
                new_vids_list = [x for x in new_vids_list if x is not None]
                self.subtitles = [x for x in self.subtitles if x is not None]
            else:
                new_subs_list = subs
                new_vids_list = vids
                self.subtitles.append(normpath(join(self.selected_folder, subs[0])))
        except Exception as e:
            logger.debug(f"reorderFiles: {e}")
        return new_subs_list,new_vids_list


class RenameFiles(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=u"Renamer",
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
            width = FILE_SETTINGS["Renamer"]["W"]
            height = FILE_SETTINGS["Renamer"]["H"]
            self.SetSize(width, height)
        except:
            self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        Sizer1 = wx.BoxSizer(wx.VERTICAL)

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
        self.Label_1.SetLabel(f"\u2009{os.path.basename(self.get_current_user())}")

        Sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.splitter_pos = FILE_SETTINGS["Renamer"]["splitter"]
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
            selected_directory = FILE_SETTINGS["Renamer"]["Selected"]
        except:
            selected_directory = self.get_current_user()
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
        
        self.m_textCtrl1 = wx.TextCtrl(
            self.panel2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_RICH2,
        )
        self.m_textCtrl1.DragAcceptFiles(True)
        Sizer4.Add(self.m_textCtrl1, 1, wx.EXPAND | wx.RIGHT | wx.TOP, 5)
        
        self.m_textCtrl2 = wx.TextCtrl(
            self.panel2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_RICH2,
        )
        Sizer4.Add(self.m_textCtrl2, 1, wx.BOTTOM | wx.EXPAND | wx.RIGHT | wx.TOP, 5)

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
                selected_directory,
                wx.DefaultPosition,
                wx.DefaultSize,
                wx.ALIGN_LEFT,
            )
        self.Label_2.Wrap(-1)
    
        self.Label_2.SetFont(
                wx.Font(
                    10,
                    wx.FONTFAMILY_SWISS,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL,
                    False,
                    "Franklin Gothic Medium",
                )
            )        
        Sizer5 = wx.StdDialogButtonSizer()
        Sizer5.Add(self.Label_2, 0, wx.LEFT, 5)
        self.Sizer5_OK = wx.Button(self, wx.ID_OK)
        Sizer5.AddButton(self.Sizer5_OK)
        self.Sizer5_Cancel = wx.Button(self, wx.ID_CANCEL)
        Sizer5.AddButton(self.Sizer5_Cancel)
        Sizer5.Realize()

        Sizer1.Add(Sizer5, 0, wx.BOTTOM | wx.EXPAND | wx.RIGHT, 5)

        self.SetSizer(Sizer1)
        self.Layout()

        self.Centre(wx.BOTH)
        
        self.current_path = None
        self.suffix = ".srt"
        self.vid_suffix = ".mkv"
    
        self.subtitles = []
        self.renamed = []
        
        # Set the drop target only for the first text control
        drop_target = MyFileDropTarget(self.m_textCtrl1, self)
        self.m_textCtrl1.SetDropTarget(drop_target)
        
        # Ensure the second text control does not accept drops
        self.m_textCtrl2.SetDropTarget(None)        

        # Connect Events
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag, self.genericDirCtrl.GetTreeCtrl())
        self.splitter1.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.GetsplitterPosition)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onFileActivated, self.genericDirCtrl.GetTreeCtrl())
        self.Sizer5_Cancel.Bind(wx.EVT_BUTTON, self.onCancel)
        self.Sizer5_OK.Bind(wx.EVT_BUTTON, self.renameFiles)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def set_splitter_position(self):
        self.splitter1.SetSashPosition(self.splitter_pos)    
    
    def GetsplitterPosition(self, event):
        self.splitter_pos = self.splitter1.GetSashPosition()
        event.Skip()
        
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
            self.Label_2.SetLabel(f"{path}")
            self.getNames()            
                
    def onFileActivated(self, event):
        item = event.GetItem()
        path = self.genericDirCtrl.GetPath(item)
        if os.path.isdir(path):
            self.current_path = path
            self.Label_2.SetLabel(f"{path}")
            self.getNames()
        event.Skip()
    
    def get_current_user(self):
        try:
            user_home = os.path.expanduser("~")
            return user_home
        except Exception:
            return "Unknown"        
    
    def getNames(self):
        self.m_textCtrl1.Clear()
        self.m_textCtrl2.Clear()
        collector = CollectFiles(self.current_path)
        title_list,video_list = collector.listFiles(self.suffix)        
        try:
            new_subs_list,new_vids_list = collector.reorderFiles(title_list, video_list)
            self.vid_suffix = splitext(video_list[0])[1]
            self.subtitles = collector.subtitles
            renamed_subs_list = [splitext(filename)[0] + ".srt" for filename in new_vids_list]
        
            for title_name in new_subs_list:
                self.m_textCtrl1.AppendText(f"{title_name}\n")
            for file_name in renamed_subs_list:
                self.m_textCtrl2.AppendText(f"{file_name}\n")
        except Exception as e:
            logger.debug(f"getNames: {e}")        
    
    def renameFiles(self, event):
        ''''''
        renamed = self.renamed
        renamed.clear()
        n = self.m_textCtrl2.GetNumberOfLines()
        if n > 2:
            pl_name = f"{split(dirname(self.subtitles[0]))[1]}.m3u"
            pl_file = join(dirname(self.subtitles[0]), pl_name)
            with open(pl_file, "w", encoding="utf-8") as f:
                f.write(f"#{basename(pl_file)[:-4]} Playlist\n")            
        for i in range(0, n):
            try:
                line = self.m_textCtrl2.GetLineText(i)
                new_name = join(os.path.dirname(self.subtitles[i]), line)
                shutil.move(self.subtitles[i], new_name)
                renamed.append(f"{line}\n")
                if n > 2:
                    with open(pl_file, "a", encoding="utf-8") as f:
                        f.write(f"{splitext(line)[0]}{self.vid_suffix}\n")                
                logger.debug(f"{basename(self.subtitles[i])} -> {line}")
            except Exception as e:
                logger.debug(f"{e}")
        self.subtitles.clear()
        self.writeSettings()
        self.checkRenamed()
        event.Skip()
        
    def checkRenamed(self):
        """"""
        collector = CollectFiles(self.current_path)
        s_list, v = collector.listFiles(self.suffix)        
        renamed = [item.strip() for item in self.renamed]
        if s_list and renamed:
            try:
                if len(s_list) == len(renamed) and set(s_list) == set(renamed):
                    return [item + "\n" for item in s_list]
            except (TypeError, Exception) as e:
                logger.debug(f"Error: {e}")    
    
    def writeSettings(self):
        """"""
        # Get current directory and the size of the frame 
        size = self.GetSize()
        width = size.GetWidth()
        height = size.GetHeight()
        current_dir = self.Label_2.GetLabel()
        if not os.path.exists(current_dir):
            try:
                current_dir = dirname(current_dir)
            except:
                current_dir = self.get_current_user()
        # Update the FILE_SETTINGS dictionary
        FILE_SETTINGS["Renamer"] = {"W": width, "H": height, "splitter": self.splitter_pos, "Selected": current_dir}
        
    def onCancel(self, event):
        self.writeSettings()
        self.Destroy()
        event.Skip()
        
    def onClose(self, event):
        self.writeSettings()
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        self.dialog = RenameFiles(None)
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        #self.dialog.Destroy()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
