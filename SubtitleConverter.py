# -*- coding: utf-8 -*-


from settings import MAIN_SETTINGS, MULTI_FILE, WORK_TEXT, FILE_HISTORY, main_settings_file, log_file_history, printEncoding, shortcutsKeys
from MultiSelection import MultiFiles 
from choice_dialog import MultiChoice
from zip_confirm import ZipStructure
from interactive_replace import FindReplace

from settings_dialog import SettingsDialog
from merge import myMerger
from TextFileProc import FileHandler, DocumentHandler, ErrorsHandler, Transliteracija, normalizeText

from resources.IsCyrillic import checkCyrillicAlphabet
from resources.renamer import RenameFiles
from resources.FixSubtitles import SubtitleFixer
from resources.fixer_settings import FixerSettings
from resources.merger_settings import MergerSettings
from resources import ExportZipFile
from resources.Manual import MyManual

import srt
import re
import json
import shutil
import linecache
import sys
import os
from os.path import join, basename, normpath, exists, splitext, dirname
import inspect

import wx
import wx.richtext as rt

try:
    from agw import shortcuteditor as SE
except ImportError: 
    import wx.lib.agw.shortcuteditor as SE

from sc_gui import ConverterFrame

import logging.config
logging.config.fileConfig("resources/var/log/mainlog.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

VERSION = linecache.getline(join("resources", "version.txt"), 1).rstrip()

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.main_window = window.GetTopLevelParent()  # Store a reference to the main window

    def OnDropFiles(self, x, y, filenames):
        self.main_window.handle_drop_files(filenames)  # Use the reference to the main window
        return True

class MainWindow(ConverterFrame):

    def __init__(self, *args):
        ConverterFrame.__init__(self, *args)

        self.SetTitle(f"SubtitleConverter {VERSION}")
        
        drop_target = MyFileDropTarget(self.Text_1)
        self.Text_1.SetDropTarget(drop_target)        
        
        self.single_file = r""
        self.file_enc = r""
        self.CYR = False
        self.showMessage = True
        self.new_files = []
        self.cyr_utf8 = []
        self.sc = {}
        
        self.hideDialog = False
        self.lastCaller = None
        
        self.findData = wx.FindReplaceData()
        self.findData.SetFlags(wx.FR_DOWN)        
        self.find_dialog = None

        self.setFontAndStyle()

        self.filehistory = wx.FileHistory()
        self.filehistory.UseMenu(self.recent_files)
        self.filehistory.AddFilesToMenu()
        
        ##==============================================================================##
        self.Bind(wx.EVT_MENU, self.onOpen, id=self.file_open.GetId())
        self.Bind(wx.EVT_MENU, self.SaveFile, id=self.save.GetId())
        self.Bind(wx.EVT_MENU, self.onOpenMultiple, id=self.open_multiple.GetId())
        self.Bind(wx.EVT_MENU, self.ReloadFile, id=self.reload_file.GetId())
        self.Bind(wx.EVT_MENU, self.openPrevious, id=self.previous.GetId())
        self.Bind(wx.EVT_MENU, self.exportZIP, id=self.export_zip.GetId())
        self.Bind(wx.EVT_MENU, self.RenameFiles, id=self.renamer.GetId())
        self.Bind(wx.EVT_MENU, self.CloseFile, id=self.close_file.GetId())
        self.Bind(wx.EVT_MENU, self.onQuit, id=self.quit_program.GetId())
        ##------------------------------------------------------------------------------##
        self.Bind(wx.EVT_MENU, self.zoomIn, id=self.zoom_in.GetId())
        self.Bind(wx.EVT_MENU, self.zoomOut, id=self.zoom_out.GetId())
        self.Bind(wx.EVT_MENU, self.zoomNormal, id=self.zoom_normal.GetId())        
        ##------------------------------------------------------------------------------##
        for menu_item in [
            self.undo, self.redo, self.copy, self.paste, self.cut, self.delete, self.select_all]:
            self.Bind(wx.EVT_MENU, self.EditText, menu_item)
        self.Bind(wx.EVT_MENU, self.OnShowFindReplace, id=self.find_replace.GetId())
        ##------------------------------------------------------------------------------##
        for menu_item in [
            self.italic, self.bold, self.underline, self.color, self.all_caps]:
            self.Bind(wx.EVT_MENU, self.formatText, menu_item)
        ##------------------------------------------------------------------------------##
        self.Bind(wx.EVT_MENU, self.changeEncoding, id=self.to_ansi.GetId())
        self.Bind(wx.EVT_MENU, self.changeEncoding, id=self.to_utf8.GetId())
        self.Bind(wx.EVT_MENU, self.changeEncoding, id=self.convert_encoding.GetId())
        self.Bind(wx.EVT_MENU, self.LatinToCyrillic, id=self.to_cyrillic.GetId())
        self.Bind(wx.EVT_MENU, self.CyrillicToLatin, id=self.cyr_to_lat_ansi.GetId())
        self.Bind(wx.EVT_MENU, self.CyrillicToLatin, id=self.cyr_to_lat_utf8.GetId())
        self.Bind(wx.EVT_MENU, self.OnFixerSettings, id=self.fix_subtitles.GetId())
        self.Bind(wx.EVT_MENU, self.MergeLines, id=self.merge.GetId())
        self.Bind(wx.EVT_MENU, self.onTranscribe, id=self.transcribe.GetId())
        self.Bind(wx.EVT_MENU, self.onCleanup, id=self.clean_up.GetId())
        self.Bind(wx.EVT_MENU, self.onRepSpecial, id=self.spec_replace.GetId())
        self.Bind(wx.EVT_MENU, self.ChangeManualy, id=self.change_manually.GetId())
        ##------------------------------------------------------------------------------##
        self.Bind(wx.EVT_MENU, self.OnMainSettings, id=self.settings_main.GetId())
        self.Bind(wx.EVT_MENU, self.editShortcuts, id=self.ShortcutEdit.GetId())
        self.Bind(wx.EVT_MENU, self.onMergerSettings, id=self.merger_settings.GetId())
        self.Bind(wx.EVT_MENU, self.onManual, id=self.manual.GetId())
        self.Bind(wx.EVT_MENU, self.onAbout, id=self.about.GetId())
        ##==============================================================================##
        self.Bind(wx.EVT_TOOL, self.onOpen, id=self.open.GetId())
        self.Bind(wx.EVT_TOOL, self.SaveFile, id=109)
        self.Bind(wx.EVT_TOOL, self.onQuit, id=101)
        self.Bind(wx.EVT_TOOL, self.changeEncoding, id=102)
        self.Bind(wx.EVT_TOOL, self.changeEncoding, id=103)
        self.Bind(wx.EVT_TOOL, self.LatinToCyrillic, id=104)
        self.Bind(wx.EVT_TOOL, self.onTranscribe, id=105)
        self.Bind(wx.EVT_TOOL, self.onRepSpecial, id=106)
        self.Bind(wx.EVT_TOOL, self.onCleanup, id=107)
        ##==============================================================================##
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.comboBox.Bind(wx.EVT_COMBOBOX, self.on_combo_box_changed)
        self.Text_1.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_MENU_RANGE, self.onFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9,)        
        self.Text_1.Bind(wx.EVT_TEXT, self.documentWasModified)
        self.Text_1.Bind(wx.EVT_TEXT_ENTER, self.setFontAndStyle)
        ##==============================================================================##
         
        MAIN_SETTINGS["CB_value"] = self.comboBox.GetValue()
        
        for i in FILE_HISTORY:
            if os.path.isfile(i):
                self.filehistory.AddFileToHistory(i)
            else:
                FILE_HISTORY.remove(i)
        self.toolBar1.EnableTool(109, False)
        
        self.default_font_size = self.get_current_font_size()
        self.zoom_factor = 1  # Zoom step increment for each wheel scroll
        
    def on_mouse_wheel(self, event):
        # Check if Ctrl key is pressed
        if event.ControlDown():
            # Determine the direction of the wheel scroll
            if event.GetWheelRotation() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
        else:
            event.Skip()
            
    def zoomIn(self, event=None):
        self.adjust_font_size(self.zoom_factor)
    
    def zoomOut(self, event=None):
        self.adjust_font_size(-self.zoom_factor)
    
    def zoomNormal(self, event=None):
        self.set_font_size(self.default_font_size)
    
    def adjust_font_size(self, increment):
        # Get the current range of text and increase the font size
        start, end = self.Text_1.GetSelectionRange()
        
        if start == end:  # If no selection, adjust the whole text
            start, end = 0, self.Text_1.GetLastPosition()
        
        # Create a RichTextRange for the selected range of text
        text_range = rt.RichTextRange(start, end)
        
        # Get the current text style
        attr = rt.RichTextAttr()
        self.Text_1.GetStyleForRange(text_range, attr)
        current_size = attr.GetFontSize()
        new_size = max(2, current_size + increment)  # Ensure font size >= 2
        
        # Update the font size and apply it
        attr.SetFontSize(new_size)
        self.Text_1.SetStyle(text_range.GetStart(), text_range.GetEnd(), attr)
        
    def set_font_size(self, size):
        # Set the font size for the entire text
        start, end = 0, self.Text_1.GetLastPosition()

        # Create a RichTextRange for the entire text
        text_range = rt.RichTextRange(start, end)

        # Get the current text style
        attr = rt.RichTextAttr()
        self.Text_1.GetStyleForRange(text_range, attr)

        # Set the font size to the default (or specified) size
        attr.SetFontSize(size)
        self.Text_1.SetStyle(text_range.GetStart(), text_range.GetEnd(), attr)    
        
    def get_current_font_size(self):
        # Get the current font size set in the RichTextCtrl
        current_font = self.Text_1.GetFont()
        return current_font.GetPointSize()    
    
    def handle_drop_files(self, filenames):
        # Create a list of files with the extensions .srt, .txt and .zip
        file_list = []
        for filename in filenames:
            if os.path.isdir(filename):
                for root, dirs, files in os.walk(filename):
                    for file in files:
                        if file.endswith(('.txt', '.zip', '.srt')):
                            file_list.append(os.path.join(root, file))
            else:
                if filename.endswith(('.txt', '.zip', '.srt')):
                    file_list.append(filename)
        self.OpenFiles(file_list)
        
    def displayFiles(self, files):
        # Set the text color to light gray
        color = "#a6acaf"
        curClr = MAIN_SETTINGS["key4"]["fontColour"]
        self.Text_1.Clear()
        # Iterate through the files and append them to the text edit widget with a corresponding number
        for i, file in enumerate(files):
            # Insert the number into the text edit widget
            number = f"{i + 1:02}.  "
            # Apply color to the number
            self.Text_1.BeginTextColour(color)
            self.Text_1.WriteText(number)
            self.Text_1.EndTextColour()
            # Apply default color to the filename
            self.Text_1.BeginTextColour(curClr)
            self.Text_1.WriteText(f" {basename(file.path)}\n")
            self.Text_1.EndTextColour()
        return len(files)

    def onOpen(self, event):
        # open a file dialog to select files
        wildcard = (
            "SubRip (*.zip; *.srt; *.txt)|*.zip;*.srt;*.txt|"
            "MicroDVD (*.sub)|*.sub|"
            "Text File (*.txt)|*.txt|"
            "All Files (*.*)|*.*"
        )
        last_opened = MAIN_SETTINGS["Directory"]
        if not exists(last_opened):
            last_opened = join(os.path.expanduser("~"), "Documents")        
        dlg = wx.FileDialog(
            self,
            message="Choose a file",
            defaultDir=last_opened,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN
            | wx.FD_MULTIPLE
            #| wx.FD_CHANGE_DIR
            | wx.FD_FILE_MUST_EXIST
            | wx.FD_PREVIEW,
        )
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            file_paths = dlg.GetPaths()
            if file_paths:
                MAIN_SETTINGS["Directory"] = normpath(dirname(file_paths[0]))
                self.OpenFiles(file_paths)
        dlg.Destroy()
        event.Skip()

    def OpenFiles(self, file_paths):
        if not isinstance(file_paths, list):
            file_paths = [file_paths]
        handler = FileHandler(input_files=file_paths)
        self.CYR = False
        if len(file_paths) == 1:
            text = handler.singleFileInput()
            self.filehistory.AddFileToHistory(file_paths[0])
            if text:
                self.Text_1.SetValue(text)
                self.CYR = (
                    handler.file_encoding in ("windows-1251", "utf-8", "utf-8-sig", "utf-16")
                    ) and checkCyrillicAlphabet(text) > 60
            if handler.real_path:
                real_path = handler.real_path
                self.SetStatusText(f"{basename(real_path)}", 0)
                self.single_file=handler.real_path
                self.file_enc = handler.file_encoding
                self.SetStatusText(f"{printEncoding(handler.file_encoding)} ", 1)
                self.highlight_parts(text)
                self.save.Enable(False)
                self.save_as.Enable(False)
                self.reload_file.Enable(True)
            if len(MULTI_FILE) > 1:
                file_count = self.displayFiles(MULTI_FILE)
                self.SetStatusText(f"Fajlova:  {file_count}", 1)
                self.SetStatusText("Ready for multiple files", 0)
        else:
            handler.multiFilesInput()
            file_count = self.displayFiles(MULTI_FILE)
            self.SetStatusText("Ready for multiple files", 0)
            self.SetStatusText(f"Fajlova:  {file_count}", 1)

    def onOpenMultiple(self, event):
        """"""
        dlg = MultiFiles(None)
        result = dlg.ShowModal()
        filelist = dlg.GetSelectedFiles()
        if result == True:
            if filelist:
                self.OpenFiles(filelist)
        dlg.Destroy()
        event.Skip()

    def highlight_parts(self, text, positions=None):
        if not positions:
            handler = ErrorsHandler(input_text=text)
            parts_start, parts_end = handler.findSurrogates()
        else:
            parts_start = positions[0]
            parts_end = positions[1]
            
        # Internal index and processing function inside highlight_parts
        def process_next_error(current_index):
            if current_index < len(parts_start):
                start = parts_start[current_index]
                end = parts_end[current_index]
    
                # Highlight in red
                self.Text_1.SetStyle(start, end, wx.TextAttr(wx.RED))
    
                # Set selection and scroll to the highlighted part
                self.Text_1.SetSelection(end, end)
                self.Text_1.ShowPosition(end)
    
                # Introduce a delay before processing the next
                if len(parts_start) < 45:
                    wx.CallLater(450, process_next_error, current_index + 1)  # 450ms delay for less than 45 errors
                elif len(parts_start) > 1000:
                    return  # Skip the process for large inputs
                else:
                    wx.CallLater(10, process_next_error, current_index + 1)   # 10ms delay for larger inputs
            else:
                # Finished processing all errors
                pass
    
        # Start the process with the first part
        process_next_error(0)                    

    def changeEncoding(self, event):
        """"""
        if event.Id == self.to_ansi.Id or event.Id == 102:
            new_encoding = "windows-1250"
            ext = MAIN_SETTINGS["key5"]["lat_ansi_srt"]
            if self.CYR is True:
                if self.showMessage is True:
                    self.cyr_message()
                return
        
        elif event.Id == self.to_utf8 or event.Id == 103:
            if self.utf8_BOM.IsChecked():
                new_encoding="utf-8-sig"
            else:
                new_encoding = "utf-8"
            ext = MAIN_SETTINGS["key5"]["lat_utf8_srt"]
        
        elif event.Id == self.convert_encoding.Id:
            new_encoding = self.comboBox.GetValue().strip()
            ext = new_encoding
            if new_encoding == "auto":
                wx.MessageBox(
                    f"Unknown encoding\n\nIzaberite kodiranje iz padajućeg menija,\n"
                    f"„auto“ nije regularan izbor kodiranja za ovu opciju",
                    "SubtitleConverter",
                )
                return
            if self.CYR is True and new_encoding in [
                "windows-1250", "windows-1252", "iso-8859-1", "iso-8859-2", "cp852", "ascii", "latin2"]:
                if self.showMessage is True:
                    self.cyr_message()
                return

        if len(MULTI_FILE) <= 1 and self.single_file:
            text = self.Text_1.GetValue()
            handler = DocumentHandler(
                self.single_file, text, new_encoding, ext, cyr=self.CYR
            )
            new_file_name = handler.write_new_file()
            if new_file_name:
                handler.handleErrors(new_file_name)
                self.OpenFiles(new_file_name)
                self.previous.Enable(True)
        elif len(MULTI_FILE) > 1:
            self.new_files.clear()
            self.cyr_utf8.clear()
            paths = [m.realpath for m in MULTI_FILE]
            for file_item in MULTI_FILE:
                text = normalizeText(file_item.enc, file_item.path)
                handler = DocumentHandler(file_item.realpath, text, new_encoding, ext, cyr=self.CYR)
                new_file_name = handler.write_new_file(multi=True, info=False, ask=False)
                if new_file_name:
                    self.new_files.append(new_file_name)
                    handler.handleErrors(new_file_name)
                    self.setStatus(status1=basename(file_item.path), encoding=new_encoding)
            self.setStatus("MultiFiles done", encoding=new_encoding, files=True)
            self.infoMessage("\n".join([basename(x) for x in self.new_files]))
            self.OpenFiles(paths)
        event.Skip()

    def LatinToCyrillic(self, event):
        """"""
        if event.Id == self.to_cyrillic.Id or event.Id == 104:
            ext = MAIN_SETTINGS["key5"]["cyr_ansi_srt"]
            comboBox_value = self.comboBox.GetValue().strip()
            if comboBox_value == "auto":
                new_encoding = "windows-1251"
            else:
                if comboBox_value not in ["windows-1251", "utf-16"]:
                    wx.MessageBox(
                        f"Encoding error\n\n"
                        f"Izabrano kodiranje „{comboBox_value}“ nije podržano!\n"
                        f"Za ćirilicu birajte „windows-1251“ ili „utf-16“",
                        "SubtitleConverter",
                    )
                    return
                else:
                    new_encoding = comboBox_value
        
        if len(MULTI_FILE) <= 1 and self.single_file:
            self.cyr_utf8.clear()
            text = self.Text_1.GetValue()
            handler = Transliteracija(self.single_file, text, new_encoding, ext)
            new_file_name = handler.write_transliterated()
            if new_file_name:
                handler.handleErrors(new_file_name)
                self.OpenFiles(new_file_name)
                self.previous.Enable(True)
                self.CYR = True
            new_utf8_file = handler.write_utf8_file()
            self.cyr_utf8.append(new_utf8_file)
        elif len(MULTI_FILE) > 1:
            self.new_files.clear()
            self.cyr_utf8.clear()
            for file_item in MULTI_FILE:
                text = normalizeText(file_encoding=file_item.enc, filepath=file_item.path)
                handler = Transliteracija(file_item.realpath, text, new_encoding, ext)
                new_file_name = handler.write_transliterated(multi=True, info=False, ask=False)
                if new_file_name:
                    handler.handleErrors(new_file_name)
                    self.new_files.append(new_file_name)
                    self.setStatus(status1=basename(file_item.path), encoding=new_encoding)
                new_utf8_file = handler.write_utf8_file(multi=True)
                if new_utf8_file:
                    self.cyr_utf8.append(new_utf8_file)
            self.CYR = True
            self.setStatus("MultiFiles done", encoding=new_encoding, files=True)
            self.infoMessage("\n".join([basename(x) for x in self.new_files]))            

    def CyrillicToLatin(self, event):
        """"""
        if event.Id == self.cyr_to_lat_ansi.Id:
            new_encoding = "windows-1250"
            ext = MAIN_SETTINGS["key5"]["lat_ansi_srt"]
        elif event.Id == self.cyr_to_lat_utf8.Id:
            if self.utf8_BOM.IsChecked():
                new_encoding="utf-8-sig"
            else:
                new_encoding = "utf-8"
            ext = MAIN_SETTINGS["key5"]["lat_utf8_srt"]

        if len(MULTI_FILE) <= 1 and self.single_file:
            text = self.Text_1.GetValue()
            handler = Transliteracija(self.single_file, text, new_encoding, ext, reversed_action=True)
            new_file_name = handler.write_transliterated()
            if new_file_name:
                handler.handleErrors(new_file_name)
                self.OpenFiles(new_file_name)
                self.previous.Enable()
        elif len(MULTI_FILE) > 1:
            self.new_files.clear()
            for file_item in MULTI_FILE:
                text = normalizeText(file_encoding=file_item.enc, filepath=file_item.path)
                handler = Transliteracija(file_item.realpath, text, new_encoding, ext, reversed_action=True)
                new_file_name = handler.write_transliterated(multi=True, info=False, ask=False)
                if new_file_name:
                    handler.handleErrors(new_file_name)
                    self.new_files.append(new_file_name)
                    self.setStatus(status1=basename(file_item.path), encoding=new_encoding)
            self.CYR = False
            self.setStatus("MultiFiles done", encoding=new_encoding, files=True)
            self.infoMessage("\n".join([basename(x) for x in self.new_files]))
        event.Skip()

    def exportZIP(self, event):

        ext_4 = MAIN_SETTINGS["key5"]["lat_utf8_srt"]

        if len(MULTI_FILE) <= 1 and self.single_file:
            FileToSave = os.path.splitext(self.single_file)[0]
            fileName = self.fileSave_dialog(FileToSave, "Save Zip file")
            if fileName:
                handler = ExportZipFile.ExportZip(
                    [self.single_file],
                    self.cyr_utf8,
                    [FILE_HISTORY[-2]],
                    utf8_ext=ext_4,
                )
                all_paths = handler.collectInfoData()
                dlg = MultiChoice(self, basename(fileName), "Select files", all_paths)
                if dlg.ShowModal() == wx.ID_OK:
                    selected = dlg.GetSelections()
                    dlg.Destroy()
                    if not selected:
                        return
                    result = handler.WriteZipFile(fileName, selected)
                    if result is True:
                        self.messageInformation(fileName)
        elif len(MULTI_FILE) > 1:
            ofiles = [MULTI_FILE[x].path for x in range(len(MULTI_FILE))]
            if self.CYR is True and self.cyr_utf8:
                handler = ExportZipFile.ExportZip(
                    self.new_files, self.cyr_utf8, ofiles, utf8_ext=ext_4)
                all_paths = handler.CreateInfo()
                FileToSave = handler.file_name(MULTI_FILE[0].path)
                fileName = self.fileSave_dialog(FileToSave, "Save Zip file")
                new_zipFile_name = fileName
                dlg = ZipStructure(
                    None, dirname(FileToSave), basename(fileName), all_paths
                )
                retcode = dlg.ShowModal()
                selection = dlg.GetSelections()
                if retcode != True:
                    return
                folders = dlg.makeFolder()
                result = handler.WriteZipFile(
                    new_zipFile_name, selections=selection, folders=folders
                )
                if result is True:
                    self.messageInformation(new_zipFile_name)
            else:
                handler = ExportZipFile.ExportZip(input_1=self.new_files)
                FileToSave = handler.file_name(MULTI_FILE[0].path)
                fileName = self.fileSave_dialog(FileToSave, "Save Zip file")
                selection = [1 for x in handler.collectInfoData()]
                result = handler.WriteZipFile(
                    fileName, selections=selection, folders=False
                )
                if result is True:
                    self.messageInformation(fileName)
        event.Skip()
    
    @staticmethod
    def fileSave_dialog(FileToSave, message, wildcards=None):
        """"""
        if not wildcards:
            wildcards="Zip files (*.zip)|*.zip|All files (*.*)|*.*"
        with wx.FileDialog(
                None, 
                message, 
                defaultDir=dirname(FileToSave),  # Set the default directory
                defaultFile=basename(FileToSave),  # Set the default file name
                wildcard=wildcards,
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # User canceled the dialog
            return fileDialog.GetPath()        
    
    def cyr_message(self):
        """"""
        dlg = wx.RichMessageDialog(
            None,
            f"UnicodeDecode Error\n\n"
            f"Tekst je većinom ćirilica.\n"
            f"Koristite opcije za transliteraciju teksta.",
            "SubtitleConverter"
        )
        dlg.ShowCheckBox("Sakrij ovaj dijalog")
        dlg.ShowModal()
        if dlg.IsCheckBoxChecked():
            self.showMessage = False        
        
    @staticmethod
    def messageInformation(path):
        wx.MessageBox(
            message=f"Fajl je uspešno sačuvan\n\n{basename(path)}",
            caption="SubtitleConverter",
        )
        
    @staticmethod
    def infoMessage(message_):
        wx.MessageBox(
            message=f"Files processed:\n\n{message_}", caption="Subtitle Converter"
        )
    
    def displayText(self, intext=[]):
        """"""
        caller_method = inspect.stack()[1].function
        if self.hideDialog and self.lastCaller == caller_method:
            return
        dlg = wx.RichMessageDialog(self, "".join(intext), "SubtitleConverter", style=wx.OK)
        dlg.ShowCheckBox("Sakrij ovaj dijalog")

        if dlg.ShowModal() == wx.ID_OK:
            if dlg.IsCheckBoxChecked():
                self.hideDialog = True
            dlg.Destroy()

        self.lastCaller = caller_method        
    
    def RenameFiles(self, event):
        """"""
        dlg = RenameFiles(None)
        dlg.ShowModal()
        event.Skip()        

    def OnFixerSettings(self, event):
        dlg = FixerSettings(None)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == True:
            self.FixSubtiles()
        event.Skip()

    def FixSubtiles(self):

        ext_f = MAIN_SETTINGS['key5']['fixed_subs']

        if len(MULTI_FILE) < 1 and self.single_file:
            text = self.Text_1.GetValue()
            fixer = SubtitleFixer(text_in=text)
            text = fixer.FixSubtileText()
            handler = DocumentHandler(self.single_file, text, self.file_enc, ext_f)
            new_file_path = handler.write_new_file(info=False, ask=False)
            if new_file_path:
                self.OpenFiles(new_file_path)
                self.previous.Enable(True)
        elif len(MULTI_FILE) > 1:
            self.new_files.clear()
            self.cyr_utf8.clear()
            for file_item in MULTI_FILE:
                text = normalizeText(file_item.enc, file_item.path)
                fixer = SubtitleFixer(text_in=text, multi=True)
                text = fixer.FixSubtileText()
                handler = DocumentHandler(file_item.realpath, text, file_item.enc, ext_f, cyr=self.CYR)
                new_file_name = handler.write_new_file(multi=True, info=False, ask=False)
                if new_file_name:
                    self.new_files.append(new_file_name)
                    handler.handleErrors(new_file_name)
                    self.setStatus(status1=basename(file_item.path), encoding=file_item.enc)
            self.setStatus("MultiFiles done", encoding=self.file_enc, files=True)
            self.infoMessage("\n".join([basename(x) for x in self.new_files]))            
            
    def MergeLines(self, event):

        lineLenght = MAIN_SETTINGS['key2']['l_lenght']
        maxChar = MAIN_SETTINGS['key2']['m_char']
        maxGap = MAIN_SETTINGS['key2']['m_gap']
        f_suffix = MAIN_SETTINGS['key2']['f_suffix']

        text = self.Text_1.GetValue()
        subs_a = list(srt.parse(text, ignore_errors=True))

        if len(subs_a) > 0:
            myMerger(subs_in=subs_a, max_time=lineLenght, max_char=maxChar, _gap=maxGap)

            b1 = len(list(srt.parse(WORK_TEXT.getvalue(), ignore_errors=True)))
            a1 = len(subs_a)

            text = WORK_TEXT.getvalue()
            text = srt.compose(srt.parse(text, ignore_errors=True))

            handler = DocumentHandler(
                self.single_file, text, self.file_enc, f_suffix, self.CYR
            )
            new_file_path = handler.write_new_file(info=False, ask=False)
            if new_file_path:
                self.OpenFiles(new_file_path)
                self.previous.Enable(True)
            try:
                prf = format(((a1 - b1) / a1 * 100), '.2f')
            except ZeroDivisionError as e:
                logger.debug(f"Merger Error: {e}")
            else:
                logger.debug(f"Merger: Spojenih linija: {a1-b1}, ili {prf} %")
                wx.MessageBox(
                    f"Merdžer\n\nSpojenih linija: {a1-b1}, ili {prf} %",
                    "SubtitleConverter",
                )
        event.Skip()
                
    def onTranscribe(self, event):

        ext = MAIN_SETTINGS['key5']['transcribe']

        if self.utf8_BOM.IsChecked():
            new_encoding="utf-8-sig"
        else:
            new_encoding = "utf-8"

        if len(MULTI_FILE) < 1 and self.single_file:
            text = self.Text_1.GetValue()

            handler = DocumentHandler(self.single_file, text, new_encoding, ext, cyr=self.CYR)
            text = handler.rplStr(text)
            num, text = handler.zameniImena(text)

            if num > 28 or (num < 28 and num > 2):
                wx.MessageBox(f"Zamenjenih objekata\nukupno [ {num} ]", "SubtitleConverter")
                
            new_file_path = handler.write_new_file(text=text, info=False, ask=False)
            if new_file_path:
                handler.handleErrors(new_file_path)
                self.OpenFiles(new_file_path)
                self.reload_file.Enable(True)
        event.Skip()

    def onCleanup(self, event):

        ext =  MAIN_SETTINGS['key5']['cleanup']
        text = self.Text_1.GetValue()

        try:
            subs = list(srt.parse(text, ignore_errors=True))
            NUM1 = len(subs)
            subs = srt.compose(subs)

            cleaner = SubtitleFixer()

            text = cleaner.cleanUp(subs)

            N2, text_s = cleaner.cleanLine(text)

            text = cleaner.cleanUp(text_s)

            D2, text_s = cleaner.cleanLine(text)            

            writer = DocumentHandler(self.single_file, text_s, self.file_enc, ext, self.CYR)
            new_file_path = writer.write_new_file(info=False, ask=False)
            logger.debug(f"CleanUp _1: {sys.exc_info()}")

            if new_file_path:
                if D2 == 0 and N2 == 0:
                    message = "Subtitle clean\nno changes made."
                else:
                    if D2 == 0 and N2 > 0:
                        D2 = N2
                    message = f"Subtitles deleted: [{NUM1-D2} ]"
                wx.MessageBox(message, "SubtitleConverter")
                self.OpenFiles(new_file_path)
                self.reload_file.Enable(True)
        except Exception as e:
            logger.debug(f"Cleanup: {e}")
            return
        event.Skip()

    def onRepSpecial(self, event):

        try:
            text = self.Text_1.GetValue()
            ext = splitext(splitext(self.single_file)[0])[1].strip(".")
            if re.search(r"(x|h)\.?264|ION(10|265)|\d{3,4}", ext, re.I) or len(ext) > 8:
                ext = ""
            handler = SubtitleFixer()
            num, text_o = handler.doReplace(text)

            writer = DocumentHandler(
                self.single_file, text_o, self.file_enc, ext, self.CYR
            )
            new_file_path = writer.write_new_file(multi=False, info=False, ask=False)
            if new_file_path:
                self.OpenFiles(new_file_path)
                self.reload_file.Enable(True)
                wx.MessageBox(
                    f"Zamenjenih objekata\nukupno [ {num} ]", "SubtitleConverter"
                )
        except Exception as e:
            logger.debug(f"ReplaceSpecial Error: {e}")
            return
        event.Skip()

    def SaveFile(self, event):
        """"""
        FileToSave = self.single_file
        Enc_saved = self.file_enc
        if not FileToSave:
            self.SaveAs(event)
        else:
            text = self.Text_1.GetValue()
            writer = DocumentHandler(input_text=text, encoding=Enc_saved)
            res = writer.WriteFile(text_in=text, file_path=FileToSave, info=False, ask=False)
            self.setStatus(basename(FileToSave), encoding=Enc_saved)
            if res:
                self.save.Enable(False)
                self.toolBar1.EnableTool(109, False)
        event.Skip()

    def SaveAs(self, event):
        """"""
        FileToSave = self.single_file or "Untitled.txt"
        Enc_saved = self.file_enc or "utf-8"
        fileName = self.fileSave_dialog(
            FileToSave, "Save File", "SubRip (*.srt *.txt);; All files (*.*)"
        )
        if fileName:
            text = self.Text_1.GetValue()
            writer = DocumentHandler(encoding=Enc_saved)
            res = writer.WriteFile(text_in=text, file_path=fileName, ask=False)
            self.setStatus(basename(fileName), encoding=Enc_saved)
            self.filehistory.AddFileToHistory(fileName)
            if res:
                self.save_as.Enable(False)
        event.Skip()

    def CloseFile(self, event):
        """"""
        self.Text_1.SetValue("")
        self.single_file = None
        self.save.Enable(False)
        self.save_as.Enable(False)
        self.toolBar1.EnableTool(109, False)
        self.setStatus("SubtitleConverter is ready", encoding="")
        event.Skip()

    def documentWasModified(self, event):
        self.save.Enable(True)
        self.save_as.Enable(True)
        self.undo.Enable(True)
        self.toolBar1.EnableTool(109, True)
        event.Skip()

    def ReloadFile(self, event):
        """"""
        self.OpenFiles(self.single_file)
        event.Skip()

    def openPrevious(self, event):
        """"""
        previous_file = FILE_HISTORY[-2]
        self.OpenFiles(previous_file)
        self.previous.Enable(False)
        event.Skip()

    def EditText(self, event):
        """"""
        if event.Id == self.undo.Id:
            if not self.Text_1.CanUndo():
                self.undo.Enable(False)
            else:
                self.Text_1.Undo()
                self.redo.Enable(True)
        
        elif event.Id == self.redo.Id:
            if not self.Text_1.CanRedo():
                self.redo.Enable(False)
            else:
                self.Text_1.Redo()
        
        elif event.Id == self.copy.Id:
            if self.Text_1.CanCopy:
                self.Text_1.Copy()
        
        elif event.Id == self.paste.Id:
            if self.Text_1.CanPaste:
                self.Text_1.Paste()
                
        elif event.Id == self.cut.Id:
            if self.Text_1.CanCut:
                self.Text_1.Cut()
        
        elif event.Id == self.select_all.Id:
            self.Text_1.SelectAll()
        
        elif event.Id == self.delete.Id:
            selection_range = self.Text_1.GetSelectionRange()
            if selection_range[0] != selection_range[1]:
                self.Text_1.Delete(selection_range)
        event.Skip()
        
    def onFileHistory(self, event):
        # get the file based on the menu ID
        fileNum = event.GetId() - wx.ID_FILE1
        file_path = self.filehistory.GetHistoryFile(fileNum)
        if not exists(file_path):
            logger.debug(f"FileHistory: not found {file_path}")
            return
        self.OpenFiles(file_path)
        self.filehistory.AddFileToHistory(file_path)
        event.Skip()

    def onMergerSettings(self, event):
        dlg = MergerSettings()
        dlg.ShowModal()
        event.Skip()

    def OnMainSettings(self, event):
        settings_dlg = SettingsDialog(None)
        result = settings_dlg.ShowModal()
        curClr = settings_dlg.GetColor()
        curFont = settings_dlg.GetFont()
        settings_dlg.Destroy()
        if result == True:
            with open(main_settings_file, "w") as wf:
                wf.write(json.dumps(MAIN_SETTINGS, ensure_ascii=False, indent=4))
            shutil.copyfile(main_settings_file, main_settings_file+".bak")
            self.setFontAndStyle(curFont,  curClr)

    def on_combo_box_changed(self, event):
        """
        This function will be called when the user selects a new item in the combo box
        """
        MAIN_SETTINGS["CB_value"] = self.comboBox.GetValue()
        event.Skip()

    def setStatus(self, status1, encoding, files=False):
        self.SetStatusText("")
        self.SetStatusText(status1)
        self.SetStatusText("", 1)
        if files:
            if not encoding:
                encoding = "Multi-enc"
            M2 = f" Fajlova:  {self.Text_1.GetNumberOfLines()-1}" 
            self.SetStatusText(f"{printEncoding(encoding)} – {M2}", 1)
        else:
            self.SetStatusText(f"{printEncoding(encoding)} ", 1)

    def apply_style(self, selection, style_keyword, color_rgb=None):
        """
        Applies a style around the selected text based on a keyword.
    
        :param selection: The selected text to style.
        :param style_keyword: The keyword for the style (e.g., "italic", "bold", "underline").
        :raises ValueError: If the style_keyword is not valid.
        """
        if color_rgb:
            color_id = self.hex_from_rgb(color_rgb)
        else:
            color_id = "#000000"
        # Mapping of keywords to tags and methods
        style_data = {
            "italic": ("<i>", "</i>", self.Text_1.BeginItalic, self.Text_1.EndItalic),
            "bold": ("<b>", "</b>", self.Text_1.BeginBold, self.Text_1.EndBold),
            "underline": ("<u>", "</u>", self.Text_1.BeginUnderline, self.Text_1.EndUnderline),
            "color": (f"<font color='{color_id}'>", "</font>", self.Text_1.BeginTextColour, self.Text_1.EndTextColour),
        }
    
        if style_keyword not in style_data:
            logger.debug(f"Error: The style '{style_keyword}' is not recognized.")
            return
    
        open_tag, close_tag, begin_style_method, end_style_method = style_data[style_keyword]
        
        if selection and open_tag and close_tag and begin_style_method and end_style_method:
            self.Text_1.DeleteSelectedContent()
            self.Text_1.Freeze()
    
            self.Text_1.WriteText(open_tag)
            if color_rgb:
                begin_style_method(color_rgb)
            else:
                begin_style_method()
    
            self.Text_1.WriteText(selection)
    
            end_style_method()
            self.Text_1.WriteText(close_tag)
    
            self.Text_1.Thaw()
            
    def formatText(self, event):
        """Sets the formating of the selected text."""

        selection = self.Text_1.GetStringSelection()

        if not selection:
            wx.MessageBox(
                f"Ništa nije selektovano?\n\n" f"Selektujte tekst za formatiranje",
                "Formatiranje teksta",
            )
            return

        if event.Id == self.italic.Id:
            self.apply_style(selection, "italic")

        elif event.Id == self.bold.Id:
            self.apply_style(selection, "bold")

        elif event.Id == self.underline.Id:
            self.apply_style(selection, "underline")

        elif event.Id == self.color.Id:
            color = self.getColor()
            self.apply_style(selection, "color", color_rgb=color)

        elif event.Id == self.all_caps.Id:
            self.Text_1.DeleteSelectedContent()
            self.Text_1.Freeze()
            self.Text_1.WriteText(selection.upper())
            self.Text_1.Thaw()

        event.Skip()
    
    @staticmethod
    def hex_from_rgb(rgb):
        """
        Converts an RGB tuple to HEX format.
        :param rgb: A tuple of RGB values, e.g., (255, 0, 0)
        :return: The HEX color string, e.g., "#FF0000"
        """
        return '#{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])    

    @staticmethod
    def getColor():
        """Return the color in RGB format."""
        dlg = wx.ColourDialog(None)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour().Get(includeAlpha=False)
            return color
        dlg.Destroy()
        
    def setFontAndStyle(self, font=None, color=None):
        """Sets the font and style of the wx.richtext widget."""
        if not font:
            font = wx.Font(
                MAIN_SETTINGS["key4"]['fontSize'],
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                MAIN_SETTINGS["key4"]['weight'],
                0,
                MAIN_SETTINGS["key4"]['new_font'],
            )
        if not color:
            color = MAIN_SETTINGS["key4"]["fontColour"]
        
        attr = rt.RichTextAttr()
        attr.SetFont(font)
        attr.SetTextColour(wx.Colour(color))
        self.Text_1.SetDefaultStyle(attr)
        start, end = 0, self.Text_1.GetLastPosition() # From start to end
        self.Text_1.SetStyle(start, end, attr)        
        self.Text_1.Refresh()
        self.Text_1.Update()

    def onQuit(self, event):
        self.writeSettings()
        self.writeFileHistory(FILE_HISTORY)
        self.removeTmpFiles()
        self.Destroy()
        event.Skip()
    
    def onClose(self, event):
        self.writeSettings()
        self.writeFileHistory(FILE_HISTORY)
        self.removeTmpFiles()
        self.Destroy()
        event.Skip()
        
    def writeSettings(self):
        width = self.GetSize().GetWidth()
        height = self.GetSize().GetHeight()        
        MAIN_SETTINGS["FrameSize"] = {"W": width, "H": height}
        MAIN_SETTINGS["Preferences"]["bom_utf8"] = self.utf8_BOM.IsChecked()
        MAIN_SETTINGS["Preferences"]["utf8_txt"] = self.utf8_TXT.IsChecked()        
        with open(main_settings_file, "w", encoding="utf-8") as wf:
            wf.write(json.dumps(MAIN_SETTINGS, ensure_ascii=False, indent=4))
        shutil.copyfile(main_settings_file, main_settings_file+".bak")        
        
    def writeFileHistory(self, hfile_list):
        """"""
        logfile = open(log_file_history, "w", encoding="utf-8", newline="\r\n")
        log_list = []
        for path in hfile_list:
            if os.path.exists(path):
                if path not in log_list:
                    log_list.append(path)
        for file_path in log_list:
            logfile.write(normpath(file_path) + "\n")
        logfile.close()

    def removeTmpFiles(self):
        directory = 'tmp'
        num_files_to_keep = 20
        files = os.listdir(directory)
        files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)))
        for file in files[:-num_files_to_keep]:
            os.remove(os.path.join(directory, file))
            
    def onShortcutChanged(self, event):
        shortcut = event.GetShortcut()
        newAccel = event.GetAccelerator()
        if newAccel == "Disabled":
            newAccel = ""
        self.sc[shortcut.label] = newAccel
        event.Skip()

    def editShortcuts(self, event):

        dlg = SE.ShortcutEditor(self)
        dlg.FromMenuBar(self)
        dlg.Bind(SE.EVT_SHORTCUT_CHANGED, self.onShortcutChanged)

        if dlg.ShowModal() == wx.ID_OK:
            dlg.ToMenuBar(self)
            try:
                #shortcutsKeys.update([(key, self.sc[key]) for key in self.sc.keys()])
                shortcutsKeys.update(self.sc)

                i_list = list(shortcutsKeys.keys())
                
                cfg_file = join("resources", "var", "shortcut_keys.cfg") 

                with open(cfg_file, "r", encoding="utf-8") as cf:
                    new_f = ""
                    for line in cf:
                        if any(line.startswith(n) for n in i_list):
                            x = line.split("=")
                            s = f"{x[0].strip()}={shortcutsKeys[x[0].strip()]}\n"
                            new_f += s
                        else:
                            new_f += line
                with open(join(cfg_file), "w",encoding="utf-8", newline="\r\n") as cf:
                    cf.write(new_f)
            except Exception as e:
                logger.debug(f"editShortcuts: {e}")
            dlg.Destroy()
        event.Skip()
    
    @staticmethod    
    def getPositions(current_text, values):
        """"""
        pos_start = []
        pos_end = []
        for x in set(values):
            ctext = re.compile(r"\b" + x + r"\b")
            for match in re.finditer(ctext, current_text):
                pos_start.append(match.start())
                pos_end.append(match.end())
        return [pos_start, pos_end]

    def ChangeManualy(self, event):
        """"""
        text = self.Text_1.GetValue()
        frame = FindReplace(self, on_done=self.on_change_done, subtitles=list(srt.parse(text)))
        frame.Show()
        event.Skip()
        
    def on_change_done(self, data_list, current_text):
        self.Text_1.SetValue(current_text)
        _positions = self.getPositions(current_text, data_list)
        self.highlight_parts(text=None, positions=_positions)    
        
    def BindFindEvents(self, win):
        """Bind the find and replace events to the dialog."""
        win.Bind(wx.EVT_FIND, self.OnFind)
        win.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        win.Bind(wx.EVT_FIND_REPLACE, self.OnFind)
        win.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnFind)
        win.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)

    def OnShowFindReplace(self, event):
        """Show the Find & Replace dialog."""
        if not self.find_dialog:
            self.find_dialog = wx.FindReplaceDialog(
                self, self.findData, "Find & Replace", wx.FR_REPLACEDIALOG
            )
            self.BindFindEvents(self.find_dialog)
        self.find_dialog.Show(True)

    def OnFind(self, evt):
        """Handle all find/replace events."""
        map_events = {
            wx.wxEVT_COMMAND_FIND: "FIND",
            wx.wxEVT_COMMAND_FIND_NEXT: "FIND_NEXT",
            wx.wxEVT_COMMAND_FIND_REPLACE: "REPLACE",
            wx.wxEVT_COMMAND_FIND_REPLACE_ALL: "REPLACE_ALL",
        }
        event_type = evt.GetEventType()
        event_name = map_events.get(event_type, "UNKNOWN")

        find_string = self.findData.GetFindString()
        replace_string = self.findData.GetReplaceString()
        text = self.Text_1.GetValue()
        start_pos = self.Text_1.GetInsertionPoint()

        flags = evt.GetFlags()

        # Apply match case logic
        if not (flags & wx.FR_MATCHCASE):
            find_string = find_string.lower()
            text = text.lower()

        if event_name == "FIND" or event_name == "FIND_NEXT":
            found_pos = -1  # Default to not found

            while start_pos < len(text):
                found_pos = text.find(find_string, start_pos)

                if found_pos == -1:
                    wx.MessageBox(
                        f"No more occurrences of '{find_string}' found!",
                        "Info",
                        wx.OK | wx.ICON_INFORMATION,
                    )
                    self.Text_1.SetInsertionPoint(0)  # Reset to start of the document
                    return

                if flags & wx.FR_WHOLEWORD:
                    before = found_pos - 1
                    after = found_pos + len(find_string)

                    if (before >= 0 and text[before].isalnum()) or (
                        after < len(text) and text[after].isalnum()
                    ):
                        start_pos = after
                        continue
                break

            if found_pos != -1:
                self.Text_1.SetInsertionPoint(found_pos)
                self.Text_1.ShowPosition(found_pos)
                self.Text_1.SetSelection(found_pos, found_pos + len(find_string))

        elif event_name == "REPLACE":
            selection_start, selection_end = self.Text_1.GetSelectionRange().Get()
            selected_text = self.Text_1.GetStringSelection()
            
            # Case-insensitive check
            if (flags & wx.FR_MATCHCASE and selected_text == find_string) or (
                not (flags & wx.FR_MATCHCASE) and selected_text.lower() == find_string.lower()
            ):
                self.Text_1.DeleteSelectedContent()
                self.Text_1.WriteText(replace_string)
                self.Text_1.SetInsertionPoint(selection_start + len(replace_string))
            else:
                wx.MessageBox(
                    f"No text selected or selected text does not match '{find_string}'",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
        
        elif event_name == "REPLACE_ALL":
            start_pos = 0
            while start_pos < len(text):
                # always search in lowercase when Match Case is off
                search_text = text if (flags & wx.FR_MATCHCASE) else text.lower()
                search_term = find_string if (flags & wx.FR_MATCHCASE) else find_string.lower()
        
                found_pos = search_text.find(search_term, start_pos)
                if found_pos == -1:
                    break
        
                if flags & wx.FR_WHOLEWORD:
                    before = found_pos - 1
                    after = found_pos + len(find_string)
                    if (before >= 0 and text[before].isalnum()) or (
                        after < len(text) and text[after].isalnum()):
                        start_pos = after
                        continue
        
                self.Text_1.SetSelection(found_pos, found_pos + len(find_string))
                self.Text_1.DeleteSelectedContent()
                self.Text_1.WriteText(replace_string)
                start_pos = found_pos + len(replace_string)

    def OnFindClose(self, event):
        """Close the find dialog when the user finishes."""
        event.GetDialog().Destroy()
        self.find_dialog = None
        
    def onManual(self, event):
        dlg = MyManual(None)
        dlg.Show()
        event.Skip()
        

    def onAbout(self, event):
        """"""
        AboutDlg = wx.MessageDialog(
            self,
            f"SubtitleConverter {VERSION}\n\n"
            f"Program za rad sa *.srt i tekstualnim fajlovima\n"
            f"Radi se promena enkodinga i preslovljavanje iz Latinice u Ćirilicu\n"
            f"i druga uređivanja teksta i titlova.\n"
            f"Autor: @padovaSR\n"
            f"https://github.com/padovaSR\n"
            f"License: GNU GPL v2",
            "About the Program",
            wx.OK | wx.ICON_INFORMATION,
        )
        AboutDlg.ShowModal()        
        event.Skip()
        

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainWindow(None)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True    

if __name__ == "__main__":
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    app = MyApp(0)
    app.MainLoop()
