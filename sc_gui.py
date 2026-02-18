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
        self.file_open = self.file.Append(
            wx.ID_ANY,
            u"Open" + u"\t" + keyS["Open"],
            u"Open File",
        )
        self.file_open.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU)
        )
        
        self.open_multiple = self.file.Append(
            wx.ID_ANY,
            u"Open multiple" + "\t" + keyS["OpenMultiple"],
            u"Open multiple files",
        )
        self.open_multiple.SetBitmap(
            wx.Bitmap(join(I_PATH, "folder-search.16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.reload_file = self.file.Append(
            wx.ID_ANY,
            u"Reload file" + u"\t" + keyS["Reload file"],
            u"Reload file",
        )
        self.reload_file.SetBitmap(
            wx.Bitmap(join(I_PATH, "reload-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.reload_file.Enable(False)

        self.previous = self.file.Append(
            wx.ID_ANY,
            u"Open previous" + "\t" + keyS["Previous"],
            wx.EmptyString,
        )
        self.previous.SetBitmap(
            wx.Bitmap(join(I_PATH, "return-16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.previous.Enable(False)

        self.file.AppendSeparator()

        self.save = self.file.Append(
            wx.ID_ANY,
            u"Save" + u"\t" + keyS["Save"],
            u"Save changes",
        )
        self.save.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU))
        self.save.Enable(False)

        self.save_as = self.file.Append(
            wx.ID_ANY,
            u"Save as" + u"\t" + keyS["Save as"],
            u"Save file as...",
        )
        self.save_as.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU)
        )
        self.save_as.Enable(False)

        self.export_zip = self.file.Append(
            wx.ID_ANY,
            u"Export ZIP" + u"\t" + keyS["Export as ZIP"],
            u"Export as zip file",
        )
        self.export_zip.SetBitmap(
            wx.Bitmap(join(I_PATH, "zip_file.png"), wx.BITMAP_TYPE_ANY)
        )
        self.file.AppendSeparator()

        self.renamer = self.file.Append(
            wx.ID_ANY,
            u"Rename subtitles" + u"\t" + keyS["Rename subtitles"],
            u"Rename subtitle files",
        )
        self.renamer.SetBitmap(
            wx.Bitmap(join(I_PATH, "ListView.png"), wx.BITMAP_TYPE_ANY)
        )
        self.file.AppendSeparator()

        self.close_file = self.file.Append(
            wx.ID_ANY,
            u"Close" + u"\t" + keyS["Close"],
            u"Close current file",
        )
        self.close_file.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CLOSE, wx.ART_MENU))
        
        self.recent_files = wx.Menu()
        # self.recent_files.Append(-1, "Recent files", "")
        self.file.AppendSubMenu(self.recent_files, u"Recent files")

        self.file.AppendSeparator()

        self.quit_program = self.file.Append(
            wx.ID_ANY,
            u"Quit" + u"\t" + keyS["Quit"],
            u"Exit program",
        )
        self.quit_program.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU))
        
        self.menubar1.Append(self.file, u"File")
        
        self.view = wx.Menu()
        self.zoom_in = self.view.Append(
            wx.ID_ANY,
            "Zoom in" + "\t" + keyS["Zoom_in"],
            wx.EmptyString,
        )
        self.zoom_in.SetBitmap(
            wx.Bitmap(join(I_PATH, "zoom-in.16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.zoom_out = self.view.Append(
            wx.ID_ANY,
            "Zoom out" + "\t" + keyS["Zoom_out"],
            wx.EmptyString,
        )
        self.zoom_out.SetBitmap(
            wx.Bitmap(join(I_PATH, "zoom-out.16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.zoom_normal = self.view.Append(
            wx.ID_ANY,
            "Normal size" + "\t" + keyS["Zoom_normal"],
            wx.EmptyString,
        )
        self.zoom_normal.SetBitmap(
            wx.Bitmap(join(I_PATH, "nsize.16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.menubar1.Append(self.view, "View")
        
        self.edit = wx.Menu()
        self.undo = self.edit.Append(
            wx.ID_ANY,
            u"Undo" + u"\t" + keyS["Undo"],
            u"Undo",
        )
        self.undo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_MENU))
        
        self.redo = self.edit.Append(
            wx.ID_ANY,
            u"Redo" + u"\t" + keyS["Redo"],
            u"Redo",
        )
        self.redo.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU))
        
        self.copy = self.edit.Append(
            wx.ID_ANY,
            u"Copy" + u"\t" + keyS["Copy"],
            u"Copy text",
        )
        self.copy.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
        
        self.cut = self.edit.Append(
            wx.ID_ANY,
            u"Cut" + u"\t" + keyS["Cut"],
            u"Cut text",
        )
        self.cut.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_MENU))
        
        self.paste = self.edit.Append(
            wx.ID_ANY,
            u"Paste" + u"\t" + keyS["Paste"],
            u"Paste text",
        )
        self.paste.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_MENU))
        
        self.delete = self.edit.Append(
            wx.ID_ANY,
            u"Delete" + u"\t" + keyS["Delete"],
            u"Delete text",
        )
        self.delete.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU))
        self.edit.AppendSeparator()

        self.find_replace = self.edit.Append(
            wx.ID_ANY,
            u"FindReplace" + u"\t" + keyS["FindReplace"],
            u"Find and replace text",
        )
        self.find_replace.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_MENU)
        )
        self.edit.AppendSeparator()

        self.select_all = self.edit.Append(
            wx.ID_ANY,
            u"Select all" + u"\t" + keyS["SelectAll"],
            u"Select all text",
        )
        self.select_all.SetBitmap(
            wx.Bitmap(join(I_PATH, "selectall.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.menubar1.Append(self.edit, u"Edit")

        self.format = wx.Menu()
        self.italic = self.format.Append(
            wx.ID_ANY,
            u"Italic" + u"\t" + keyS["Italic"],
            u"Format Italic",
        )
        self.italic.SetBitmap(
            wx.Bitmap(join(I_PATH, "text-italic.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.bold = self.format.Append(
            wx.ID_ANY,
            u"Bold" + u"\t" + keyS["Bold"],
            u"Bold fonts",
        )
        self.bold.SetBitmap(
            wx.Bitmap(join(I_PATH, "text-bold.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.underline = self.format.Append(
            wx.ID_ANY,
            u"Underline" + u"\t" + keyS["Underline"],
            u"Text underline",
        )
        self.underline.SetBitmap(
            wx.Bitmap(join(I_PATH, "text-underline.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.color = self.format.Append(
            wx.ID_ANY,
            u"Color" + u"\t" + keyS["Color"],
            u"Text color",
        )
        self.color.SetBitmap(
            wx.Bitmap(join(I_PATH, "app-graphics.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.all_caps = self.format.Append(
            wx.ID_ANY,
            u"All caps" + u"\t" + keyS["AllCaps"],
            u"All caps",
        )
        self.all_caps.SetBitmap(
            wx.Bitmap(join(I_PATH, "uppercase-16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.menubar1.Append(self.format, u"Format")

        self.actions = wx.Menu()
        self.to_cyrillic = self.actions.Append(
            wx.ID_ANY,
            u"ToCyr" + "\t" + keyS["ToCYR"],
            "Preslovljavanje u ćirilicu",
        )
        self.to_cyrillic.SetBitmap(
            wx.Bitmap(join(I_PATH, "cyr-ltr.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.to_ansi = self.actions.Append(
            wx.ID_ANY,
            u"To ANSI" + "\t" + keyS["ToANSI"],
            u"To ansi",
        )
        self.to_ansi.SetBitmap(
            wx.Bitmap(join(I_PATH, "filenew-16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.to_utf8 = self.actions.Append(
            wx.ID_ANY,
            u"To UTF8" + "\t" + keyS["ToUTF8"],
            u"To UTF8",
        )
        self.to_utf8.SetBitmap(
            wx.Bitmap(join(I_PATH, "filenew1-16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.cyr_to_lat_ansi = self.actions.Append(
            wx.ID_ANY,
            u"Cyr to lat_ANSI" + u"\t" + keyS["Cyr to latin ansi"],
            u"Ćirilica u latinicu ANSI",
        )
        self.cyr_to_lat_ansi.SetBitmap(
            wx.Bitmap(join(I_PATH, "text.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.cyr_to_lat_utf8 = self.actions.Append(
            wx.ID_ANY,
            u"Cyr to lat_UTF8" + u"\t" + keyS["Cyr to latin utf8"],
            u"Ćirilica u latinicu UTF8",
        )
        self.cyr_to_lat_utf8.SetBitmap(
            wx.Bitmap(join(I_PATH, "text.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.AppendSeparator()

        self.convert_encoding = self.actions.Append(
            wx.ID_ANY,
            "Convert encoding" + "\t" + keyS["Convert"],
            "Univerzalni metod promene kodiranja teksta",
        )
        self.convert_encoding.SetBitmap(
            wx.Bitmap(join(I_PATH, "raw.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.AppendSeparator()

        self.change_manually = self.actions.Append(
            wx.ID_ANY,
            "ChangeManually" + "\t" + keyS["Change"],
            "Ručno uredi titlove",
        )
        self.change_manually.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_MENU)
        )
        self.actions.AppendSeparator()

        self.transcribe = self.actions.Append(
            wx.ID_ANY,
            u"Transcribe" + u"\t" + keyS["Transcribe"],
            u"Primena rečnika na tekst",
        )
        self.transcribe.SetBitmap(
            wx.Bitmap(join(I_PATH, "cyr-ltr.16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.clean_up = self.actions.Append(
            wx.ID_ANY,
            u"Cleanup" + u"\t" + keyS["Cleanup"],
            u"Clean subtitles",
        )
        self.clean_up.SetBitmap(
            wx.Bitmap(join(I_PATH, "editclear-16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.spec_replace = self.actions.Append(
            wx.ID_ANY,
            u"SpecReplace" + u"\t" + keyS["SpecReplace"],
            u"Primena rečnika Special-Replace",
        )
        self.spec_replace.SetBitmap(
            wx.Bitmap(join(I_PATH, "edit-replace.16.png"), wx.BITMAP_TYPE_ANY)
        )
        self.actions.AppendSeparator()

        self.fix_subtitles = self.actions.Append(
            wx.ID_ANY,
            u"Fixer" + u"\t" + keyS["FixSubtitle"],
            u"Fix subtitles",
        )
        self.fix_subtitles.SetBitmap(
            wx.Bitmap(join(I_PATH, "search.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.merge = self.actions.Append(
            wx.ID_ANY,
            u"Merger" + u"\t" + keyS["Merger"],
            u"Merge lines",
        )
        self.merge.SetBitmap(wx.Bitmap(join(I_PATH, "merge.png"), wx.BITMAP_TYPE_ANY))
        
        self.menubar1.Append(self.actions, u"Actions")

        self.preferences = wx.Menu()
        self.utf8_BOM = self.preferences.AppendCheckItem(
            wx.ID_ANY,
            u"utf8_bom" + "\t" + keyS["bom_utf8"],
            wx.EmptyString,
        )
        
        self.utf8_TXT = self.preferences.AppendCheckItem(
            wx.ID_ANY,
            u"utf8_txt" + "\t" + keyS["txt_utf8"],
            wx.EmptyString,
        )
        self.preferences.AppendSeparator()
        
        self.notify = self.preferences.AppendCheckItem(
            wx.ID_ANY,
            f"ShowErrors\t{keyS['ShowErrors']}",
            "Pokazuje Info poruku sa greškama",
        )
        self.preferences.AppendSeparator()        

        self.settings_main = self.preferences.Append(
            wx.ID_ANY,
            u"Settings main" + u"\t" + keyS["MainSettings"],
            u"Podešavanja programa",
        )
        self.settings_main.SetBitmap(
            wx.Bitmap(join(I_PATH, "preferences.16.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.merger_settings = self.preferences.Append(
            wx.ID_ANY,
            u"Merger settings" + "\t" + keyS["MergerSettings"],
            wx.EmptyString,
        )
        self.merger_settings.SetBitmap(
            wx.Bitmap(join(I_PATH, "document-properties1.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.ShortcutEdit = self.preferences.Append(
            wx.ID_ANY,
            "ShortcutEditor" + "\t" + keyS["ShortcutEditor"],
            wx.EmptyString,
        )
        self.ShortcutEdit.SetBitmap(
            wx.Bitmap(join(I_PATH, "keyboard.png")), wx.BITMAP_TYPE_ANY
        )
        
        self.menubar1.Append(self.preferences, u"Preferences")

        self.help = wx.Menu()
        self.about = self.help.Append(
            wx.ID_ANY,
            u"About" + "\t" + keyS["About"],
            wx.EmptyString,
        )
        self.about.SetBitmap(
            wx.Bitmap(join(I_PATH, "help-about.png"), wx.BITMAP_TYPE_ANY)
        )
        
        self.manual = self.help.Append(
            wx.ID_ANY,
            u"Manual" + u"\t" + keyS["Manual"],
            u"Manual",
        )
        self.manual.SetBitmap(wx.Bitmap(join(I_PATH, "help-contents.png"), wx.BITMAP_TYPE_ANY))
        #self.manual.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_PAGE, wx.ART_MENU))
        
        self.menubar1.Append(self.help, u"Help")

        self.SetMenuBar(self.menubar1)

        self.Centre(wx.BOTH)
        
        try:
            menu_dict = MAIN_SETTINGS["Preferences"]
            if menu_dict["bom_utf8"] is True:
                self.utf8_BOM.Check(True)
            if menu_dict["utf8_txt"] is True:
                self.utf8_TXT.Check(True)
            if menu_dict["Notify"] is True:
                self.notify.Check(True)
        except Exception as e:
            logger.debug(f"Unexpected error: {e}")


class MyApp(wx.App):
    def OnInit(self):
        self.frame = ConverterFrame(None)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
