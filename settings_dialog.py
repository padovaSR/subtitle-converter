#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from os.path import join
from settings import FILE_SETTINGS, settings_file

import logging.config

import wx

logger = logging.getLogger(__name__)


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, *args):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
      )
        self.SetTitle("Podešavanja programa")
        self.SetSize(415, 435)
        icon = wx.NullIcon
        icon.CopyFromBitmap(
            wx.Bitmap(join("resources", "icons", "system-run.png"), wx.BITMAP_TYPE_ANY)
      )
        self.SetIcon(icon)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.listbook1 = wx.Listbook(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(-1, -1),
            wx.LB_DEFAULT | wx.LB_LEFT,
      )
        self.panel_1 = wx.Panel(
            self.listbook1,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL,
      )
        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.staticText0 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            f"Odeđuje se dodatna ekstenzija ispred ekstenzije\n"
            f"fajla *.srt, *txt... Može se ostaviti prazno polje bez\n"
            f"spejseva i tada će sačuvani fajl biti prepisan.",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_LEFT,
      )
        self.staticText0.Wrap(-1)

        bSizer3.Add(self.staticText0, 0, wx.ALL | wx.EXPAND, 5)

        gSizer1 = wx.GridSizer(8, 2, 5, 5)

        self.staticText1 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Ćirilica ANSI",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText1.Wrap(-1)

        gSizer1.Add(
            self.staticText1,
            1,
            wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
            5,
      )

        self.staticText5 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Ćirilica UTF-8 txt",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText5.Wrap(-1)

        gSizer1.Add(
            self.staticText5,
            1,
            wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
            5,
      )

        self.textCtrl1 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl1, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.textCtrl5 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl5, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.staticText2 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Ćirilica UTF-8 srt",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText2.Wrap(-1)

        gSizer1.Add(
            self.staticText2, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.staticText6 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Latinica ANSI",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText6.Wrap(-1)

        gSizer1.Add(
            self.staticText6, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.textCtrl2 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl2, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.textCtrl6 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl6, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.staticText3 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Latinica UTF-8",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText3.Wrap(-1)

        gSizer1.Add(
            self.staticText3, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.staticText7 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Popravljeni titlovi",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText7.Wrap(-1)

        gSizer1.Add(
            self.staticText7, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.textCtrl3 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl3, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.textCtrl7 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl7, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.staticText4 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Transkribovani titlovi",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText4.Wrap(-1)

        gSizer1.Add(
            self.staticText4, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.staticText8 = wx.StaticText(
            self.panel_1,
            wx.ID_ANY,
            u"Pročišćeni titlovi",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText8.Wrap(-1)

        gSizer1.Add(
            self.staticText8, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.textCtrl4 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl4, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.textCtrl8 = wx.TextCtrl(
            self.panel_1,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer1.Add(
            self.textCtrl8, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        bSizer3.Add(gSizer1, 1, wx.ALL | wx.EXPAND, 5)

        self.panel_1.SetSizer(bSizer3)
        self.panel_1.Layout()
        bSizer3.Fit(self.panel_1)
        self.listbook1.AddPage(self.panel_1, u"Ekstenzije", True)
        self.panel_2 = wx.Panel(
            self.listbook1,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL,
      )
        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        self.staticText_F = wx.StaticText(
            self.panel_2,
            wx.ID_ANY,
            f"Imena foldera kreiranih u opciji\n"
            f"Eksport ZIP multiple. Ako su folderi kreirani.",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_LEFT,
      )
        self.staticText_F.Wrap(-1)

        bSizer4.Add(self.staticText_F, 0, wx.ALL | wx.EXPAND, 5)

        gSizer2 = wx.GridSizer(4, 2, 5, 5)

        self.staticText9 = wx.StaticText(
            self.panel_2,
            wx.ID_ANY,
            u"Ćirilica ANSI",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        self.staticText9.Wrap(-1)

        gSizer2.Add(
            self.staticText9, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.staticText11 = wx.StaticText(
            self.panel_2, wx.ID_ANY, u"Ćirilica UTF-8", wx.DefaultPosition, wx.DefaultSize, 0
      )
        self.staticText11.Wrap(-1)

        gSizer2.Add(
            self.staticText11, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.textCtrl9 = wx.TextCtrl(
            self.panel_2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer2.Add(
            self.textCtrl9, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.textCtrl11 = wx.TextCtrl(
            self.panel_2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer2.Add(
            self.textCtrl11, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.staticText10 = wx.StaticText(
            self.panel_2, wx.ID_ANY, u"Latinica ANSI", wx.DefaultPosition, wx.DefaultSize, 0
      )
        self.staticText10.Wrap(-1)

        gSizer2.Add(
            self.staticText10, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.staticText12 = wx.StaticText(
            self.panel_2, wx.ID_ANY, u"Latinica UTF-8", wx.DefaultPosition, wx.DefaultSize, 0
      )
        self.staticText12.Wrap(-1)

        gSizer2.Add(
            self.staticText12, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 5
      )

        self.textCtrl10 = wx.TextCtrl(
            self.panel_2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer2.Add(
            self.textCtrl10, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        self.textCtrl12 = wx.TextCtrl(
            self.panel_2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
      )
        gSizer2.Add(
            self.textCtrl12, 1, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5
      )

        bSizer4.Add(gSizer2, 0, wx.ALL | wx.EXPAND, 5)

        self.panel_2.SetSizer(bSizer4)
        self.panel_2.Layout()
        bSizer4.Fit(self.panel_2)
        self.listbook1.AddPage(self.panel_2, u"Eksport ZIP", False)
        
        self.panel_3 = wx.Panel(
            self.listbook1,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TAB_TRAVERSAL,
       )
        sbSizer1 = wx.StaticBoxSizer(
            wx.StaticBox(self.panel_3, wx.ID_ANY, wx.EmptyString), wx.VERTICAL
       )
    
        self.staticText15 = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Izbor boje fonta u tekstu",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_LEFT,
       )
        self.staticText15.Wrap(-1)
    
        self.staticText15.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Franklin Gothic Medium",
           )
       )

        sbSizer1.Add(self.staticText15, 0, wx.ALL | wx.EXPAND, 5)

        self.bpButton1 = wx.BitmapButton(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            wx.NullBitmap,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BU_AUTODRAW | 0,
       )

        self.bpButton1.SetDefault()

        self.bpButton1.SetBitmap(
            wx.Bitmap(join("resources", "icons", "colors.png"), wx.BITMAP_TYPE_ANY)
       )
        self.bpButton1.SetToolTip("Otvara kolor dijalog")
        sbSizer1.Add(self.bpButton1, 0, wx.ALL, 5)
        
        self.m_staticText17 = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"Trenutni font:",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
       )
        self.m_staticText17.Wrap(-1)

        sbSizer1.Add(self.m_staticText17, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        
        self.ExampleText = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            u"AaBbCcDdEeČčĆćŽžĐđŠš\tţ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_LEFT,
       )
        self.ExampleText.Wrap(-1)
        
        ex = FILE_SETTINGS['key4']
        
        self.curClr = ex['fontColour']
        
        self.ExampleText.SetFont(
            wx.Font(
                16,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                False,
                ex["new_font"],
           )
       )
        self.ExampleText.SetForegroundColour(self.curClr)
        try:
            ex = FILE_SETTINGS["key5"]
            self.textCtrl1.SetValue(ex['cyr_ansi_srt'])
            self.textCtrl2.SetValue(ex['cyr_utf8_srt'])
            self.textCtrl3.SetValue(ex['lat_utf8_srt'])
            self.textCtrl4.SetValue(ex['transcribe'])
            self.textCtrl5.SetValue(ex['cyr_utf8_txt'])
            self.textCtrl6.SetValue(ex['lat_ansi_srt'])
            self.textCtrl7.SetValue(ex['fixed_subs'])
            self.textCtrl8.SetValue(ex['cleanup'])
            self.textCtrl9.SetValue(ex["Cyr-ansi"])
            self.textCtrl10.SetValue(ex["Lat-ansi"])
            self.textCtrl11.SetValue(ex["Cyr-utf8"])
            self.textCtrl12.SetValue(ex["Lat-utf8"])
        except Exception as e:
            logger.debug(f"Settings: {e}")        

        sbSizer1.Add(self.ExampleText, 0, wx.ALL|wx.EXPAND, 12)

        self.panel_3.SetSizer(sbSizer1)
        self.panel_3.Layout()
        sbSizer1.Fit(self.panel_3)
        self.listbook1.AddPage(self.panel_3, u"Boja fonta", False)
    
        bSizer2.Add(self.listbook1, 1, wx.ALL | wx.EXPAND, 5)

        bSizer1.Add(bSizer2, 1, wx.EXPAND, 5)

        sdbSizer2 = wx.StdDialogButtonSizer()
        self.sdbSizer2OK = wx.Button(self, wx.ID_OK)
        sdbSizer2.AddButton(self.sdbSizer2OK)
        self.sdbSizer2Cancel = wx.Button(self, wx.ID_CANCEL)
        sdbSizer2.AddButton(self.sdbSizer2Cancel)
        sdbSizer2.Realize()

        bSizer1.Add(sdbSizer2, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)
        
        # Connect Events
        self.bpButton1.Bind(wx.EVT_BUTTON, self.onButton)
        self.sdbSizer2Cancel.Bind(wx.EVT_BUTTON, self.onCancel)
        self.sdbSizer2OK.Bind(wx.EVT_BUTTON, self.saveSettings)
        self.Bind(wx.EVT_CLOSE, self.onClose, id=wx.ID_ANY)
        
    def onButton(self, event):
        """"""        
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour().Get(includeAlpha=False)
            self.ExampleText.SetForegroundColour(color)
            self.curClr = color
            self.Refresh()
        dlg.Destroy() 
        event.Skip()

    def onCancel(self, event):
        self.Destroy()
        event.Skip()
        
    def onClose(self, event):
        """"""
        self.Destroy()
        event.Skip()
        
    def saveSettings(self, event):
        try:
            FILE_SETTINGS["key5"] = {
                'cyr_ansi_srt': self.textCtrl1.GetValue(),
                'cyr_utf8_srt': self.textCtrl2.GetValue(),
                'lat_utf8_srt': self.textCtrl3.GetValue(),
                'transcribe': self.textCtrl4.GetValue(),
                'cyr_utf8_txt': self.textCtrl5.GetValue(),
                'lat_ansi_srt': self.textCtrl6.GetValue(),
                'fixed_subs': self.textCtrl7.GetValue(),
                'cleanup': self.textCtrl8.GetValue(),
                "Cyr-ansi": self.textCtrl9.GetValue(),
                "Lat-ansi": self.textCtrl10.GetValue(),
                "Cyr-utf8": self.textCtrl11.GetValue(),
                "Lat-utf8": self.textCtrl12.GetValue(),
            }
            FILE_SETTINGS["key4"]["fontColour"] = self.curClr
        except Exception as e:
            logger.debug(f"Settings: {e}")        
        event.Skip()        
    
    def GetColor(self):
        return self.curClr
        

class MyApp(wx.App):
    def OnInit(self):
        self.dialog = SettingsDialog(None, wx.ID_ANY, "")
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
