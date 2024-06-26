#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre
#
from settings import filePath, FILE_SETTINGS
from TextFileProc import shortcutsKey
import logging.config

import wx

logger = logging.getLogger(__name__)


class ConverterFrame(wx.Frame):
    def __init__(self, *args):
        wx.Frame.__init__(self, *args, style=wx.DEFAULT_FRAME_STYLE)
        try:
            size_dict = FILE_SETTINGS["FrameSize"]
            w = size_dict["W"]
            h = size_dict["H"]
            self.SetSize((w, h))
        except Exception as e:
            logger.debug(f"SetSize error: {e}")
            self.SetSize((622, 573))

        _icon = wx.NullIcon
        _icon.CopyFromBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "subConvert.ico"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.SetIcon(_icon)

        ## Menu Bar ###############################################################################
        keyS = shortcutsKey
        self.menubar1 = wx.MenuBar()
        self.file = wx.Menu()

        self.fopen = wx.MenuItem(
            self.file, wx.ID_OPEN, "&Open\t" + keyS["Open"], "Otvori fajl"
        )
        self.fopen.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU)
        )

        self.file.Append(self.fopen)

        self.file.AppendSeparator()

        self.openMulti = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            "&OpenMultiple..\t"+keyS["OpenMultiple"],
            "Otvori multi_file dijalog",
            wx.ITEM_NORMAL
        )
        self.openMulti.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_MENU))
        self.file.Append(self.openMulti)
        
        self.file.AppendSeparator()
        self.reload = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            "&Reload file\t" + keyS["Reload file"],
            "Ponovo učitaj fajl",
            wx.ITEM_NORMAL,
        )
        self.reload.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "reload.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.file.Append(self.reload)

        self.file.AppendSeparator()

        self.save = wx.MenuItem(
            self.file, wx.ID_SAVE, "&Save\t" + keyS["Save"], "Save file"
        )
        self.save.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU)
        )
        self.file.Append(self.save)

        self.save_as = wx.MenuItem(
            self.file,
            wx.ID_SAVEAS,
            "&Save as\t" + keyS["Save as"],
            "Save as",
        )
        self.save_as.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU)
        )
        self.file.Append(self.save_as)

        self.export_zip = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            "&Export as ZIP\t" + keyS["Export as ZIP"],
            "Export as ZIP",
        )
        self.export_zip.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "zip_file.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.file.Append(self.export_zip)
        self.file.AppendSeparator()
        self.rename_srt = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            "&Rename subtitles\t" + keyS["Rename subtitles"],
            "Mass-rename subtitle files",
        )
        self.rename_srt.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_HELP_SIDE_PANEL, wx.ART_MENU)
        )
        self.file.Append(self.rename_srt)
        self.file.AppendSeparator()

        self.close = wx.MenuItem(
            self.file, wx.ID_CLOSE, "&Close\t" + keyS["Close"], "Close file"
        )
        self.close.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_MENU)
        )
        self.file.Append(self.close)

        self.file.AppendSeparator()

        # Submenu
        self.file_sub = wx.Menu()
        self.file_sub.Append(-1, "Recent files", "")
        # self.file.Append(-1, "Recent", self.file_sub, "")
        self.file.AppendSubMenu(self.file_sub, "Recent", "")

        self.file.AppendSeparator()
        # Submenu end

        self.quit_program = wx.MenuItem(
            self.file, wx.ID_ANY, "&Quit\t" + keyS["Quit"], "Quit program"
        )
        self.quit_program.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "application-exit.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.file.Append(self.quit_program)

        self.menubar1.Append(self.file, "File")
        ## EDIT MENU ##############################################################################
        self.edit = wx.Menu()
        self.undo = wx.MenuItem(
            self.edit, wx.ID_ANY, "&Undo\t" + keyS["Undo"], "Undo text"
        )
        self.undo.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_MENU)
        )
        self.edit.Append(self.undo)

        self.redo = wx.MenuItem(
            self.edit, wx.ID_ANY, "&Redo\t" + keyS["Redo"], "Redo text"
        )
        self.redo.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU)
        )
        self.edit.Append(self.redo)

        self.edit.AppendSeparator()
        #self.clear = wx.MenuItem(
            #self.edit,
            #wx.ID_ANY,
            #"&Clear Undo-Redo\t" + keyS["Clear Undo-Redo"],
            #"Clear Undo-Redo history",
        #)
        #self.clear.SetBitmap(
            #wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_MENU)
        #)
        #self.edit.Append(self.clear)
        #self.edit.AppendSeparator()

        self.reloadtext = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            "&Reload text\t" + keyS["ReloadText"],
            "Ponovo učitaj text",
        )
        self.reloadtext.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "doc-revert.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.edit.Append(self.reloadtext)

        self.menubar1.Append(self.edit, "Edit")

        ## Actions ################################################################################
        self.action = wx.Menu()
        self.undo_action = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&Undo Action\t" + keyS["Undo_A"],
            "Undo prethodne akcije",
        )
        self.undo_action.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "edit-undo.png"), wx.BITMAP_TYPE_ANY
            )
        )
        self.action.Append(self.undo_action)
        self.redo_action = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&Redo Action\t" + keyS["Redo_A"],
            "Redo prethodne akcije",
        )
        self.redo_action.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "edit-redo.png"), wx.BITMAP_TYPE_ANY
            )
        )
        self.action.Append(self.redo_action)
        self.action.AppendSeparator()
        self.to_cyrillic = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&ToCyrillic\t" + keyS["ToCyrillic"],
            "Konvertuje u ćirilicu",
            wx.ITEM_NORMAL,
        )
        self.to_cyrillic.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "cyr-ltr.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.to_cyrillic)

        self.to_ansi = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&ToANSI\t" + keyS["ToANSI"],
            "Konvertuje u ANSI",
            wx.ITEM_NORMAL,
        )
        self.to_ansi.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "go-next.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.to_ansi)

        self.to_utf8 = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&ToUTF\t" + keyS["ToUTF"],
            "Konvertuje u UTF",
            wx.ITEM_NORMAL,
        )
        self.to_utf8.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "go-next.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.to_utf8)

        self.action.AppendSeparator()

        self.transcrib = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&Transcribe\t" + keyS["Transcribe"],
            "Transcribe",
            wx.ITEM_NORMAL,
        )
        self.transcrib.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_MENU)
        )
        self.action.Append(self.transcrib)
        
        self.change = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&ChangeManualy\t" + keyS["Change"],
            "Transcribe manualy from dictionaries",
            wx.ITEM_NORMAL,
        )
        self.change.SetBitmap(
            wx.Bitmap(filePath("resources", "icons", "cyr-ltr.png"), wx.BITMAP_TYPE_ANY)
        )
        self.action.Append(self.change)

        self.specials = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&SpecReplace\t" + keyS["SpecReplace"],
            "ReplaceSpecial definicije",
            wx.ITEM_NORMAL,
        )
        self.specials.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "go-next.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.specials)

        self.cleaner = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&Cleanup\t" + keyS["Cleanup"],
            "Clean subtitle file",
            wx.ITEM_NORMAL,
        )
        self.cleaner.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "edit-clear-all.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.cleaner)

        self.action.AppendSeparator()
        self._regex = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&CustomRegex\t" + keyS["CustomRegex"],
            "Apply Regex",
            wx.ITEM_NORMAL,
        )
        self._regex.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_MENU)
        )
        self.action.Append(self._regex)

        self.action.AppendSeparator()

        self.cyr_to_ansi = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&Cyr to latin ansi\t" + keyS["Cyr to latin ansi"],
            "Preslovljavanje cirilice u latinicu ansi",
            wx.ITEM_NORMAL,
        )
        self.cyr_to_ansi.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "go-next.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.cyr_to_ansi)

        self.cyr_to_utf = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&Cyr to latin utf8\t" + keyS["Cyr to latin utf8"],
            "Preslovljavanje cirilice u latinicu utf8",
            wx.ITEM_NORMAL,
        )
        self.cyr_to_utf.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "go-next.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.cyr_to_utf)

        self.action.AppendSeparator()

        self.fixer = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&FixSubtitle\t" + keyS["FixSubtitle"],
            "Fix subtitle file",
            wx.ITEM_NORMAL,
        )
        self.fixer.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "go-next.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.fixer)

        self.action.AppendSeparator()

        self.merger = wx.MenuItem(
            self.action,
            wx.ID_ANY,
            "&Merger\t" + keyS["Merger"],
            "Merge lines",
            wx.ITEM_NORMAL,
        )
        self.merger.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "merge.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.action.Append(self.merger)

        self.menubar1.Append(self.action, u"Actions")

        ## Preferences menu #######################################################################
        self.preferences = wx.Menu()
        self.bom_utf8 = wx.MenuItem(
            self.preferences,
            1011,
            "&bom_utf-8\t" + keyS["bom_utf-8"],
            "Default za unikode",
            wx.ITEM_CHECK,
        )
        self.preferences.Append(self.bom_utf8)

        self.txt_utf8 = wx.MenuItem(
            self.preferences,
            1012,
            "&txt_utf-8\t" + keyS["txt_utf-8"],
            "Default fajl format unikode",
            wx.ITEM_CHECK,
        )
        self.preferences.Append(self.txt_utf8)
        self.preferences.AppendSeparator()

        self.show = wx.MenuItem(
            self.preferences,
            1013,
            "&Show ErrorLog\t" + keyS["ErrorLog"],
            "Otvori error.log fajl u editoru",
            wx.ITEM_CHECK,
        )
        self.preferences.Append(self.show)
        self.preferences.AppendSeparator()

        self.prelatin = wx.MenuItem(
            self.preferences,
            1014,
            "&Lat-Cyr preprocessing\t" + keyS["PreLat-Cyr"],
            "Uključi-Isključi procesovanje specijalnih znakova za 'ToCyrillic' opciju",
            wx.ITEM_CHECK,
        )
        self.preferences.Append(self.prelatin)
        self.preferences.AppendSeparator()

        self.fonts = wx.MenuItem(
            self.preferences,
            wx.ID_ANY,
            "&Font settings\t" + keyS["Font settings"],
            "Font settings",
            wx.ITEM_NORMAL,
        )
        self.fonts.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "preferences-font.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.preferences.Append(self.fonts)

        self.preferences.AppendSeparator()

        self.shortcuts = wx.MenuItem(
            self.preferences,
            wx.ID_ANY,
            "&ShortcutEditor\t" + keyS["ShortcutEditor"],
            "Shortcut keys",
            wx.ITEM_NORMAL,
        )
        self.shortcuts.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "input-keyboard.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.preferences.Append(self.shortcuts)

        self.preferences.AppendSeparator()

        self.merger_pref = wx.MenuItem(
            self.preferences,
            wx.ID_ANY,
            "&MergerSettings" + keyS["MergerSettings"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.merger_pref.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "merge-settings.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.preferences.Append(self.merger_pref)

        self.menubar1.Append(self.preferences, u"Preferences")

        ## Help menu ##############################################################################
        self.help = wx.Menu()
        self.about = wx.MenuItem(
            self.help,
            wx.ID_ANY,
            "&About\t" + keyS["About"],
            "O programu",
            wx.ITEM_NORMAL,
        )
        self.about.SetBitmap(
            wx.Bitmap(
                filePath("resources", "icons", "help-about.png"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.help.Append(self.about)

        self.help.AppendSeparator()

        self.manual = wx.MenuItem(
            self.help,
            wx.ID_ANY,
            "&Manual\t" + keyS["Manual"],
            "Manual",
            wx.ITEM_NORMAL,
        )
        self.manual.SetBitmap(
            wx.Bitmap(
                wx.ArtProvider.GetBitmap(wx.ART_HELP_PAGE, wx.ART_MENU)
            )
        )
        self.help.Append(self.manual)

        self.menubar1.Append(self.help, u"Help")

        self.SetMenuBar(self.menubar1)
        # Menu Bar end

        self.frame_statusbar = self.CreateStatusBar(2)
        self.frame_statusbar.SetStatusWidths([-4, -1])

        # statusbar fields
        frame_statusbar_fields = ["SubtitleConverter is ready", ""]
        for i in range(len(frame_statusbar_fields)):
            self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)

        ## ToolBar ###############################################################################
        self.frame_toolbar = self.CreateToolBar(wx.TB_DEFAULT_STYLE|wx.TB_NODIVIDER, wx.ID_ANY)
        self.frame_toolbar.AddTool(
            1001,
            "Open",
            wx.ArtProvider.GetBitmap(
                wx.ART_FILE_OPEN, wx.ART_TOOLBAR, wx.DefaultSize
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Open file",
            "Open file",
        )
        self.frame_toolbar.AddTool(
            1010,
            "Save",
            wx.ArtProvider.GetBitmap(
                wx.ART_FILE_SAVE, wx.ART_TOOLBAR, wx.DefaultSize
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Save file",
            "Save file",
        )

        self.frame_toolbar.AddSeparator()

        self.frame_toolbar.AddTool(
            1002,
            "Cirilica",
            wx.Bitmap(
                filePath("resources", "icons", "cyrillic.png"),
                wx.BITMAP_TYPE_ANY,
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "U cirilicu",
            "U cirilicu",
        )
        self.frame_toolbar.AddTool(
            1003,
            "ANSI",
            wx.Bitmap(
                filePath("resources", "icons", "ANSI.png"),
                wx.BITMAP_TYPE_ANY,
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "U ansi",
            "U ansi",
        )
        self.frame_toolbar.AddTool(
            1004,
            "UTF",
            wx.Bitmap(
                filePath("resources", "icons", "UTF8.png"),
                wx.BITMAP_TYPE_ANY,
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "U utf-8",
            "U utf-8",
        )
        self.frame_toolbar.AddTool(
            1005,
            "Transcribe",
            wx.Bitmap(
                filePath("resources", "icons", "cyr-ltr.24.png"),
                wx.BITMAP_TYPE_ANY,
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Transcribe",
            "Transcribe",
        )
        self.frame_toolbar.AddTool(
            1006,
            "Special",
            wx.Bitmap(
                filePath("resources", "icons", "edit-find-replace.png"),
                wx.BITMAP_TYPE_ANY,
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Replace speial",
            "Replace special",
        )
        self.frame_toolbar.AddTool(
            1007,
            "Cleanup",
            wx.Bitmap(
                filePath("resources", "icons", "editclear.png"),
                wx.BITMAP_TYPE_ANY,
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Cleanup",
            "Cleanup",
        )

        self.frame_toolbar.AddTool(
            1008,
            "Quit",
            wx.Bitmap(
                filePath("resources", "icons", "application-exit.24.png"),
                wx.BITMAP_TYPE_ANY,
            ),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Exit",
            "Exit program",
        )
        
        self.frame_toolbar.AddSeparator()
        self.searchCtrl1 = wx.SearchCtrl(
            self.frame_toolbar,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_PROCESS_ENTER,
        )
        self.searchCtrl1.ShowSearchButton(True)
        self.searchCtrl1.ShowCancelButton(False)
        self.searchCtrl1.SetSize(120, 24)
        self.frame_toolbar.AddControl(self.searchCtrl1)
        self.frame_toolbar.AddSeparator()
        
        comboBox1Choices = [
            " auto",
            " windows-1250",
            " windows-1251",
            " windows-1252",
            " utf-8",
            " utf-16",
            " utf-16le",
            " utf-16be",
            " utf-32",
            " iso-8859-1",
            " iso-8859-2",
            " iso-8859-5",
            " ascii", 
            " latin",
            " latin2",
        ]
        self.comboBox1 = wx.ComboBox(
            self.frame_toolbar,
            wx.ID_ANY,
            "combo1",
            wx.DefaultPosition,
            wx.DefaultSize,
            comboBox1Choices,
            wx.CB_DROPDOWN | wx.BORDER_DEFAULT,
        )

        self.comboBox1.SetToolTip("Kodiranja")
        self.comboBox1.SetMinSize((118, 18))
        self.frame_toolbar.AddControl(self.comboBox1)
        self.comboBox1.SetSelection(0)
        
        self.frame_toolbar.SetToolBitmapSize((24, 24))
        self.frame_toolbar.SetMargins((5, 5))
        self.frame_toolbar.SetToolPacking(1)
        self.frame_toolbar.SetToolSeparation(8)
        self.SetToolBar(self.frame_toolbar)
        self.frame_toolbar.Realize()
        ## Tool Bar end ###########################################################################

        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.text_1 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            "",
            style=wx.TE_MULTILINE
            | wx.TE_NOHIDESEL
            | wx.TE_PROCESS_ENTER
            | wx.TE_PROCESS_TAB
            | wx.TE_RICH2
            | wx.TE_WORDWRAP,
        )
        wx.CallAfter(self.text_1.SetFocus)

        sizer_1.Add(self.text_1, 1, wx.ALL | wx.EXPAND, 5)

        self.panel_1.SetSizer(sizer_1)
        try:
            menu_dict = FILE_SETTINGS["Preferences"]
            if menu_dict["bom_utf8"] is True:
                self.preferences.Check(1011, check=True)
            if menu_dict["utf8_txt"] is True:
                self.preferences.Check(1012, check=True)
            if menu_dict["ShowLog"] is True:
                self.preferences.Check(1013, check=True)
            if menu_dict["preprocess"] is True:
                self.preferences.Check(1014, check=True)
        except Exception as e:
            logger.debug(f"{e}")

        self.Layout()

        # end wxGlade


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
