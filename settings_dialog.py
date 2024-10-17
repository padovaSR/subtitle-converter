# -*- coding: utf-8 -*-

## Python code generated with wxFormBuilder (version 3.10.1-282-g1fa54006)
## http://www.wxformbuilder.org/
##
## modified by padovaSR

from os.path import join
from settings import MAIN_SETTINGS, I_PATH, main_settings_file

import logging.config

import wx

logger = logging.getLogger(__name__)

## Class SettingsDialog


class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE
        )

        self.SetTitle("Podešavanja programa")
        self.SetSize(540, 570)
        icon = wx.NullIcon
        icon.CopyFromBitmap(
            wx.Bitmap(join(I_PATH, "system-run.png"), wx.BITMAP_TYPE_ANY)
        )
        self.SetIcon(icon)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_panel1 = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.m_listbook2 = wx.Listbook(
            self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_DEFAULT
        )
        self.m_panel5 = wx.Panel(
            self.m_listbook2,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_THEME | wx.TAB_TRAVERSAL,
        )
        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        bSizer4.Add((2, 12), 0, 0, 0)

        self.staticText_a = wx.StaticText(
            self.m_panel5,
            wx.ID_ANY,
            f"Određuje se dodatna ekstenzija fajlova: *_cyr, *.lat...\n"
            f"Mogu se ostaviti prazna polja bez spejseva\n"
            f"i tada će originalni fajlovi biti prepisani.",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_a.Wrap(-1)

        bSizer4.Add(self.staticText_a, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 48)

        gSizer5 = wx.GridSizer(0, 2, 0, 50)
        
        static_font = wx.Font(
                8,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Segoe UI Semibold",
            )
        
        self.staticText_1 = wx.StaticText(
            self.m_panel5, wx.ID_ANY, u"Cyr ANSI", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.staticText_1.Wrap(-1)
        self.staticText_1.SetFont(static_font)

        gSizer5.Add(self.staticText_1, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.staticText_2 = wx.StaticText(
            self.m_panel5,
            wx.ID_ANY,
            u"Cyr utf8 txt",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_2.Wrap(-1)
        self.staticText_2.SetFont(static_font)
        gSizer5.Add(self.staticText_2, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.textCtrl_1 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_1, 0, wx.ALL, 5)

        self.textCtrl_2 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_2, 0, wx.ALL, 5)

        self.staticText_3 = wx.StaticText(
            self.m_panel5,
            wx.ID_ANY,
            u"Cyr utf8 srt",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_3.Wrap(-1)
        self.staticText_3.SetFont(static_font)
        gSizer5.Add(self.staticText_3, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.staticText_4 = wx.StaticText(
            self.m_panel5, wx.ID_ANY, u"Lat ANSI", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.staticText_4.Wrap(-1)
        self.staticText_4.SetFont(static_font)
        gSizer5.Add(self.staticText_4, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.textCtrl_3 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_3, 0, wx.ALL, 5)

        self.textCtrl_4 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_4, 0, wx.ALL, 5)

        self.staticText_5 = wx.StaticText(
            self.m_panel5, wx.ID_ANY, u"Lat utf8", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.staticText_5.Wrap(-1)
        self.staticText_5.SetFont(static_font)
        gSizer5.Add(self.staticText_5, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.staticText_6 = wx.StaticText(
            self.m_panel5, wx.ID_ANY, u"Cleanup", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.staticText_6.Wrap(-1)
        self.staticText_6.SetFont(static_font)
        gSizer5.Add(self.staticText_6, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.textCtrl_5 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_5, 0, wx.ALL, 5)

        self.textCtrl_6 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_6, 0, wx.ALL, 5)

        self.staticText_7 = wx.StaticText(
            self.m_panel5,
            wx.ID_ANY,
            u"Transcribe",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_7.Wrap(-1)
        self.staticText_7.SetFont(static_font)
        gSizer5.Add(self.staticText_7, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.staticText_8 = wx.StaticText(
            self.m_panel5, wx.ID_ANY, u"Fixed", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.staticText_8.Wrap(-1)
        self.staticText_8.SetFont(static_font)
        gSizer5.Add(self.staticText_8, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.textCtrl_7 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_7, 0, wx.ALL, 5)

        self.textCtrl_8 = wx.TextCtrl(
            self.m_panel5,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        gSizer5.Add(self.textCtrl_8, 0, wx.ALL, 5)

        bSizer4.Add(gSizer5, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.m_panel5.SetSizer(bSizer4)
        self.m_panel5.Layout()
        bSizer4.Fit(self.m_panel5)
        self.m_listbook2.AddPage(self.m_panel5, u"Ekstenzije", True)
        self.m_panel6 = wx.Panel(
            self.m_listbook2,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_THEME | wx.TAB_TRAVERSAL,
        )
        bSizer41 = wx.BoxSizer(wx.VERTICAL)

        self.staticText_b = wx.StaticText(
            self.m_panel6,
            wx.ID_ANY,
            f"Određuju se imena kreiranih foldera u opciji\n"
            f"Eksport ZIP multiple.\n"
            f"Ako je izbrana opcija za kreiranje foldera.",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_b.Wrap(-1)

        bSizer41.Add(self.staticText_b, 0, wx.ALL | wx.EXPAND, 18)

        fgSizer1 = wx.FlexGridSizer(4, 2, 8, 52)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.staticText_z1 = wx.StaticText(
            self.m_panel6,
            wx.ID_ANY,
            u"Ćirilica ANSI",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_z1.Wrap(-1)

        fgSizer1.Add(self.staticText_z1, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

        self.staticText_z2 = wx.StaticText(
            self.m_panel6,
            wx.ID_ANY,
            u"Ćirilica UTF8",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_z2.Wrap(-1)

        fgSizer1.Add(self.staticText_z2, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

        self.textCtrl_z1 = wx.TextCtrl(
            self.m_panel6,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        fgSizer1.Add(self.textCtrl_z1, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 12)

        self.textCtrl_z2 = wx.TextCtrl(
            self.m_panel6,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        fgSizer1.Add(self.textCtrl_z2, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 12)

        self.staticText_z3 = wx.StaticText(
            self.m_panel6,
            wx.ID_ANY,
            u"Latinica ANSI",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_z3.Wrap(-1)

        fgSizer1.Add(self.staticText_z3, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

        self.staticText_z4 = wx.StaticText(
            self.m_panel6,
            wx.ID_ANY,
            u"Latinica UTF8",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_z4.Wrap(-1)

        fgSizer1.Add(self.staticText_z4, 0, wx.ALIGN_BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

        self.textCtrl_z3 = wx.TextCtrl(
            self.m_panel6,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        fgSizer1.Add(self.textCtrl_z3, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 12)

        self.textCtrl_z4 = wx.TextCtrl(
            self.m_panel6,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, 27),
            0,
        )
        fgSizer1.Add(self.textCtrl_z4, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 12)

        bSizer41.Add(fgSizer1, 1, wx.ALL | wx.EXPAND, 12)

        self.m_panel6.SetSizer(bSizer41)
        self.m_panel6.Layout()
        bSizer41.Fit(self.m_panel6)
        self.m_listbook2.AddPage(self.m_panel6, u"Eksport ZIP", False)
        self.m_panel7 = wx.Panel(
            self.m_listbook2,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_THEME | wx.TAB_TRAVERSAL,
        )
        wSizer1 = wx.WrapSizer(wx.VERTICAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.staticText_c = wx.StaticText(
            self.m_panel7,
            wx.ID_ANY,
            u"Određuje se font i boja fonta",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_c.Wrap(-1)

        self.staticText_c.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Franklin Gothic Medium",
            )
        )

        wSizer1.Add(self.staticText_c, 0, wx.ALL | wx.EXPAND, 12)
        
        bSizer5 = wx.BoxSizer(wx.HORIZONTAL)

        self.bpButton = wx.BitmapButton(
            self.m_panel7,
            wx.ID_ANY,
            wx.NullBitmap,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BU_AUTODRAW | 0,
        )

        self.bpButton.SetBitmap(
            wx.Bitmap(join(I_PATH, "colors.png"), wx.BITMAP_TYPE_ANY)
        )
        self.bpButton.SetToolTip(u"Dijalog boje fonta")
        bSizer5.Add(self.bpButton, 0, wx.ALL, 12)
        
        self.bpButton1 = wx.BitmapButton(
            self.m_panel7,
                    wx.ID_ANY,
                    wx.NullBitmap,
                    wx.DefaultPosition,
                    wx.DefaultSize,
                    wx.BU_AUTODRAW | 0,
        )
        
        self.bpButton1.SetBitmap(
                wx.Bitmap(join(I_PATH, "Font-folder.48.png"), wx.BITMAP_TYPE_ANY)
            )
        self.bpButton1.SetToolTip(u"Font dijalog")
    
        bSizer5.Add(self.bpButton1, 0, wx.ALL, 12)
        wSizer1.Add(bSizer5, 1, wx.EXPAND, 5)

        self.staticText_c1 = wx.StaticText(
            self.m_panel7,
            wx.ID_ANY,
            u"Trenutni font:",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_c1.Wrap(-1)

        self.staticText_c1.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "Franklin Gothic Medium",
            )
        )

        wSizer1.Add(self.staticText_c1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 24)

        wSizer1.Add((2, 24), 0, 0, 5)

        self.staticText_fonts = wx.StaticText(
            self.m_panel7,
            wx.ID_ANY,
            u"AaBbCcDdEeČčĆćŽžĐđŠš",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.staticText_fonts.Wrap(-1)
        
        self.curClr = MAIN_SETTINGS["key4"]["fontColour"]        

        self.staticText_fonts.SetFont(
            wx.Font(
                MAIN_SETTINGS["key4"]["fontSize"],
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                MAIN_SETTINGS["key4"]["weight"],
                False,
                MAIN_SETTINGS["key4"]["new_font"],                
            )
        )
        self.staticText_fonts.SetForegroundColour(self.curClr)
        self.curFont = self.staticText_fonts.GetFont()
        try:
            ex = MAIN_SETTINGS["key5"]
            self.textCtrl_1.SetValue(ex['cyr_ansi_srt'])
            self.textCtrl_2.SetValue(ex['cyr_utf8_txt'])
            self.textCtrl_3.SetValue(ex['cyr_utf8_srt'])
            self.textCtrl_4.SetValue(ex['lat_ansi_srt'])
            self.textCtrl_5.SetValue(ex['lat_utf8_srt'])
            self.textCtrl_6.SetValue(ex['cleanup'])
            self.textCtrl_7.SetValue(ex['transcribe'])
            self.textCtrl_8.SetValue(ex['fixed_subs'])
            self.textCtrl_z1.SetValue(ex["Cyr-ansi"])
            self.textCtrl_z2.SetValue(ex["Cyr-utf8"])
            self.textCtrl_z3.SetValue(ex["Lat-ansi"])
            self.textCtrl_z4.SetValue(ex["Lat-utf8"])
        except Exception as e:
            logger.debug(f"Settings: {e}")        
        
        wSizer1.Add(
                    self.staticText_fonts, 0, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 24
                )        

        self.m_panel7.SetSizer(wSizer1)
        self.m_panel7.Layout()
        wSizer1.Fit(self.m_panel7)
        self.m_listbook2.AddPage(self.m_panel7, u"Font", False)

        bSizer3.Add(self.m_listbook2, 1, wx.EXPAND | wx.ALL, 5)

        self.m_panel1.SetSizer(bSizer3)
        self.m_panel1.Layout()
        bSizer3.Fit(self.m_panel1)
        bSizer1.Add(self.m_panel1, 1, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer1.AddButton(self.m_sdbSizer1OK)
        self.m_sdbSizer1Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer1.AddButton(self.m_sdbSizer1Cancel)
        m_sdbSizer1.Realize()
        m_sdbSizer1.SetMinSize(wx.Size(120, 27))

        #bSizer1.Add(m_sdbSizer1, 0, wx.BOTTOM | wx.RIGHT | wx.EXPAND, 7)
        bSizer1.Add(m_sdbSizer1, 0, wx.BOTTOM | wx.EXPAND, 5)
        
        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.bpButton.Bind(wx.EVT_BUTTON, self.OnColor)
        self.bpButton1.Bind(wx.EVT_BUTTON, self.OnFont)
        self.m_sdbSizer1Cancel.Bind(wx.EVT_BUTTON, self.onCancel)
        self.m_sdbSizer1OK.Bind(wx.EVT_BUTTON, self.saveSettings)
        self.Bind(wx.EVT_CLOSE, self.onClose, id=wx.ID_ANY)
        
    def OnColor(self, event):
        """"""        
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            color = data.GetColour().Get(includeAlpha=False)
            self.staticText_fonts.SetForegroundColour(color)
            self.curClr = color
            self.Refresh()
        dlg.Destroy() 
        event.Skip()
        
    def UpdateUI(self):
        self.staticText_fonts.SetFont(self.curFont)
        self.staticText_fonts.SetForegroundColour(self.curClr)
        self.staticText_fonts.Refresh()
        
    def OnFont(self, event):
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(self.curClr)
        data.SetInitialFont(self.curFont)

        dlg = wx.FontDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            colour = data.GetColour().Get(includeAlpha=False)
            
            self.curFont = font
            self.curClr = colour
            self.UpdateUI()        
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
            MAIN_SETTINGS["key5"] = {
                "cyr_ansi_srt": self.textCtrl_1.GetValue(), 
                "cyr_utf8_txt": self.textCtrl_2.GetValue(), 
                "cyr_utf8_srt": self.textCtrl_3.GetValue(), 
                "lat_ansi_srt": self.textCtrl_4.GetValue(), 
                "lat_utf8_srt": self.textCtrl_5.GetValue(), 
                "cleanup": self.textCtrl_6.GetValue(), 
                "transcribe": self.textCtrl_7.GetValue(), 
                "fixed_subs": self.textCtrl_8.GetValue(), 
                "Cyr-ansi": self.textCtrl_z1.GetValue(), 
                "Cyr-utf8": self.textCtrl_z2.GetValue(), 
                "Lat-ansi": self.textCtrl_z3.GetValue(), 
                "Lat-utf8": self.textCtrl_z4.GetValue(),                
            }
            MAIN_SETTINGS["key4"]["fontColour"] = self.curClr
            MAIN_SETTINGS["key4"]["fontSize"] = self.curFont.GetPointSize()
            MAIN_SETTINGS["key4"]["new_font"] = self.curFont.GetFaceName()
            MAIN_SETTINGS["key4"]["weight"] = self.curFont.GetWeight()
        except Exception as e:
            logger.debug(f"Settings: {e}")        
        self.EndModal(True)        
    
    def GetColor(self):
        return self.curClr
    
    def GetFont(self):
        return self.curFont
        

class MyApp(wx.App):
    def OnInit(self):
        self.dialog = SettingsDialog(None)
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
