# -*- coding: utf-8 -*-

## Python code generated with wxFormBuilder (version 3.10.1-282-g1fa54006)
## http://www.wxformbuilder.org/
##
## Modified by padovaSR
##
from settings import MAIN_SETTINGS, I_PATH, shortcutsKeys
from os.path import join
import logging.config
import wx
import wx.richtext

logger = logging.getLogger(__name__)

## Class ConverterFrame

class ConverterFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE)

        try:
            self.SetSize(
                (MAIN_SETTINGS["FrameSize"]["W"], MAIN_SETTINGS["FrameSize"]["H"])
            )
        except:
            self.SetSize((631, 632))
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(join(I_PATH, "sc.ico"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.panel1 = wx.Panel(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_NONE | wx.TAB_TRAVERSAL,
        )
        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        wx.richtext.RichTextBuffer.SetFloatingLayoutMode(False)
        self.Text_1 = wx.richtext.RichTextCtrl(
            self.panel1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_PROCESS_TAB | wx.VSCROLL | wx.BORDER_NONE | wx.WANTS_CHARS,
        )
        wx.CallAfter(self.Text_1.SetFocus)

        #self.Text_1.SetFont(
             #wx.Font(
                #MAIN_SETTINGS["key4"]['fontSize'],
                #wx.FONTFAMILY_DEFAULT,
                #wx.FONTSTYLE_NORMAL,
                #MAIN_SETTINGS["key4"]['weight'],
                #0,
                #MAIN_SETTINGS["key4"]['new_font'],
            #)
        #)
        self.Text_1.SetToolTip(u"Drag and Drop Enabled")

        bSizer2.Add(self.Text_1, 1, wx.ALL | wx.EXPAND, 5)

        self.panel1.SetSizer(bSizer2)
        self.panel1.Layout()
        bSizer2.Fit(self.panel1)
        bSizer1.Add(self.panel1, 1, wx.EXPAND)

        self.SetSizer(bSizer1)
        self.Layout()

        self.statusBar1 = self.CreateStatusBar(2, wx.STB_SIZEGRIP, wx.ID_ANY)
        self.statusBar1.SetStatusWidths([-3, -1])
        # statusbar fields
        frame_statusbar_fields = ["SubtitleConverter is ready", ""]
        for i in range(len(frame_statusbar_fields)):
            self.statusBar1.SetStatusText(frame_statusbar_fields[i], i)

        self.toolBar1 = self.CreateToolBar(
            wx.TB_HORIZONTAL | wx.TB_NODIVIDER | wx.FULL_REPAINT_ON_RESIZE, wx.ID_ANY
        )
        self.toolBar1.SetToolBitmapSize(wx.Size(21, 21))
        self.toolBar1.SetToolSeparation(2)
        self.open = self.toolBar1.AddTool(
            108,
            u"Open",
            wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            u"Open File",
            u"Open File",
            None,
        )

        self.save = self.toolBar1.AddTool(
            109,
            u"Save",
            wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            u"Save changes",
            u"Save changes",
            None,
        )

        self.toolBar1.AddSeparator()

        self.to_cyr = self.toolBar1.AddTool(
            104,
            u"To_Cyr",
            wx.Bitmap(join(I_PATH, "cyrillic.png"), wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            u"To cyrillic",
            u"To cyrillic",
            None,
        )

        self.to_ansi = self.toolBar1.AddTool(
            102,
            u"To_Ansi",
            wx.Bitmap(join(I_PATH, "filenew.png"), wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            u"To ansi",
            u"To ANSI",
            None,
        )

        self.to_utf8 = self.toolBar1.AddTool(
            103,
            u"To_UTF8",
            wx.Bitmap(join(I_PATH, "filenew_1.png"), wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            u"To utf8",
            u"To UTF8",
            None,
        )

        self.toolBar1.AddSeparator()

        self.transcribe = self.toolBar1.AddTool(
            105,
            u"Transcribe",
            wx.Bitmap(join(I_PATH, "cyr-ltr.24.png"), wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Transkripcija",
            "Transkripcija",
            None,
        )

        self.spec_replace = self.toolBar1.AddTool(
            106,
            u"SpecReplace",
            wx.Bitmap(join(I_PATH, "edit-replace.png"), wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Special Replace",
            "Special Replace",
            None,
        )

        self.clean_up = self.toolBar1.AddTool(
            107,
            u"CleanUp",
            wx.Bitmap(join(I_PATH, "editclear.png"), wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Cleanup",
            "Cleanup",
            None,
        )

        self.toolBar1.AddSeparator()

        self.quit = self.toolBar1.AddTool(
            101,
            u"Quit",
            wx.Bitmap(join(I_PATH, "quit.png"), wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "Exit program",
            "Exit program",
            None,
        )

        self.toolBar1.AddSeparator()

        self.label_1 = wx.StaticText(
            self.toolBar1,
            wx.ID_ANY,
            u"Kodiranje:",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_LEFT,
        )
        self.label_1.Wrap(-1)

        self.label_1.SetFont(
            wx.Font(
                9,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Franklin Gothic Medium",
            )
        )

        self.toolBar1.AddControl(self.label_1)
        comboBoxChoices = [
            u"auto",
            u"windows-1250",
            u"windows-1251",
            u"windows-1252",
            u"utf-8-sig",
            u"utf-8",
            u"cp852",
            u"latin2",
            u"ascii",
            u"utf16",
        ]
        self.comboBox = wx.ComboBox(
            self.toolBar1,
            wx.ID_ANY,
            u"ComboBox",
            wx.DefaultPosition,
            wx.DefaultSize,
            comboBoxChoices,
            wx.CB_DROPDOWN | wx.BORDER_DEFAULT,
        )
        self.comboBox.SetSelection(0)
        self.comboBox.SetFont(
            wx.Font(
                9,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Sans",
            )
        )
        # self.comboBox.SetMinSize(wx.Size(125, 20))
        # self.comboBox.SetMaxSize(wx.Size(125, 20))

        self.toolBar1.AddControl(self.comboBox)
        self.toolBar1.Realize()
        
        ## Menu Bar ===========================================================================================##
        keyS = shortcutsKeys
        self.menubar1 = wx.MenuBar(0 | wx.BORDER_NONE | wx.FULL_REPAINT_ON_RESIZE)
        self.file = wx.Menu()
        self.file_open = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Open" + u"\t" + keyS["Open"],
            u"Open File",
            wx.ITEM_NORMAL,
        )
        self.file_open.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU)
        )
        self.file.Append(self.file_open)

        self.open_multiple = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Open multiple" + "\t" + keyS["OpenMultiple"],
            u"Open multiple files",
            wx.ITEM_NORMAL,
        )
        self.open_multiple.SetBitmap(
            wx.Bitmap(join(I_PATH, "folder-search.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.file.Append(self.open_multiple)

        self.reload_file = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Reload file" + u"\t" + keyS["Reload file"],
            u"Reload file",
            wx.ITEM_NORMAL,
        )
        self.reload_file.SetBitmap(
            wx.Bitmap(join(I_PATH, "reload-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.file.Append(self.reload_file)
        self.reload_file.Enable(False)

        self.previous = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Open previous" + "\t" + keyS["Previous"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.previous.SetBitmap(
            wx.Bitmap(join(I_PATH, "return-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.file.Append(self.previous)
        self.previous.Enable(False)

        self.file.AppendSeparator()

        self.save = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Save" + u"\t" + keyS["Save"],
            u"Save changes",
            wx.ITEM_NORMAL,
        )
        self.save.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU))
        self.file.Append(self.save)
        self.save.Enable(False)

        self.save_as = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Save as" + u"\t" + keyS["Save as"],
            u"Save file as...",
            wx.ITEM_NORMAL,
        )
        self.save_as.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU)
        )
        self.file.Append(self.save_as)
        self.save_as.Enable(False)

        self.export_zip = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Export ZIP" + u"\t" + keyS["Export as ZIP"],
            u"Export as zip file",
            wx.ITEM_NORMAL,
        )
        self.export_zip.SetBitmap(
            wx.Bitmap(join(I_PATH, "zip_file.png"), wx.BITMAP_TYPE_ANY)
        )
        self.file.Append(self.export_zip)

        self.file.AppendSeparator()

        self.renamer = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Rename subtitles" + u"\t" + keyS["Rename subtitles"],
            u"Rename subtitle files",
            wx.ITEM_NORMAL,
        )
        self.renamer.SetBitmap(
            wx.Bitmap(join(I_PATH, "ListView.png"), wx.BITMAP_TYPE_ANY)
        )
        self.file.Append(self.renamer)

        self.file.AppendSeparator()

        self.close_file = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Close" + u"\t" + keyS["Close"],
            u"Close current file",
            wx.ITEM_NORMAL,
        )
        self.close_file.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_MENU))
        self.file.Append(self.close_file)

        self.recent_files = wx.Menu()
        # self.recent_files.Append(-1, "Recent files", "")
        self.file.AppendSubMenu(self.recent_files, u"Recent files")

        self.file.AppendSeparator()

        self.quit_program = wx.MenuItem(
            self.file,
            wx.ID_ANY,
            u"Quit" + u"\t" + keyS["Quit"],
            u"Exit program",
            wx.ITEM_NORMAL,
        )
        self.quit_program.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU))
        self.file.Append(self.quit_program)

        self.menubar1.Append(self.file, u"File")
        
        self.view = wx.Menu()
        self.zoom_in = wx.MenuItem(
            self.view,
            wx.ID_ANY,
            "Zoom in" + "\t" + keyS["Zoom_in"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.zoom_in.SetBitmap(
            wx.Bitmap(join(I_PATH, "zoom-in.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.view.Append(self.zoom_in)

        self.zoom_out = wx.MenuItem(
            self.view,
            wx.ID_ANY,
            "Zoom out" + "\t" + keyS["Zoom_out"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.zoom_out.SetBitmap(
            wx.Bitmap(join(I_PATH, "zoom-out.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.view.Append(self.zoom_out)

        self.zoom_normal = wx.MenuItem(
            self.view,
            wx.ID_ANY,
            "Normal size" + "\t" + keyS["Zoom_normal"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.zoom_normal.SetBitmap(
            wx.Bitmap(join(I_PATH, "nsize.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.view.Append(self.zoom_normal)
        
        self.menubar1.Append(self.view, "View")
        
        self.edit = wx.Menu()
        self.undo = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"Undo" + u"\t" + keyS["Undo"],
            u"Undo",
            wx.ITEM_NORMAL,
        )
        self.undo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_MENU))
        self.edit.Append(self.undo)

        self.redo = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"Redo" + u"\t" + keyS["Redo"],
            u"Redo",
            wx.ITEM_NORMAL,
        )
        self.redo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU))
        self.edit.Append(self.redo)

        self.copy = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"Copy" + u"\t" + keyS["Copy"],
            u"Copy text",
            wx.ITEM_NORMAL,
        )
        self.copy.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
        self.edit.Append(self.copy)

        self.cut = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"Cut" + u"\t" + keyS["Cut"],
            u"Cut text",
            wx.ITEM_NORMAL,
        )
        self.cut.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_MENU))
        self.edit.Append(self.cut)

        self.paste = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"Paste" + u"\t" + keyS["Paste"],
            u"Paste text",
            wx.ITEM_NORMAL,
        )
        self.paste.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_MENU))
        self.edit.Append(self.paste)

        self.delete = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"Delete" + u"\t" + keyS["Delete"],
            u"Delete text",
            wx.ITEM_NORMAL,
        )
        self.delete.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU))
        self.edit.Append(self.delete)

        self.edit.AppendSeparator()

        self.find_replace = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"FindReplace" + u"\t" + keyS["FindReplace"],
            u"Find and replace text",
            wx.ITEM_NORMAL,
        )
        self.find_replace.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_MENU)
        )
        self.edit.Append(self.find_replace)

        self.edit.AppendSeparator()

        self.select_all = wx.MenuItem(
            self.edit,
            wx.ID_ANY,
            u"Select all" + u"\t" + keyS["SelectAll"],
            u"Select all text",
            wx.ITEM_NORMAL,
        )
        self.select_all.SetBitmap(
            wx.Bitmap(join(I_PATH, "selectall.png"), wx.BITMAP_TYPE_ANY)
        )
        self.edit.Append(self.select_all)

        self.menubar1.Append(self.edit, u"Edit")

        self.format = wx.Menu()
        self.italic = wx.MenuItem(
            self.format,
            wx.ID_ANY,
            u"Italic" + u"\t" + keyS["Italic"],
            u"Format Italic",
            wx.ITEM_NORMAL,
        )
        self.italic.SetBitmap(
            wx.Bitmap(join(I_PATH, "text-italic.png"), wx.BITMAP_TYPE_ANY)
        )
        self.format.Append(self.italic)

        self.bold = wx.MenuItem(
            self.format,
            wx.ID_ANY,
            u"Bold" + u"\t" + keyS["Bold"],
            u"Bold fonts",
            wx.ITEM_NORMAL,
        )
        self.bold.SetBitmap(
            wx.Bitmap(join(I_PATH, "text-bold.png"), wx.BITMAP_TYPE_ANY)
        )
        self.format.Append(self.bold)

        self.underline = wx.MenuItem(
            self.format,
            wx.ID_ANY,
            u"Underline" + u"\t" + keyS["Underline"],
            u"Text underline",
            wx.ITEM_NORMAL,
        )
        self.underline.SetBitmap(
            wx.Bitmap(join(I_PATH, "text-underline.png"), wx.BITMAP_TYPE_ANY)
        )
        self.format.Append(self.underline)

        self.color = wx.MenuItem(
            self.format,
            wx.ID_ANY,
            u"Color" + u"\t" + keyS["Color"],
            u"Text color",
            wx.ITEM_NORMAL,
        )
        self.color.SetBitmap(
            wx.Bitmap(join(I_PATH, "app-graphics.png"), wx.BITMAP_TYPE_ANY)
        )
        self.format.Append(self.color)

        self.all_caps = wx.MenuItem(
            self.format,
            wx.ID_ANY,
            u"All caps" + u"\t" + keyS["AllCaps"],
            u"All caps",
            wx.ITEM_NORMAL,
        )
        self.all_caps.SetBitmap(
            wx.Bitmap(join(I_PATH, "uppercase-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.format.Append(self.all_caps)

        self.menubar1.Append(self.format, u"Format")

        self.actions = wx.Menu()
        self.to_cyrillic = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"ToCyr" + "\t" + keyS["ToCYR"],
            "Preslovljavanje u ćirilicu",
            wx.ITEM_NORMAL,
        )
        self.to_cyrillic.SetBitmap(
            wx.Bitmap(join(I_PATH, "cyr-ltr.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.to_cyrillic)

        self.to_ansi = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"To ANSI" + "\t" + keyS["ToANSI"],
            u"To ansi",
            wx.ITEM_NORMAL,
        )
        self.to_ansi.SetBitmap(
            wx.Bitmap(join(I_PATH, "filenew-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.to_ansi)

        self.to_utf8 = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"To UTF8" + "\t" + keyS["ToUTF8"],
            u"To UTF8",
            wx.ITEM_NORMAL,
        )
        self.to_utf8.SetBitmap(
            wx.Bitmap(join(I_PATH, "filenew1-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.to_utf8)

        self.cyr_to_lat_ansi = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"Cyr to lat_ANSI" + u"\t" + keyS["Cyr to latin ansi"],
            u"Ćirilica u latinicu ANSI",
            wx.ITEM_NORMAL,
        )
        self.cyr_to_lat_ansi.SetBitmap(
            wx.Bitmap(join(I_PATH, "text.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.cyr_to_lat_ansi)

        self.cyr_to_lat_utf8 = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"Cyr to lat_UTF8" + u"\t" + keyS["Cyr to latin utf8"],
            u"Ćirilica u latinicu UTF8",
            wx.ITEM_NORMAL,
        )
        self.cyr_to_lat_utf8.SetBitmap(
            wx.Bitmap(join(I_PATH, "text.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.cyr_to_lat_utf8)

        self.actions.AppendSeparator()

        self.convert_encoding = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            "Convert encoding" + "\t" + keyS["Convert"],
            "Univerzalni metod promene kodiranja teksta",
            wx.ITEM_NORMAL,
        )
        self.convert_encoding.SetBitmap(
            wx.Bitmap(join(I_PATH, "raw.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.convert_encoding)

        self.actions.AppendSeparator()

        self.change_manually = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            "ChangeManually" + "\t" + keyS["Change"],
            "Ručno uredi titlove",
            wx.ITEM_NORMAL,
        )
        self.change_manually.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_MENU)
        )
        self.actions.Append(self.change_manually)

        self.actions.AppendSeparator()

        self.transcribe = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"Transcribe" + u"\t" + keyS["Transcribe"],
            u"Primena rečnika na tekst",
            wx.ITEM_NORMAL,
        )
        self.transcribe.SetBitmap(
            wx.Bitmap(join(I_PATH, "cyr-ltr.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.transcribe)

        self.clean_up = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"Cleanup" + u"\t" + keyS["Cleanup"],
            u"Clean subtitles",
            wx.ITEM_NORMAL,
        )
        self.clean_up.SetBitmap(
            wx.Bitmap(join(I_PATH, "editclear-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.clean_up)

        self.spec_replace = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"SpecReplace" + u"\t" + keyS["SpecReplace"],
            u"Primena rečnika Special-Replace",
            wx.ITEM_NORMAL,
        )
        self.spec_replace.SetBitmap(
            wx.Bitmap(join(I_PATH, "edit-replace.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.spec_replace)

        self.actions.AppendSeparator()

        self.fix_subtitles = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"Fixer" + u"\t" + keyS["FixSubtitle"],
            u"Fix subtitles",
            wx.ITEM_NORMAL,
        )
        self.fix_subtitles.SetBitmap(
            wx.Bitmap(join(I_PATH, "search.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.Append(self.fix_subtitles)

        self.merge = wx.MenuItem(
            self.actions,
            wx.ID_ANY,
            u"Merger" + u"\t" + keyS["Merger"],
            u"Merge lines",
            wx.ITEM_NORMAL,
        )
        self.merge.SetBitmap(wx.Bitmap(join(I_PATH, "merge.png"), wx.BITMAP_TYPE_ANY))
        self.actions.Append(self.merge)

        self.menubar1.Append(self.actions, u"Actions")

        self.preferences = wx.Menu()
        self.utf8_BOM = wx.MenuItem(
            self.preferences,
            1011,
            u"utf8_bom" + "\t" + keyS["bom_utf8"],
            wx.EmptyString,
            wx.ITEM_CHECK,
        )
        self.preferences.Append(self.utf8_BOM)

        self.utf8_TXT = wx.MenuItem(
            self.preferences,
            1012,
            u"utf8_txt" + "\t" + keyS["txt_utf8"],
            wx.EmptyString,
            wx.ITEM_CHECK,
        )
        self.preferences.Append(self.utf8_TXT)

        self.preferences.AppendSeparator()

        self.settings_main = wx.MenuItem(
            self.preferences,
            wx.ID_ANY,
            u"Settings main" + u"\t" + keyS["MainSettings"],
            u"Podešavanja programa",
            wx.ITEM_NORMAL,
        )
        self.settings_main.SetBitmap(
            wx.Bitmap(join(I_PATH, "preferences.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.preferences.Append(self.settings_main)

        self.merger_settings = wx.MenuItem(
            self.preferences,
            wx.ID_ANY,
            u"Merger settings" + "\t" + keyS["MergerSettings"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.merger_settings.SetBitmap(
            wx.Bitmap(join(I_PATH, "document-properties1.png"), wx.BITMAP_TYPE_ANY)
        )
        self.preferences.Append(self.merger_settings)

        self.ShortcutEdit = wx.MenuItem(
            self.preferences,
            wx.ID_ANY,
            "ShortcutEditor" + "\t" + keyS["ShortcutEditor"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.ShortcutEdit.SetBitmap(
            wx.Bitmap(join(I_PATH, "keyboard.png")), wx.BITMAP_TYPE_ANY
        )
        self.preferences.Append(self.ShortcutEdit)

        self.menubar1.Append(self.preferences, u"Preferences")

        self.help = wx.Menu()
        self.about = wx.MenuItem(
            self.help,
            wx.ID_ANY,
            u"About" + "\t" + keyS["About"],
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.about.SetBitmap(
            wx.Bitmap(join(I_PATH, "help-about.png"), wx.BITMAP_TYPE_ANY)
        )
        self.help.Append(self.about)

        self.manual = wx.MenuItem(
            self.help,
            wx.ID_ANY,
            u"Manual" + u"\t" + keyS["Manual"],
            u"Manual",
            wx.ITEM_NORMAL,
        )
        self.manual.SetBitmap(wx.Bitmap(join(I_PATH, "help-contents.png"), wx.BITMAP_TYPE_ANY))
        #self.manual.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_PAGE, wx.ART_MENU))
        self.help.Append(self.manual)

        self.menubar1.Append(self.help, u"Help")

        self.SetMenuBar(self.menubar1)

        self.Centre(wx.BOTH)
        try:
            menu_dict = MAIN_SETTINGS["Preferences"]
            if menu_dict["bom_utf8"] is True:
                self.preferences.Check(1011, check=True)
            if menu_dict["utf8_txt"] is True:
                self.preferences.Check(1012, check=True)
        except Exception as e:
            logger.debug(f"{e}")        


class MyApp(wx.App):
    def OnInit(self):
        self.frame = ConverterFrame(None)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
