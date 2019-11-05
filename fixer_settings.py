#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.0pre on Thu Oct  4 01:25:07 2018
#

import wx

# begin wxGlade: dependencies
# end wxGlade
import shelve
import pickle
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(filename=os.path.join("resources", "var", "FileProcessing.log"), mode="a", encoding="utf-8")
handler.setFormatter(formatter)
logger.addHandler(handler)

class FixerSettings(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: fixerSettings.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((339, 219))
        
        t1 = os.path.join('resources', 'var', 'dialog_settings.db.dat')
        cb3s = os.path.join('resources', 'var', 'fixer_cb3.data')
        
        self.cb1 = wx.CheckBox(self, wx.ID_ANY, "cbox_1", style=wx.CHK_2STATE)
        self.lb1 = wx.StaticText(self, wx.ID_ANY, "Popravi gapove", style=wx.ALIGN_LEFT)
        
        self.cb2 = wx.CheckBox(self, wx.ID_ANY, "cbox_2", style=wx.CHK_2STATE)
        self.lb2 = wx.StaticText(self, wx.ID_ANY, "Poravnaj linije teksta", style=wx.ALIGN_LEFT)
        
        self.cb3 = wx.CheckBox(self, wx.ID_ANY, "cbox_3", style=wx.CHK_2STATE)
        self.lb3 = wx.StaticText(self, wx.ID_ANY, u"Prika\u017ei linije sa gre\u0161kama u konvertovanom titlu", style=wx.ALIGN_LEFT)
        
        self.cb4 = wx.CheckBox(self, wx.ID_ANY, "cbox_4", style=wx.CHK_2STATE)
        self.lb4 = wx.StaticText(self, wx.ID_ANY, u"Ukloni crtice na po\u010detku prvog reda", style=wx.ALIGN_LEFT)
        
        self.cb5 = wx.CheckBox(self, wx.ID_ANY, "cbox_5", style=wx.CHK_2STATE)
        self.lb5 = wx.StaticText(self, wx.ID_ANY, u"Ukloni spejs iza crtice na po\u010detku", style=wx.ALIGN_LEFT)
        
        self.cb6 = wx.CheckBox(self, wx.ID_ANY, "cbox_6", style=wx.CHK_2STATE)
        self.lb6 = wx.StaticText(self, wx.ID_ANY, u"Vi\u0161estruke spejseve u jedan", style=wx.ALIGN_LEFT)
        
        self.cb7 = wx.CheckBox(self, wx.ID_ANY, "cbox_7", style=wx.CHK_2STATE)
        self.lb7 = wx.StaticText(self, wx.ID_ANY, u"Ukloni suvi\u0161ne italik tagove", style=wx.ALIGN_LEFT)
        
        self.cb8 = wx.CheckBox(self, wx.ID_ANY, "cbox_8", style=wx.CHK_2STATE)
        self.lb8 = wx.StaticText(self, wx.ID_ANY, "Nuliranje time-code celog titla", style=wx.ALIGN_LEFT)        
         
        if os.path.exists(t1):
            try:
                with shelve.open(os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback') as  sp:
                    ex = sp['key1']
                    cb1_s = ex['state1']; cb2_s = ex['state2']; cb3_s = ex['state3']
                    cb4_s = ex['state4']; cb5_s = ex['state5']; cb6_s = ex['state6']; cb7_s = ex['state7']; cb8_s = ex['state8']
            except IOError as e:
                logger.debug("fixerSettings, I/O error({0}): {1}".format(e.errno, e.strerror))
            except Exception as e: #handle other exceptions such as attribute errors
                logger.debug(f"fixerSetting, unexpected error: {e}")
            else:
                              
                self.cb1.SetValue(cb1_s); self.cb2.SetValue(cb2_s); self.cb3.SetValue(cb3_s)
                self.cb4.SetValue(cb4_s); self.cb5.SetValue(cb5_s); self.cb6.SetValue(cb6_s); self.cb7.SetValue(cb7_s)
                self.cb8.SetValue(cb8_s)
                
                if self.cb8.IsChecked() and self.cb1.IsChecked(): self.cb1.SetValue(False)
                
        self.button_2 = wx.Button(self, wx.ID_ANY, "Cancel")
        self.button_1 = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TOOL, self.onClose, id=-1)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.button_1)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: fixerSettings.__set_properties
        self.SetTitle("FixSubtitle settings")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(os.path.join("resources", "icons", "tool.ico"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((350, 259))
        self.SetFocus()
        
        _fonts = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI")
        
        self.cb1.SetMinSize((15, 15))
        self.lb1.SetMinSize((293, 16))
        self.lb1.SetFont(_fonts)
        
        self.cb2.SetMinSize((15, 15))
        self.lb2.SetMinSize((293, 16))
        self.lb2.SetFont(_fonts)
        
        self.cb3.SetMinSize((15, 15))
        self.lb3.SetMinSize((293, 16))
        self.lb3.SetFont(_fonts)
        
        self.cb4.SetMinSize((15, 15))
        self.lb4.SetMinSize((293, 16))
        self.lb4.SetFont(_fonts)
        
        self.cb5.SetMinSize((15, 15))
        self.lb5.SetMinSize((293, 16))
        self.lb5.SetFont(_fonts)
        
        self.cb6.SetMinSize((15, 15))
        self.lb6.SetMinSize((293, 16))
        self.lb6.SetFont(_fonts)
        
        self.cb7.SetMinSize((15, 15))
        self.lb7.SetMinSize((293, 16))
        self.lb7.SetFont(_fonts)
        
        self.cb8.SetMinSize((15, 15))
        self.cb8.SetToolTip("Carefully, think twice :-)")
        self.lb8.SetMinSize((293, 16))
        self.lb8.SetForegroundColour(wx.Colour(255, 0, 0))
        self.lb8.SetFont(_fonts)        
        
        self.button_2.SetMinSize((80, 23))
        self.button_1.SetMinSize((80, 23))
        self.button_1.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: fixerSettings.__do_layout
        self.sizer_1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL)
        self.sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_2.Add(self.cb1, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_2.Add(self.lb1, 1, wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_2, 0, wx.BOTTOM | wx.TOP, 2)
        self.sizer_3.Add(self.cb2, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_3.Add(self.lb2, 1, wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_3, 0, wx.BOTTOM | wx.TOP, 2)
        self.sizer_4.Add(self.cb3, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_4.Add(self.lb3, 1, wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_4, 0, wx.BOTTOM | wx.TOP, 2)
        self.sizer_5.Add(self.cb4, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_5.Add(self.lb4, 1, wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_5, 0, wx.BOTTOM | wx.TOP, 2)
        self.sizer_6.Add(self.cb5, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_6.Add(self.lb5, 1, wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_6, 0, wx.BOTTOM | wx.TOP, 2)
        self.sizer_7.Add(self.cb6, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_7.Add(self.lb6, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_7, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
        self.sizer_9.Add(self.cb7, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_9.Add(self.lb7, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_9, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
        self.sizer_10.Add(self.cb8, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 2)
        self.sizer_10.Add(self.lb8, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT, 2)
        self.sizer_1.Add(self.sizer_10, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
        static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.sizer_1.Add(static_line_1, 0, wx.ALL | wx.EXPAND, 4)
        self.sizer_8.Add(self.button_2, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.TOP, 1)
        self.sizer_8.Add(self.button_1, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.TOP, 1)
        self.sizer_1.Add(self.sizer_8, 0, wx.ALIGN_RIGHT, 0)
        self.SetSizer(self.sizer_1)
        self.Layout()
        # end wxGlade

    def on_cancel(self, event):  # wxGlade: fixerSettings.<event_handler>
        self.Destroy()
        event.Skip()
    
    def on_ok(self, event):  # wxGlade: fixerSettings.<event_handler>
        c1 = self.cb1.GetValue(); c2 = self.cb2.GetValue(); c3 = self.cb3.GetValue()
        c4 = self.cb4.GetValue(); c5 = self.cb5.GetValue(); c6 = self.cb6.GetValue()
        c7 = self.cb7.GetValue(); c8 = self.cb8.GetValue()
        
        konf = [c1, c2, c3, c4, c5, c6, c7, c8]
        a = konf[0]; b = konf[1]; c = konf[2]; d = konf[3]; e = konf[4]; f = konf[5]; g = konf[6]; h = konf[7]
        with shelve.open(os.path.join('resources', 'var', 'dialog_settings.db'), flag='writeback') as s:
            s['key1'] = {'state1': a, 'state2': b, 'state3': c, 'state4': d, 'state5': e, 'state6': f, 'state7': g, 'state8': h, }
        cb3s = os.path.join('resources', 'var', 'fixer_cb3.data')
        with open(cb3s, 'wb') as p:
            pickle.dump(c3, p)
        self.Destroy()
        event.Skip()
    
    #def EvtCheckBox(self, event):  # wxGlade: fixerSettings.<event_handler>
        ## print('EvtCheckBox: %d\n' % event.IsChecked())
        #event.Skip()
        
    def onClose(self, event):
        self.Destroy()
        event.Skip()
# end of class fixerSettings

class MyApp(wx.App):
    def OnInit(self):
        self.dialog = FixerSettings(None, wx.ID_ANY, "")
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        # self.dialog.Destroy()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
