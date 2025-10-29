# -*- coding: utf-8 -*-


import glob
import os
from os.path import join, basename, splitext
import re
import srt
from srt import Subtitle
import shutil
from collections import defaultdict 
from resources.DictHandle import Dictionaries
from resources.transliterate import cyr_to_lat
from resources.translate_text import translate_sync, lang_dict
from resources.shortcut_parser import update_accelerators
from resources.undoable_textctrl import UndoableTextCtrl
from resources.subtitles_model import SubtitlesModel
from settings import I_PATH, MAIN_SETTINGS
import itertools
try:
    from agw import shortcuteditor as SE
except ImportError: 
    import wx.lib.agw.shortcuteditor as SE

import logging.config


import wx
import wx.dataview as dv
from wx.lib.splitter import MultiSplitterWindow

logger = logging.getLogger(__name__)


def getSubtitles(filein):
    """"""
    with open(filein, "r", encoding="utf-8") as f:
        return f.read()


class FindReplace(wx.Frame):
    def __init__(self, parent, on_done=None, subtitles=None):
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE)
        
        self.on_done = on_done
        self.subtitles = subtitles
        
        try:
            data_dict = MAIN_SETTINGS["Manually"]
            self.SetSize((data_dict["W"], data_dict["H"]))
        except:
            self.SetSize((540, 621))
        self.SetTitle("Find-Replace manually")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(join(I_PATH,"edit-find-replace.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        SetFont = Dictionaries().dict_fromFile(join("resources", "var", "I_dialog.conf"), "=")
        tFont = defaultdict(str)
        tFont.update(SetFont)        

        # --- Menubar ---
        self.menubar = wx.MenuBar()
        
        # --- Edit menu ---
        self.edit_menu = wx.Menu()
        sKey = MAIN_SETTINGS["FrameShortcuts"]
        self.undo_menu = self.edit_menu.Append(wx.ID_ANY, f"Undo\t{sKey["Undo"]}")
        self.redo_menu = self.edit_menu.Append(wx.ID_ANY, f"Redo\t{sKey["Redo"]}")
        self.edit_menu.AppendSeparator()
        self.accept_menu = self.edit_menu.Append(wx.ID_ANY, f"Accept\t{sKey["Accept"]}")
        self.ignore_menu = self.edit_menu.Append(wx.ID_ANY, f"Ignore\t{sKey["Ignore"]}")
        self.replaceall_menu = self.edit_menu.Append(wx.ID_ANY, f"ReplaceAll\t{sKey["ReplaceAll"]}")
        self.ignoreall_menu = self.edit_menu.Append(wx.ID_ANY, f"IgnoreAll\t{sKey["IgnoreAll"]}")
        self.add_menu = self.edit_menu.Append(wx.ID_ANY, f"Add\t{sKey["Add"]}")
        self.ok_menu = self.edit_menu.Append(wx.ID_ANY, f"Ok\t{sKey["Ok"]}")
        self.cancel_menu = self.edit_menu.Append(wx.ID_ANY, f"Cancel\t{sKey["Cancel"]}")
        self.edit_menu.AppendSeparator()
        self.replace_menu = self.edit_menu.Append(wx.ID_ANY, f"Replace\t{sKey["Replace"]}")
        self.skip_menu = self.edit_menu.Append(wx.ID_ANY, f"Skip\t{sKey["Skip"]}")
        self.next_menu = self.edit_menu.Append(wx.ID_ANY, f"Next\t{sKey["Next"]}")
        self.edit_menu.AppendSeparator()
        self.translate_menu = self.edit_menu.Append(wx.ID_ANY, f"Translate\t{sKey["Translate"]}")

        self.menubar.Append(self.edit_menu, "&Edit")
        
        # --- Preferences menu ---
        self.preferences_menu = wx.Menu()
        self.translator_menu = self.preferences_menu.AppendCheckItem(wx.ID_ANY, "Translator")
        self.translator_menu.Check(MAIN_SETTINGS["Manually"]["Translate"])
        self.translator_menu.SetHelp("Enable-Disable translator")
        
        self.source = wx.Menu()
        self.english = self.source.AppendCheckItem(wx.ID_ANY, "Engleski")
        self.russian = self.source.AppendCheckItem(wx.ID_ANY, "Ruski")
        self.slovenian_ = self.source.AppendCheckItem(wx.ID_ANY, "Slovenački")
        self.macedonian_ = self.source.AppendCheckItem(wx.ID_ANY, "Makedonski")
        self.croatian_ = self.source.AppendCheckItem(wx.ID_ANY, "Hrvatski")
        self.bosnian = self.source.AppendCheckItem(wx.ID_ANY, "Bosanski")
        self.source_item = self.preferences_menu.AppendSubMenu(self.source, "Source")
        
        self.destination = wx.Menu()
        self.serbian = self.destination.AppendCheckItem(wx.ID_ANY, "Srpski")
        self.croatian = self.destination.AppendCheckItem(wx.ID_ANY, "Hrvatski")
        self.slovenian = self.destination.AppendCheckItem(wx.ID_ANY, "Slovenački")
        self.macedonian = self.destination.AppendCheckItem(wx.ID_ANY, "Makedonski")
        self.destination_item = self.preferences_menu.AppendSubMenu(self.destination, "Destination")
        
        self.preferences_menu.AppendSeparator()
        self.lock_menu = self.preferences_menu.AppendCheckItem(wx.ID_ANY, f"Focus lock\t{sKey["Lock focus"]}")
        self.lock_menu.Check(MAIN_SETTINGS["Manually"]["LockFocus"])
        self.lock_menu.SetHelp("Lock focus on text edit")
        self.preferences_menu.AppendSeparator()        
        self.auto_menu = self.preferences_menu.AppendCheckItem(wx.ID_ANY, "Auto Replace")
        self.auto_menu.Check(MAIN_SETTINGS["Manually"]["Auto_replace"])
        self.auto_menu.SetHelp("Enable-Disable Auto Replace")
        
        self.preferences_menu.AppendSeparator()
        
        self.shortcut_menu = self.preferences_menu.Append(wx.ID_ANY, "Shortcut Editor")
        self.menubar.Append(self.preferences_menu, "&Preferences")
        
        # Apply menubar to frame
        self.SetMenuBar(self.menubar)
                
        # --- Outer panel and sizer ---
        panel = wx.Panel(self)
        outer_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- MultiSplitter ---
        self.splitter = MultiSplitterWindow(panel, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetOrientation(wx.VERTICAL)
        self.splitter.SetMinimumPaneSize(40)

        # --- First (top) pane ---
        top_panel = wx.Panel(self.splitter)
        top_vsizer = wx.BoxSizer(wx.VERTICAL)

        # Row 1: Choice + Radio
        row1 = wx.BoxSizer(wx.HORIZONTAL)
        
        # get dictionary files
        dict_dir = "dictionaries"
        file_paths = glob.glob(os.path.join(dict_dir, "*.txt"))

        # map base name for display
        self.file_map = {splitext(basename(p))[0]: p for p in file_paths}
        
        choices = list(self.file_map.keys())        
        self.dict_choice = wx.Choice(top_panel, choices=choices)
        try:
            dictionary = choices.index("Dictionary-1")
        except:
            dictionary = 0
        self.dict_choice.SetSelection(dictionary)
        choice = self.dict_choice.GetStringSelection()
        self.dname = self.file_map[choice]
        
        self.check_whole = wx.CheckBox(top_panel, label="Whole Words")
        self.check_whole.SetValue(True)         
        row1.Add(self.dict_choice, 1, wx.ALL | wx.EXPAND, 5)
        row1.Add(self.check_whole, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_NORMAL, False, "Franklin Gothic Medium")
        t_font2 = wx.Font(int(tFont["fontSize"]), wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, tFont["TextFont"],)
        t_font1 = wx.Font(int(tFont["fontSize1"]), wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, tFont["Text1Font"],)        

        # Row 2: Two multiline text controls
        row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.text_1 = wx.TextCtrl(top_panel, style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL|wx.TE_RICH2)
        self.text_1.SetFont(font)
        self.text_1.SetForegroundColour("BLUE")
        self.text_1.SetToolTip("From dictionary")
        self.txt2 = wx.TextCtrl(top_panel, style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL|wx.TE_RICH2)
        self.txt2.SetFont(t_font1)
        self.txt2.SetToolTip("Current line")
        row2.Add(self.text_1, 1, wx.ALL | wx.EXPAND, 5)
        row2.Add(self.txt2, 1, wx.ALL | wx.EXPAND, 5)

        top_vsizer.Add(row1, 0, wx.EXPAND)
        top_vsizer.Add(row2, 1, wx.EXPAND)
        top_panel.SetSizer(top_vsizer)

        # --- Second (middle) pane ---
        mid_panel = wx.Panel(self.splitter)
        mid_hsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.dvc = dv.DataViewCtrl(
            mid_panel,
            style=dv.DV_ROW_LINES
            | dv.DV_VERT_RULES
            | dv.DV_HORIZ_RULES
            | dv.DV_MULTIPLE,
        )
        self.dvc.SetFont(t_font2)
        self.dvc.SetToolTip("\n Press ‚Esc’ or ‚Tab’ to switch focus \n ")
        # renderer + column for each field
        self.dvc.AppendTextColumn("Line", 0, width=60, mode=dv.DATAVIEW_CELL_INERT)
        self.dvc.AppendTextColumn("Start", 1, width=120, mode=dv.DATAVIEW_CELL_INERT)
        self.dvc.AppendTextColumn("End",   2, width=120, mode=dv.DATAVIEW_CELL_INERT)
        self.dvc.AppendTextColumn("CPS",   3, width=60, mode=dv.DATAVIEW_CELL_INERT)
        self.dvc.AppendTextColumn("Text", 4, width=420, mode=dv.DATAVIEW_CELL_INERT)        
        
        mid_hsizer.Add(self.dvc, 1, wx.ALL | wx.EXPAND, 5)
        btn_vsizer = wx.BoxSizer(wx.VERTICAL)
        
        labels = [
            "Accept",
            "Ignore",
            "ReplaceAll",
            "IgnoreAll",
            ("Add",   wx.ID_ADD),
            ("Ok",    wx.ID_OK),
            ("Cancel", wx.ID_CANCEL),
        ]
        
        for item in labels:
            if isinstance(item, tuple):
                label, bid = item
                btn = wx.Button(mid_panel, id=bid, label="", size=(75, 25))
                attr_name = f"button_{label.lower()}"
            else:
                # Plain label
                btn = wx.Button(mid_panel, label=item, size=(75, 25))
                attr_name = f"button_{item.lower()}"
                
            btn_vsizer.Add(btn, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        
            # Save button as class attribute
            setattr(self, attr_name, btn)
        
        self.button_add.SetToolTip("Add sellected\nto dictionary")
        self.button_add.Enable(False)
        
        btn_vsizer.Add(12,12, proportion=1)
        
        enable_btn = not MAIN_SETTINGS["Manually"]["Auto_replace"]
        
        self.replace_btn = wx.Button(mid_panel, wx.ID_ANY, "Replace", size=(75, 25))
        self.replace_btn.SetToolTip("Replace Selected")
        self.replace_btn.Enable(enable_btn)
        btn_vsizer.Add(self.replace_btn, 0, wx.TOP |wx.LEFT |wx.RIGHT |wx.EXPAND, 5)
        
        self.skip_btn = wx.Button(mid_panel, wx.ID_ANY, "Skip", size=(75, 25))
        self.skip_btn.SetToolTip("Skip Selected")
        self.skip_btn.Enable(enable_btn)
        btn_vsizer.Add(self.skip_btn, 0, wx.TOP |wx.LEFT |wx.RIGHT |wx.EXPAND, 5)
        
        self.next_btn = wx.Button(mid_panel, wx.ID_ANY, "Next", size=(75, 25))
        self.next_btn.SetToolTip("Go to next line")
        self.next_btn.Enable(enable_btn)
        btn_vsizer.Add(self.next_btn, 0, wx.TOP |wx.LEFT |wx.RIGHT |wx.EXPAND, 5)
        
        #self.play_button = wx.Button(mid_panel, wx.ID_ANY, "Play", size=(75, 25))
        #self.play_button.SetToolTip("Play Audio")
        #btn_vsizer.Add(self.play_button, 0, wx.TOP |wx.LEFT |wx.RIGHT |wx.EXPAND, 5)        

        self.translate_btn = wx.Button(mid_panel, wx.ID_ANY, "Translate", size=(75, 25))
        self.translate_btn.SetToolTip("Translate current text")
        self.translate_btn.Enable(self.translator_menu.IsChecked())
        btn_vsizer.Add(self.translate_btn, 0, wx.ALL | wx.EXPAND, 5)
        
        mid_hsizer.Add(btn_vsizer, 0, wx.EXPAND)
        mid_panel.SetSizer(mid_hsizer)

        # --- Third (bottom) pane ---
        bottom_panel = wx.Panel(self.splitter)
        bottom_vsizer = wx.BoxSizer(wx.VERTICAL)

        self.text_3 = UndoableTextCtrl(bottom_panel, style=wx.TE_WORDWRAP)
        t_font3 = wx.Font(
            int(tFont["fontSize2"]),
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
            0,
            tFont["Text2Font"],
        )
        self.text_3.SetFont(t_font3)
        self.text_3.SetToolTip("Current line\nPress ‚Esc’ or ‚Tab’ to switch focus on the grid")
        bottom_vsizer.Add(self.text_3, 1, wx.ALL | wx.EXPAND, 5)

        # Lower: horizontal row
        bottom_row = wx.BoxSizer(wx.HORIZONTAL)

        self.text_ADD = wx.TextCtrl(bottom_panel, style=wx.TE_PROCESS_ENTER | wx.TE_NOHIDESEL|wx.TE_RICH2)
        self.text_ADD.SetFont(font)
        bottom_row.Add(self.text_ADD, 1, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = wx.Button(bottom_panel, label="OK")
        self.ok_btn.SetMinSize((75, 32))
        self.cancel_btn = wx.Button(bottom_panel, label="Cancel")
        self.cancel_btn.SetMinSize((75, 32))
        btn_box.Add(self.ok_btn, 0, wx.ALL, 5)
        btn_box.Add(self.cancel_btn, 1, wx.RIGHT | wx.TOP | wx.BOTTOM, 5)

        bottom_row.Add(btn_box, 0)

        bottom_vsizer.Add(bottom_row, 0, wx.EXPAND)
        bottom_panel.SetSizer(bottom_vsizer)

        # Append panes
        self.splitter.AppendWindow(top_panel, 200)
        self.splitter.AppendWindow(mid_panel, 200)
        self.splitter.AppendWindow(bottom_panel, 150)

        outer_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)
        wx.CallAfter(self.set_splitter_position)        
        panel.SetSizer(outer_sizer)
        self.Centre()
        self.Layout()
        
        try:
            self.default_subs = srt.compose(subtitles)
        except:
            self.default_subs = getSubtitles("test-1.srt")
                
        ## Bind Events ====================================================================##
        self.dict_choice.Bind(wx.EVT_CHOICE, self.FileChanged, self.dict_choice)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onOK, self.button_ok)
        self.Bind(wx.EVT_MENU, self.onOK, id=self.ok_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.button_cancel)
        self.Bind(wx.EVT_MENU, self.onCancel, id=self.cancel_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.next_subtitle, self.button_accept)
        self.Bind(wx.EVT_MENU, self.next_subtitle, id=self.accept_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.onReplaceAll, self.button_replaceall)
        self.Bind(wx.EVT_MENU, self.onReplaceAll, id=self.replaceall_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.onIgnore, self.button_ignore)
        self.Bind(wx.EVT_MENU, self.onIgnore, id=self.ignore_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.onIgnoreAll, self.button_ignoreall)
        self.Bind(wx.EVT_MENU, self.onIgnoreAll, id=self.ignoreall_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.addSelected, self.button_add)
        self.Bind(wx.EVT_MENU, self.addSelected, id=self.add_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.onTranslate, self.translate_btn)
        self.Bind(wx.EVT_MENU, self.onTranslate, id=self.translate_menu.GetId())
        self.Bind(wx.EVT_MENU, self.onMenuCheck, id=self.translator_menu.GetId())
        self.Bind(wx.EVT_MENU, self.onMenuCheck, id=self.auto_menu.GetId())
        self.Bind(wx.EVT_MENU, self.editShortcuts, id=self.shortcut_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.addOK, self.ok_btn)
        self.Bind(wx.EVT_BUTTON, self.addCANCEL, self.cancel_btn)
        self.check_whole.Bind(wx.EVT_CHECKBOX, self.onWholeToggle)        
        self.text_ADD.Bind(wx.EVT_TEXT, self.textAdded, self.text_ADD)
        self.text_3.Bind(wx.EVT_LEFT_UP, self.on_selection_change)
        self.text_3.Bind(wx.EVT_KEY_UP, self.on_selection_change)
        self.text_3.Bind(wx.EVT_TEXT, self.on_selection_change)
        self.Bind(wx.EVT_MENU, lambda e: self.text_3.undo(), self.undo_menu)
        self.Bind(wx.EVT_MENU, lambda e: self.text_3.redo(), self.redo_menu)        
        # --- Manual mode ---
        self.replace_btn.Bind(wx.EVT_BUTTON, self.replace_selected)
        self.skip_btn.Bind(wx.EVT_BUTTON, self.skip_selected)
        self.next_btn.Bind(wx.EVT_BUTTON, self.next_subtitle)
        self.Bind(wx.EVT_MENU, self.replace_selected, id=self.replace_menu.GetId())
        self.Bind(wx.EVT_MENU, self.skip_selected, id=self.skip_menu.GetId())
        self.Bind(wx.EVT_MENU, self.next_subtitle, id=self.next_menu.GetId())
        
        self.dvc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.on_selection_changed)
        self.dvc.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        self.text_3.Bind(wx.EVT_TEXT, self.on_text3_change)
        self._text3_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_text3_timer, self._text3_timer)        
        self.text_3.Bind(wx.EVT_KEY_DOWN, self.on_text3_key_down)
        
        # --- Bindings for single-check + settings update ---
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.english)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.russian)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.slovenian_)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.macedonian_)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.croatian_)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.bosnian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.serbian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.croatian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.slovenian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.macedonian)
        ## ================================================================================##
        
        self._restore_menu_selection()
        update_accelerators(self)
                
        self.Ignored = []
        self.ReplacedAll = []
        self.new_d = {}
        self.sc = {}
        self.whole_word = True
        self.show_dialog = True
        self.replaced = False
        
        self.matches = []
        self.sub = None
        self.replaced_text = False
        self.auto_update_enabled = True
        self._empty_iter_try = 0
                
        self.wdict = Dictionaries().dict_fromFile(self.dname, "=>")
        self.subs = srt.parse(self.default_subs, ignore_errors=True)
        self.wdict = self.clearDict(self.wdict, srt.compose(self.subs))
        
        # store subs and create model
        self.model = SubtitlesModel(list(self.subs))
        self.dvc.AssociateModel(self.model)
        
        # keep selection index
        self.selected_row = None
        
        self.subs = iter(self.model.subs)
        self.getValues(self.subs)
        
    def on_text3_key_down(self, event):
        if event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_TAB):
            # Tab or Esc → move focus to list
            self.dvc.SetFocus()
            return
        event.Skip()
        
    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            self.on_delete_row(None)
        elif event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_TAB):
            self.text_3.SetFocus()
        else:
            event.Skip()
    
    def on_text3_change(self, event):
        """Called whenever text changes — debounce CPS update."""
        if self._text3_timer.IsRunning():
            self._text3_timer.Stop()
        self._text3_timer.Start(150, oneShot=True)  # 150 ms delay
        event.Skip()
        
    def on_text3_timer(self, event):
        """When user stops typing for 150 ms, update content + CPS color."""
        selection = self.dvc.GetSelection()
        if not selection.IsOk():
            return
        row = self.model.GetRow(selection)
        if row is None:
            return
        sub = self.model.subs[row]
        sub.content = self.text_3.GetValue()
        try:
            self.model.RowChanged(row)
        except Exception:
            self.model.RowsChanged(row, row)
    
    def on_delete_row(self, event):
        selections = self.dvc.GetSelections()
        if not selections:
            return
        dlg = wx.MessageDialog(
            self,
            "Delete selected row(s)?",
            "Confirm Delete",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )
        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
        dlg.Destroy()
        rows_to_delete = sorted([self.model.GetRow(item) for item in selections], reverse=True)
        for row in rows_to_delete:
            if 0 <= row < len(self.model.subs):
                del self.model.subs[row]
                self.model.RowDeleted(row)
                self.dvc.Refresh()
        self.model.reindex()
        total = self.model.GetCount()
        if total == 0:
            self.text_3.Clear()
            self.text_3.SetFocus()
            return
        elif row >= total:
            row = total - 1
        self.dvc.Select(self.model.GetItem(row))
        self.dvc.EnsureVisible(self.model.GetItem(row))
        self.on_selection_changed(None)
        
    def replace_selected(self, event=None):
        """Replace current match and move to next."""
        if not self.matches:
            return
        
        content = self.text_3.GetValue()           
                
        match = self.matches.pop(0)
        key = match["key"]
        value = match["value"]
        self.ReplacedAll.append(value)
        if self.whole_word:
            pattern = re.compile(rf'\b{re.escape(key)}\b')
        else:
            pattern = re.compile(re.escape(key))
    
        m = pattern.search(content)
        if not m:
            return
    
        start, end = m.start(), m.end()
    
        new_content = content[:start] + value + content[end:]
        self.text_3.SetValue(new_content)
        self.text_3.SetFocus()
        
        # Adjust match positions
        delta = len(value) - (end - start)
        for m in self.matches:
            if m["start"] > end:
                m["start"] += delta
                m["end"] += delta        
        
        for val in self.new_d.values():
            wx.CallAfter(self.textStyle, self.text_3, new_content, "VIOLET RED", "", val)        
        
        self.sub.content = new_content
        #if self.matches:
        self.update_matches_from_content(new_content)            
        self.replaced_text = True
        self.sub.content = new_content
        self.sub = Subtitle(self.sub.index, self.sub.start, self.sub.end, new_content)
            
    def skip_selected(self, event=None):
        """Skip the current match and go to next."""
        if not self.matches:
            return
        #if len(self.matches) > 1:
        self.matches.pop(0)
    
        if self.matches:
            self.highlight_current()
        else:
            self.sub = None
            self.next_subtitle()
    
    def update_matches_from_content(self, content, dictionary=None):
        """Rebuild self.matches for remaining keys in new_d."""
        self.matches.clear()
        if not dictionary:
            dictionary = self.new_d
        for k, v in dictionary.items():
            pattern = re.compile(rf'\b{re.escape(k)}\b' if self.whole_word else re.escape(k))
            for m in re.finditer(pattern, content):
                self.matches.append({
                    "key": k,
                    "value": v,
                    "start": m.start(),
                    "end": m.end()
                })
        if self.matches:
            self.highlight_current()
            
    @staticmethod
    def info_message(message=None):
        """"""
        wx.MessageBox(message, "Info", wx.OK|wx.ICON_INFORMATION)
    
    def next_subtitle(self, event=None):
        if not hasattr(self, "_empty_iter_try"):
            self._empty_iter_try = 0
        self.matches.clear()
        if not self.wdict:
            return
        try:
            peek = next(self.subs)
            self.subs = itertools.chain([peek], self.subs)
            self._empty_iter_try = 0  # reset if not empty
        except StopIteration:
            self._empty_iter_try += 1
            if self._empty_iter_try == 3:
                self.info_message(f"{basename(self.dname)[:-4]}\n\nTitl je iscrpljen")
                self._empty_iter_try = 0
            return
        if self.sub and getattr(self.sub, "content", "").strip():
            if getattr(self, "replaced_text", True):
                self.replaced_text = False
        self.getValues(self.subs)
        self.text_3.SetFocus()
        
    def highlight_current(self):
        """Highlight the current match in text_3."""
        if not self.matches:
            self.next_subtitle()
            return
        match = self.matches[0]
        start = match["start"]
        end = match["end"]        
        self.text_3.SetFocus()
        if not self.auto_menu.IsChecked():
            wx.CallAfter(self.text_3.SetSelection, start, end)
        
    def select_subtitle_by_index(self, sub_index):
        row = self.model.index_map.get(sub_index)
        if row is not None:
            item = self.model.GetItem(row)
            self.dvc.Freeze()
            try:
                self.dvc.UnselectAll()
                self.dvc.Select(item)
                self.dvc.EnsureVisible(item)
            finally:
                self.dvc.Thaw()
        
    # selection -> show content in text box
    def on_selection_changed(self, event):
        # get selected item (single selection; if multiple, take first)
        sel = self.dvc.GetSelection()
        if not sel.IsOk():
            # nothing selected
            self.selected_row = None
            self.text_3.SetValue("")
            return

        # Convert DataViewItem to row index using model helper
        try:
            row = self.model.GetRow(sel)  # typical method
        except Exception:
            try:
                row = self.model.ItemToRow(sel)
            except Exception:
                # fallback: iterate to find matching row (rare)
                row = None
                for r in range(self.model.GetCount()):
                    item = self.dvc.RowToItem(r)
                    if item == sel:
                        row = r
                        break
        if row is None:
            self.selected_row = None
            self.text_3.SetValue("")
            return
        self.selected_row = row
        sub = self.model.subs[row]
        # If row is changed, convert back "|" to newlines for display
        text = (
            sub.content.replace("|", "\n")
            if row in self.model.changed_rows
            else sub.content
        )
        self.text_3.ClearUndoRedo()
        self.text_3.SetValue(text)
        if self.lock_menu.IsChecked() and not self.dvc.HasFocus():
            wx.CallAfter(self.text_3.SetFocus)
            
    def getValues(self, iterator=None):
        """"""
        c = 0
        try:
            self.sub = next(iterator)
            c += 1
        except StopIteration:
            self.info_message(f"{basename(self.dname)[:-4]}\n\nTitl je iscrpljen")
            return
        try:
            [self.wdict.pop(k, None) for k in self.Ignored]
            keys_sorted = sorted(self.wdict.keys(), key=len, reverse=True)
            if self.whole_word is False:
                r1 = re.compile(r"("+"|".join(map(re.escape, keys_sorted))+r")")
            else:
                r1 = re.compile(r"\b("+"|".join(map(re.escape, keys_sorted))+r")\b")            
            t1 = r1.findall(self.sub.content)
            self.text_1.Clear()
            for key in t1:
                self.text_1.SetDefaultStyle(wx.TextAttr(wx.BLUE)) # default
                value = self.wdict.get(key, "")
                self.text_1.AppendText(f"{key}: ")
                self.text_1.SetDefaultStyle(wx.TextAttr(wx.RED)) # color for value
                self.text_1.AppendText(f"{value}\n")
                self.text_1.SetDefaultStyle(wx.TextAttr(wx.BLUE))                 
            newd = {w: self.wdict[w] for w in t1}
            self.txt2.SetValue(self.composeSub(self.sub))
            self.update_matches_from_content(self.sub.content, newd)
            if self.matches and self.sub:
                self.txt2.SetValue(self.composeSub(self.sub))
                self.text_3.ClearUndoRedo()                    
                if not self.auto_menu.IsChecked():
                    text = self.sub.content
                    self.text_3.SetValue(text)
                    for k in newd.keys():
                        wx.CallAfter(self.textStyle, self.text_3, text, "BLACK", "#C4F0C2", k)                    
                    self.highlight_current()
                else:
                    text = self.sub.content  # start with original
                    for k, v in newd.items():
                        pattern = rf'\b{k}\b' if self.whole_word else re.escape(k)
                        text = re.sub(pattern, v, text)
                        self.ReplacedAll.append(v)
                    self.text_3.SetValue(text)
                    for v in newd.values():
                        wx.CallAfter(self.textStyle, self.text_3, text, "VIOLET RED", "", v)                
                self.select_subtitle_by_index(self.sub.index)
                self.new_d = newd
                self.text_3.SetFocus()
            else:
                self.getValues(iterator=self.subs)
            return c
        except Exception as e:
            logger.debug(f"getValues: {e}")
    
    @staticmethod
    def composeSub(sub=None):
        """"""
        start = srt.timedelta_to_srt_timestamp(sub.start)
        end = srt.timedelta_to_srt_timestamp(sub.end)
        return f"{sub.index}\n{start} --> {end}\n{sub.content}\n\n"
    
    def FileChanged(self, event):
        """"""
        choice = self.dict_choice.GetStringSelection()
        self.dname = self.file_map[choice]        
        self.wdict = Dictionaries().dict_fromFile(self.dname, "=>")
        self.default_subs = self.GetText()
        subs = srt.parse(self.default_subs)        
        self.wdict = self.clearDict(self.wdict, srt.compose(subs))
        if not self.wdict:
            wx.MessageBox(
                f"{basename(self.dname)[:-4]}\n\n"
                f"U rečniku nema poklapanja.\nPromenite rečnik",
                "Dictionary change",
            )
            return
        self.next_subtitle()
        event.Skip()

    def textStyle(self, tctrl, text, st1, st2, w=None):
        """"""
        x = re.compile(rf'\b{re.escape(w)}\b' if self.whole_word else re.escape(w))
        for m in re.finditer(x, text):
            tctrl.SetStyle(m.start(), m.end(), wx.TextAttr(st1, st2))
                
    def GetText(self):
        """"""
        return srt.compose(self.model.subs)            

    def onReplaceAll(self, event):
        ''''''
        try:
            if self.whole_word is False:
                ctext = re.compile(r"("+"|".join(map(re.escape,self.new_d.keys()))+r")")
            else:
                ctext = re.compile(r"\b("+"|".join(map(re.escape,self.new_d.keys()))+r")\b")
            self.default_subs = ctext.sub(lambda x: self.new_d[x.group()], self.default_subs)
            wsubs = self.GetText()
            wsubs = ctext.sub(lambda x: self.new_d[x.group()], wsubs)
            for k, v in self.new_d.items():
                self.ReplacedAll.append(v)
                self.wdict.pop(k)
            self.subs = srt.parse(wsubs)
            self.model.subs = list(srt.parse(wsubs))
            self.model.Reset(len(self.model.subs))
            self.next_subtitle()
        except Exception as e:
            logger.debug(f"ReplaceAll: {e}")
        event.Skip()

    def onIgnore(self, event):
        self.next_subtitle()
        event.Skip()

    def onIgnoreAll(self, event=None):
        try:
            for line in self.text_1.GetValue().splitlines():
                key = line.split(":", 1)[0].strip()
                self.Ignored.append(key)
            for k in set(self.Ignored):
                self.wdict.pop(k, None)
            self.next_subtitle()
        except Exception as e:
            logger.debug(f"IgnoreAll: {e}")        
    
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
        if self.whole_word is False:
            pattern = re.compile(r"(" + "|".join(map(re.escape, _dict.keys())) + r")")
        else:
            pattern = re.compile(r"\b(" + "|".join(map(re.escape, _dict.keys())) + r")\b")

        # Find all matches of dictionary keys in the subtitles
        matches = pattern.findall(_subs)

        # Create a new dictionary with only the matched keys
        for match in matches:
            if match in _dict:
                filtered_dict[match] = _dict[match]
        # Parse the default subtitles
        self.subs = srt.parse(self.default_subs, ignore_errors=True)
        return filtered_dict    
    
    def on_selection_change(self, event):
        start, end = self.text_3.GetSelection()
        if end > start:
            self.button_add.Enable(True)
        else:
            self.button_add.Enable(False)        
        event.Skip()    
        
    def addSelected(self, event):
        '''button_add event'''
        start,end = self.text_3.GetSelection()
        if "\n" in self.text_3.GetValue()[start : end]:
            wx.MessageBox(
                f"ValueError\n\n"
                f"Please select text from a single line only.",
                "Invalid Selection",
                style=wx.OK | wx.ICON_INFORMATION,
            )
            self.text_3.SetSelection(0, 0)
            self.button_add.Enable(False)        
        else:
            text = self.text_3.GetValue()[start : end]
            self.text_ADD.SetValue(f"{text}=>")
            if self.translator_menu.IsChecked():
                translated_text = self.translate(text)
                self.text_ADD.SetValue(f"{text}=>{translated_text}")
            self.text_ADD.SetFocus()
            self.text_ADD.SetInsertionPointEnd()
        event.Skip()

    def textAdded(self, event):
        '''EVT_TEXT text.aADD'''
        if self.translator_menu.IsChecked() or self.text_ADD.IsModified():
            self.textStyle(self.text_ADD, self.text_ADD.GetValue(), "GREY","","=>")
            self.ok_btn.Enable()
            self.cancel_btn.Enable()
        event.Skip()
        
    @staticmethod
    def translate(input_text):
        """"""
        data = MAIN_SETTINGS["Manually"]
        src_lang = lang_dict[data["Source"]]
        dest_lang = lang_dict[data["Destination"]]
        try:
            translation = translate_sync(input_text, src=src_lang, dest=dest_lang)
            if dest_lang == "sr":
                translated_text = cyr_to_lat(translation.text)
            else:
                translated_text = translation.text
            return translated_text
        except Exception as e:
            logger.debug(f"Translate: {e}")
            wx.MessageBox(f"Unexpected Error\n\n{e}", "Error")        
    
    def onTranslate(self, event):
        """"""
        text = self.text_3.GetValue().strip()
        translated_text = self.translate(text)
        if self.show_dialog:
            dlg = wx.RichMessageDialog(
                self,
                f"Prevod teksta\n\n{translated_text}",
                "Confirm",
                style=wx.OK | wx.CANCEL | wx.ICON_QUESTION,
            )
            dlg.ShowCheckBox("Ne prikazuj više ovaj dijalog")
            result = dlg.ShowModal()
            dont_show = dlg.IsCheckBoxChecked()
            dlg.Destroy()
            if dont_show:
                self.show_dialog = False
            if result == wx.ID_OK:
                self.text_3.SetValue(translated_text)
        else:
            self.text_3.SetValue(translated_text)
        event.Skip()
        
    def addOK(self, event):
        '''Button_dict event'''
        choice = self.dict_choice.GetStringSelection()
        current_dict = self.file_map[choice]        
        with open(current_dict, "a", encoding="utf-8") as dict_file:
            dict_file.write(f"\n{self.text_ADD.GetValue().strip()}")
        self.text_ADD.Clear()
        self.ok_btn.Enable(False)
        self.cancel_btn.Enable(False)
        self.text_3.SetFocus()
        event.Skip()

    def addCANCEL(self, event):
        '''Button event'''
        self.text_ADD.Clear()
        self.ok_btn.Enable(False)
        self.cancel_btn.Enable(False)
        self.text_3.SetFocus()
        event.Skip()
            
    def onWholeToggle(self, event):
        self.whole_word = self.check_whole.GetValue()
        event.Skip()
        
    def onMenuCheck(self, event):
        """"""
        menu_id = event.GetId()
        if menu_id == self.translator_menu.GetId():
            is_checked = self.translator_menu.IsChecked()
            self.translate_btn.Enable(is_checked)
            self.preferences_menu.Enable(self.source_item.GetId(), is_checked)
            self.preferences_menu.Enable(self.destination_item.GetId(), is_checked)
        elif menu_id == self.auto_menu.GetId():
            #self.text_2.Clear()
            is_checked = not self.auto_menu.IsChecked()
            self.replace_btn.Enable(is_checked)
            self.skip_btn.Enable(is_checked)
            self.next_btn.Enable(is_checked)
        event.Skip()
        
    def set_splitter_position(self):
        data_dict = MAIN_SETTINGS["Manually"]
        try:
            self.splitter.SetSashPosition(0, data_dict["sash1"])
            self.splitter.SetSashPosition(1, data_dict["sash2"])
        except (KeyError, Exception) as e:
            logger.debug(f"set_splitter_position: {e}")
        
    def writeSettings(self):
        """"""
        size = self.GetSize()
        width = size.GetWidth()
        height = size.GetHeight()
        pos_1 = self.splitter.GetSashPosition(0)
        pos_2 = self.splitter.GetSashPosition(1)
        translator = self.translator_menu.IsChecked()
        auto = self.auto_menu.IsChecked()
        lock = self.lock_menu.IsChecked()
        # Update the MAIN_SETTINGS_SETTINGS dictionary
        MAIN_SETTINGS["Manually"].update(
            {
                "W": width,
                "H": height,
                "sash1": pos_1,
                "sash2": pos_2,
                "Translate": translator,
                "LockFocus": lock,
                "Auto_replace": auto,
            }
        )
            
    def onShortcutChanged(self, event):
        """"""
        shortcut = event.GetShortcut()
        newAccel = event.GetAccelerator()
        if newAccel == "Disabled":
            newAccel = ""
        self.sc[shortcut.label] = newAccel
        event.Skip()    
    
    def editShortcuts(self, event):
        """"""
        dlg = SE.ShortcutEditor(self)
        dlg.FromMenuBar(self)
        dlg.Bind(SE.EVT_SHORTCUT_CHANGED, self.onShortcutChanged)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.ToMenuBar(self)
            shortcut_keys = MAIN_SETTINGS["FrameShortcuts"]
            shortcut_keys.update(self.sc)
            update_accelerators(self)
        event.Skip()
        
    def onSourceSelect(self, event):
        """Ensure only one source is checked and store in settings."""
        for item in self.source.GetMenuItems():
            item.Check(item.GetId() == event.GetId())
    
        label = self.source.FindItemById(event.GetId()).GetItemLabelText()
        MAIN_SETTINGS["Manually"]["Source"] = label
        
    def onDestinationSelect(self, event):
        """Ensure only one destination is checked and store in settings."""
        for item in self.destination.GetMenuItems():
            item.Check(item.GetId() == event.GetId())
    
        label = self.destination.FindItemById(event.GetId()).GetItemLabelText()
        MAIN_SETTINGS["Manually"]["Destination"] = label
        
    def _restore_menu_selection(self):
        """Restore menu state from saved MAIN_SETTINGS values."""
        src = MAIN_SETTINGS["Manually"].get("Source")
        dst = MAIN_SETTINGS["Manually"].get("Destination")
        if src:
            for item in self.source.GetMenuItems():
                item.Check(item.GetItemLabelText() == src)
        if dst:
            for item in self.destination.GetMenuItems():
                item.Check(item.GetItemLabelText() == dst)
    
    def onOK(self, event):
        """"""
        self.data_list = list(
            dict.fromkeys(w for w in self.ReplacedAll if w.strip() and len(w) > 3)
        )        
        current_text = self.GetText()
        self.writeSettings()
        if self.on_done:
            self.on_done(self.data_list, current_text)        
        self.Destroy()
        event.Skip()    
        
    def onCancel(self, event):
        self.writeSettings()
        self.Destroy()
        event.Skip()
        
    def onClose(self, event):
        self.writeSettings()
        self.Destroy()    


class MyApp(wx.App):
    def OnInit(self):
        frame = FindReplace(None)
        frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
