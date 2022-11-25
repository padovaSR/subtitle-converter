#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  generated by wxGlade 0.9.9pre; modified by padovaSR
#
#  Copyright (C) 2020  padovaSR
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import wx
from os.path import join, basename, dirname 
import logging.config

logger = logging.getLogger(__name__)


class TreeDialog(wx.Dialog):
    def __init__(self, parent, caption, root_name, files=[]):
        wx.Dialog.__init__(
            self, parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.files = files
        self.caption = caption
        self.root_name = root_name
        
        self.SetSize((439, 434))
        self.SetTitle(self.caption)
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(
            wx.Bitmap(
                join("resources", "icons", "subConvert.ico"), wx.BITMAP_TYPE_ANY
            )
        )
        self.SetIcon(_icon)
        self.SetFocus()

        szr_1 = wx.BoxSizer(wx.VERTICAL)

        szr_3 = wx.FlexGridSizer(1, 5, 0, 0)
        szr_1.Add(szr_3, 0, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)

        self.label_1 = wx.StaticText(self, wx.ID_ANY, "Selekcija ", style=wx.ALIGN_LEFT)
        self.label_1.SetFont(
            wx.Font(
                8,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_ITALIC,
                wx.FONTWEIGHT_BOLD,
                0,
                "Segoe UI",
            )
        )
        szr_3.Add(self.label_1, 1, wx.ALL | wx.EXPAND, 5)

        self.chbox_1 = wx.CheckBox(self, wx.ID_ANY, "Cyr-ansi", style=wx.CHK_2STATE)
        self.chbox_1.SetValue(1)
        szr_3.Add(self.chbox_1, 0, wx.ALIGN_BOTTOM | wx.ALL, 5)

        self.chbox_2 = wx.CheckBox(self, wx.ID_ANY, "Cyr-utf8", style=wx.CHK_2STATE)
        self.chbox_2.SetValue(1)
        szr_3.Add(self.chbox_2, 0, wx.ALL | wx.EXPAND, 5)

        self.chbox_3 = wx.CheckBox(self, wx.ID_ANY, "Lat-ansi", style=wx.CHK_2STATE)
        self.chbox_3.SetValue(1)
        szr_3.Add(self.chbox_3, 0, wx.ALL | wx.EXPAND, 5)

        self.chbox_4 = wx.CheckBox(self, wx.ID_ANY, "Lat-utf8", style=wx.CHK_2STATE)
        self.chbox_4.SetValue(1)
        szr_3.Add(self.chbox_4, 0, wx.ALL | wx.EXPAND, 5)

        # tID = wx.NewIdRef()
        self.tree = wx.TreeCtrl(self, wx.ID_ANY)

        self.tree.SetMinSize((315, 200))
        self.tree.SetToolTip("Struktura foldera")
        szr_1.Add(self.tree, 1, wx.ALL | wx.EXPAND | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 5)

        szr_2 = wx.BoxSizer(wx.HORIZONTAL)
        szr_1.Add(szr_2, 0, wx.BOTTOM | wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.checkbox_1 = wx.CheckBox(
            self, wx.ID_ANY, "Kreiraj foldere", style=wx.CHK_2STATE
        )
        self.checkbox_1.SetValue(1)
        szr_2.Add(
            self.checkbox_1,
            1,
            wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP,
            5,
        )

        szr_2.Add((20, 20), 1, wx.ALIGN_CENTER_VERTICAL, 0)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        szr_2.Add(
            self.button_OK,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP,
            5,
        )

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        szr_2.Add(
            self.button_CANCEL,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.RIGHT | wx.TOP,
            5,
        )

        self.SetSizer(szr_1)
        szr_1.SetSizeHints(self)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.onQuit, self.button_CANCEL)
        self.Bind(wx.EVT_CLOSE, self.onCancel, id=-1)
        self.Bind(wx.EVT_CHECKBOX, self.rebuildItems, id=-1)
        # end wxGlade

        isz = (16, 16)
        il = wx.ImageList(*isz)
        self.fldrix = il.Add(
            wx.Bitmap(
                join("resources", "icons", "a-zip-icon.png"), wx.BITMAP_TYPE_ANY
            )
        )
        self.fldridx = il.Add(
            wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz)
        )
        self.fldropenidx = il.Add(
            wx.ArtProvider.GetIcon(wx.ART_FOLDER_OPEN, wx.ART_OTHER, isz)
        )
        self.fileidx = il.Add(
            wx.ArtProvider.GetIcon(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz)
        )
        self.tree.SetImageList(il)
        self.il = il

        self.root = self.tree.AddRoot(self.root_name, self.fldrix, self.fldrix)

        self.items = self.buildItems()

    def buildItems(self):
        """"""
        logger.debug("Building TreeItems")
        return [self.makeMenu(x) for x in self.files]

    def makeMenu(self, items=[]):
        """"""
        if self.checkbox_1.IsChecked():
            l = [dirname(x) for x in items]
            fItems = sorted(set(l), key=l.index)
            cItems = [self.tree.AppendItem(self.root, x) for x in fItems]
            for i in items:
                a = dirname(i)
                b = basename(i)
                for x in range(len(fItems)):
                    if a == fItems[x]:
                        lfile = self.tree.AppendItem(cItems[x], b)
                        self.tree.SetItemImage(lfile, self.fileidx, wx.TreeItemIcon_Normal)
            for i in cItems:
                self.tree.SetItemImage(i, self.fldridx, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(i, self.fldropenidx, wx.TreeItemIcon_Expanded)
            self.tree.Expand(self.root)
            return cItems
        else:
            fItems = []
            cItems = []
            fItems.append(items)
            for x in fItems:
                for i in range(len(x)):
                    cItems.append(self.tree.AppendItem(self.root, basename(x[i])))
            for i in cItems:
                self.tree.SetItemImage(i, self.fileidx, wx.TreeItemIcon_Normal)
            return cItems
        
    def makeFolder(self):
        """"""
        return self.checkbox_1.IsChecked()

    def GetSelections(self):
        """"""
        t = [self.chbox_1, self.chbox_2, self.chbox_3, self.chbox_4]
        return [t.index(x) for x in t if x.IsChecked()]

    def rebuildItems(self, event):
        ''''''
        self.tree.DeleteChildren(self.root)
        makef = [self.files[x] for x in self.GetSelections()]
        self.items = [self.makeMenu(x) for x in makef]
        event.Skip()

    def onCancel(self, event):
        self.Destroy()

    def onQuit(self, event):
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        self.dialog = TreeDialog(None, wx.ID_ANY, "", "")
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
