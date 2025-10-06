# -*- coding: utf-8 -*-


import glob
import os
from os.path import join
import re
import srt
from srt import Subtitle
import shutil
from collections import defaultdict 
from resources.DictHandle import Dictionaries
from resources.transliterate import cyr_to_lat
from resources.translate_text import translate_sync, lang_dict
from settings import I_PATH, MAIN_SETTINGS, main_settings_file
import json
try:
    from agw import shortcuteditor as SE
except ImportError: 
    import wx.lib.agw.shortcuteditor as SE

import logging.config


import wx
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

        self.accept_menu = self.edit_menu.Append(wx.ID_ANY, f"Accept\t{sKey["Accept"]}")
        self.ignore_menu = self.edit_menu.Append(wx.ID_ANY, f"Ignore\t{sKey["Ignore"]}")
        self.replaceall_menu = self.edit_menu.Append(wx.ID_ANY, f"ReplaceAll\t{sKey["ReplaceAll"]}")
        self.ignoreall_menu = self.edit_menu.Append(wx.ID_ANY, f"IgnoreAll\t{sKey["IgnoreAll"]}")
        #self.apply_menu = self.edit_menu.Append(wx.ID_ANY, f"Apply\t{sKey["Apply"]}")
        self.add_menu = self.edit_menu.Append(wx.ID_ANY, f"Add\t{sKey["Add"]}")
        self.ok_menu = self.edit_menu.Append(wx.ID_ANY, f"Ok\t{sKey["Ok"]}")
        self.cancel_menu = self.edit_menu.Append(wx.ID_ANY, f"Cancel\t{sKey["Cancel"]}")
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
        self.slovenian = self.source.AppendCheckItem(wx.ID_ANY, "Slovenački")
        self.macedonian = self.source.AppendCheckItem(wx.ID_ANY, "Makedonski")
        self.source_item = self.preferences_menu.AppendSubMenu(self.source, "Source")
        
        self.destination = wx.Menu()
        self.serbian = self.destination.AppendCheckItem(wx.ID_ANY, "Srpski")
        self.croatian = self.destination.AppendCheckItem(wx.ID_ANY, "Hrvatski")
        self.slovenian = self.destination.AppendCheckItem(wx.ID_ANY, "Slovenački")
        self.macedonian = self.destination.AppendCheckItem(wx.ID_ANY, "Makedonski")
        self.destination_item = self.preferences_menu.AppendSubMenu(self.destination, "Destination")        
        
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
        self.file_map = {os.path.basename(p): p for p in file_paths}

        # choices for display
        choices = list(self.file_map.keys())        
        self.dict_choice = wx.Choice(top_panel, choices=choices)
        self.dict_choice.SetSelection(choices.index("Dictionary-1.txt"))
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
        self.text_1 = wx.TextCtrl(top_panel, style=wx.TE_MULTILINE| wx.TE_RICH2)
        self.text_1.SetFont(font)
        self.text_1.SetForegroundColour("BLUE")
        self.text_1.SetToolTip("From dictionary")
        self.txt2 = wx.TextCtrl(top_panel, style=wx.TE_MULTILINE| wx.TE_RICH2)
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

        self.text_2 = wx.TextCtrl(mid_panel, style=wx.TE_MULTILINE| wx.TE_RICH2)
        self.text_2.SetFont(t_font2)
        self.text_2.SetToolTip("Text editing is supported\nbut no line deletions")
        mid_hsizer.Add(self.text_2, 1, wx.ALL | wx.EXPAND, 5)

        btn_vsizer = wx.BoxSizer(wx.VERTICAL)
        
        labels = [
            "Accept",
            "Ignore",
            "ReplaceAll",
            "IgnoreAll",
            #("Apply", wx.ID_APPLY),
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
        self.translate_btn = wx.Button(mid_panel, wx.ID_ANY, "Translate", size=(75, 25))
        self.translate_btn.SetToolTip("Translate current text")
        btn_vsizer.Add(self.translate_btn, 0, wx.ALL | wx.EXPAND, 5)
        if self.translator_menu.IsChecked():
            self.translate_btn.Enable()
        else:
            self.translate_btn.Enable(False)
        mid_hsizer.Add(btn_vsizer, 0, wx.EXPAND)
        mid_panel.SetSizer(mid_hsizer)

        # --- Third (bottom) pane ---
        bottom_panel = wx.Panel(self.splitter)
        bottom_vsizer = wx.BoxSizer(wx.VERTICAL)

        # Upper: multiline text
        self.text_3 = wx.TextCtrl(bottom_panel,
                                  style=wx.TE_MULTILINE|wx.TE_CENTER|wx.TE_NO_VSCROLL|wx.TE_NOHIDESEL|wx.TE_RICH2)
        t_font3 = wx.Font(
            int(tFont["fontSize2"]),
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
            0,
            tFont["Text2Font"],
        )
        self.text_3.SetFont(t_font3)
        self.text_3.SetToolTip("Current Text")
        bottom_vsizer.Add(self.text_3, 1, wx.ALL | wx.EXPAND, 5)

        # Lower: horizontal row
        bottom_row = wx.BoxSizer(wx.HORIZONTAL)

        self.text_ADD = wx.TextCtrl(bottom_panel, style=wx.TE_PROCESS_ENTER | wx.TE_NOHIDESEL| wx.TE_RICH2)
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
        self.splitter.AppendWindow(mid_panel, 250)
        self.splitter.AppendWindow(bottom_panel, 150)

        outer_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)
        wx.CallAfter(self.set_splitter_position)        
        panel.SetSizer(outer_sizer)
        self.Centre()
        self.Layout()
        
        self.Ignored = []
        self.ReplacedAll = []
        self.Replaced = []
        self.new_subs = []
        self.new_d = {}
        self.find = []
        self.sc = {}
        self.whole_word = True
        self.show_dialog = True
        
        try:
            self.default_subs = srt.compose(subtitles)
        except:
            self.default_subs = getSubtitles("test.srt")
                
        ## Bind Events ====================================================================##
        self.dict_choice.Bind(wx.EVT_CHOICE, self.FileChanged, self.dict_choice)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onOK, self.button_ok)
        self.Bind(wx.EVT_MENU, self.onOK, id=self.ok_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.button_cancel)
        self.Bind(wx.EVT_MENU, self.onCancel, id=self.cancel_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.onReplace, self.button_accept)
        self.Bind(wx.EVT_MENU, self.onReplace, id=self.accept_menu.GetId())
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
        self.Bind(wx.EVT_MENU, self.editShortcuts, id=self.shortcut_menu.GetId())
        self.Bind(wx.EVT_BUTTON, self.addOK, self.ok_btn)
        self.Bind(wx.EVT_BUTTON, self.addCANCEL, self.cancel_btn)
        self.check_whole.Bind(wx.EVT_CHECKBOX, self.onWholeToggle)        
        self.text_1.Bind(wx.EVT_TEXT, self.Text1, self.text_1)
        self.text_ADD.Bind(wx.EVT_TEXT, self.textAdded, self.text_ADD)
        self.text_3.Bind(wx.EVT_LEFT_UP, self.on_selection_change)
        self.text_3.Bind(wx.EVT_KEY_UP, self.on_selection_change)
        self.text_3.Bind(wx.EVT_TEXT, self.on_selection_change)
        # --- Bindings for single-check + settings update ---
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.english)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.russian)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.slovenian)
        self.Bind(wx.EVT_MENU, self.onSourceSelect, self.macedonian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.serbian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.croatian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.slovenian)
        self.Bind(wx.EVT_MENU, self.onDestinationSelect, self.macedonian)
        ## ================================================================================##
        
        self._restore_menu_selection()        
                
        self.wdict = Dictionaries().dict_fromFile(self.dname, "=>")
        self.subs = srt.parse(self.default_subs)
        self.wdict = self.clearDict(self.wdict, srt.compose(self.subs))
        self.getValues(self.subs)
        
    def getValues(self, iterator=None):
        """"""
        c = 0
        if self.whole_word is False:
            r1 = re.compile(r"("+"|".join(map(re.escape, self.wdict.keys()))+r")")
        else:
            r1 = re.compile(r"\b("+"|".join(map(re.escape, self.wdict.keys()))+r")\b")
        try:
            sub = next(iterator)
            c += 1
        except StopIteration:
            logger.debug("Iterator was empty")
        finally:
            self.text_3.SetValue(f"{'='*20}\nEnd of subtitles reached\n{'='*20}")
        try:
            t1 = list(set(r1.findall(sub.content)))
            newd = {}
            self.text_1.Clear()
            for i in range(len(t1)):
                self.text_1.AppendText(f"{t1[i]} ")
                v = self.wdict[t1[i]]
                newd[t1[i]] = v
            for k, v in newd.items():
                self.txt2.SetValue(self.composeSub(sub))
                if self.whole_word is True:
                    ctext = re.compile(r'\b'+k+r'\b')
                else:
                    ctext = re.compile(k)
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
            
    def composeSub(self, sub=None):
        """"""
        start = srt.timedelta_to_srt_timestamp(sub.start)
        end = srt.timedelta_to_srt_timestamp(sub.end)
        return f"{sub.index}\n{start} --> {end}\n{sub.content}\n\n"
        
    def FileChanged(self, event):
        """"""
        choice = self.dict_choice.GetStringSelection()
        self.dname = self.file_map[choice]        
        self.wdict = Dictionaries().dict_fromFile(self.dname, "=>")
        self.subs = srt.parse(self.default_subs)
        self.wdict = self.clearDict(self.wdict, srt.compose(self.subs, reindex=False))
        self.text_2.Clear()
        self.Replaced.clear()
        self.onReplace(event)
        event.Skip()

    def textStyle(self, tctrl, text, st1, st2, w=r""):
        """"""
        if self.whole_word is False:
            x = re.compile(w)
        else:
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
            if self.whole_word is False:
                ctext = re.compile(r"("+"|".join(map(re.escape,self.new_d.keys()))+r")")
            else:
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
        
    def on_selection_change(self, event):
        start, end = self.text_3.GetSelection()
        if end > start:
            self.button_add.Enable(True)
        else:
            self.button_add.Enable(False)        
        event.Skip()    
        
    def addSelected(self, event):
        '''button_add event'''
        start, end = self.text_3.GetSelection()
        selected_text = self.text_3.GetValue()[start : end]
        if any(x in selected_text for x in ("\n", "\r")):
            wx.MessageBox(
                f"ValueError\n\n"
                f"Please select text from a single line only.",
                "Invalid Selection",
                style=wx.OK | wx.ICON_INFORMATION,
            )
            self.text_3.SetSelection(0, 0)
            self.button_add.Enable(False)        
        else:
            self.text_ADD.SetValue(f"{selected_text}=>")
            if self.translator_menu.IsChecked():
                translated_text = self.translate(selected_text)
                self.text_ADD.SetValue(f"{selected_text}=>{translated_text}")
            self.text_ADD.SetFocus()
            self.text_ADD.SetInsertionPointEnd()
        event.Skip()

    def textAdded(self, event):
        '''EVT_TEXT text.aADD'''
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
        # Update the MAIN_SETTINGS_SETTINGS dictionary
        MAIN_SETTINGS["Manually"].update({"W": width, "H": height, "sash1": pos_1, "sash2": pos_2, "Translate": translator})
            
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
        self.data_list = self.ReplacedAll
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
