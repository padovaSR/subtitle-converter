# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.8.0b3
#

import wx
import os
import pickle
import shelve
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
handler = logging.FileHandler(
    filename=os.path.join("resources", "var", "log", "FileProcessing.log"),
    mode="a",
    encoding="utf-8",
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class Settings(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: Settings.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        # wx.Dialog.__init__(self, *args, **kwds)
        wx.Dialog.__init__(self, None, title="")
        self.SetSize((306, 286))

        self.label_1 = wx.StaticText(
            self,
            wx.ID_ANY,
            "Dužina trajanja spojenih linija (ms):",
            style=wx.ALIGN_LEFT,
        )
        self.spin_ctrl_1 = wx.SpinCtrl(
            self, wx.ID_ANY, style=wx.SP_ARROW_KEYS | wx.TE_PROCESS_ENTER
        )
        self.spin_ctrl_1.SetRange(0, 15000)
        # self.spin_ctrl_1.SetValue(lineLenght)

        self.label_2 = wx.StaticText(
            self,
            wx.ID_ANY,
            "Broj znakova spojenih linija:",
            style=wx.ALIGN_LEFT,
        )
        self.spin_ctrl_2 = wx.SpinCtrl(
            self, wx.ID_ANY, style=wx.SP_ARROW_KEYS | wx.TE_PROCESS_ENTER
        )
        self.spin_ctrl_2.SetRange(0, 200)
        # self.spin_ctrl_2.SetValue(maxChar)

        self.label_3 = wx.StaticText(
            self,
            wx.ID_ANY,
            "Dozvoljeni gap između linija (ms):",
            style=wx.ALIGN_LEFT,
        )
        self.spin_ctrl_3 = wx.SpinCtrl(
            self, wx.ID_ANY, style=wx.SP_ARROW_KEYS | wx.TE_PROCESS_ENTER
        )
        self.spin_ctrl_3.SetRange(0, 5000)
        # self.spin_ctrl_3.SetValue(maxGap)

        self.label_4 = wx.StaticText(
            self, wx.ID_ANY, "Sufiks novog fajla:", style=wx.ALIGN_LEFT
        )
        self.tctrl_1 = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER
        )
        # self.tctrl_1.SetValue(suffix)

        self.static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.button_1 = wx.Button(self, wx.ID_CLOSE, "")
        self.button_2 = wx.Button(self, wx.ID_SAVE, "")

        with shelve.open(
            os.path.join('resources', 'var', 'dialog_settings.db'),
            flag='writeback',
        ) as sp:
            ex = sp['key2']
            try:
                lineLenght = ex['l_lenght']
                maxChar = ex['m_char']
                maxGap = ex['m_gap']
                file_suffix = ex['f_suffix']
                self.tctrl_1.SetValue(file_suffix)
                self.spin_ctrl_3.SetValue(maxGap)
                self.spin_ctrl_2.SetValue(maxChar)
                self.spin_ctrl_1.SetValue(lineLenght)
            except Exception as e:
                logger.debug("MergerSettings: key error.")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onCloseSettings, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.onSaveSettings, self.button_2)
        self.Bind(wx.EVT_CLOSE, self.onClose, id=-1)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: Settings.__set_properties
        self.SetTitle("Merger settings")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(
            wx.Bitmap(
                os.path.join("resources", "icons", "tool.ico"),
                wx.BITMAP_TYPE_ANY,
            )
        )
        self.SetIcon(_icon)
        self.SetSize((301, 282))
        self.label_1.SetMinSize((123, 23))
        self.label_1.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )

        self.spin_ctrl_1.SetMinSize((115, 23))
        self.spin_ctrl_1.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )
        self.spin_ctrl_1.SetToolTip("Maksimalna dužina linije")

        self.label_2.SetMinSize((123, 23))
        self.label_2.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )

        self.spin_ctrl_2.SetMinSize((115, 23))
        self.spin_ctrl_2.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )
        self.spin_ctrl_2.SetToolTip(
            "Maksimalni broj znakova\nspojenih linija"
        )
        self.label_3.SetMinSize((123, 23))

        self.label_3.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )

        self.spin_ctrl_3.SetMinSize((115, 23))
        self.spin_ctrl_3.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )
        self.spin_ctrl_3.SetToolTip("Dozvoljeni gap između linija")

        self.label_4.SetMinSize((123, 23))
        self.label_4.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )

        self.tctrl_1.SetMinSize((115, 23))
        self.tctrl_1.SetFont(
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Segoe UI")
        )

        self.button_1.SetMinSize((86, 24))
        self.button_2.SetMinSize((86, 24))
        self.button_2.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: Settings.__do_layout
        self.sizer_4 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL
        )
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        self.grid_sizer_1 = wx.FlexGridSizer(5, 2, 2, 2)
        self.grid_sizer_1.Add(self.label_1, 1, wx.ALL | wx.EXPAND, 3)
        self.grid_sizer_1.Add(
            self.spin_ctrl_1, 0, wx.ALIGN_RIGHT | wx.ALL, 3
        )
        self.grid_sizer_1.Add(self.label_2, 1, wx.ALL | wx.EXPAND, 3)
        self.grid_sizer_1.Add(
            self.spin_ctrl_2, 0, wx.ALIGN_RIGHT | wx.ALL, 3
        )
        self.grid_sizer_1.Add(self.label_3, 1, wx.ALL | wx.EXPAND, 3)
        self.grid_sizer_1.Add(
            self.spin_ctrl_3, 0, wx.ALIGN_RIGHT | wx.ALL, 3
        )
        self.grid_sizer_1.Add(self.label_4, 1, wx.ALL | wx.EXPAND, 3)
        self.grid_sizer_1.Add(self.tctrl_1, 0, wx.ALIGN_RIGHT | wx.ALL, 3)
        self.grid_sizer_1.AddGrowableRow(0)
        self.grid_sizer_1.AddGrowableRow(1)
        self.grid_sizer_1.AddGrowableRow(2)
        self.grid_sizer_1.AddGrowableRow(3)
        self.grid_sizer_1.AddGrowableRow(4)
        self.grid_sizer_1.AddGrowableCol(0)
        self.sizer_4.Add(self.grid_sizer_1, 1, wx.ALL | wx.EXPAND, 3)
        sizer_5.Add(
            self.static_line_1,
            0,
            wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT,
            3,
        )
        self.sizer_6.Add(
            (20, 20),
            1,
            wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND,
            3,
        )
        self.sizer_6.Add(
            self.button_1,
            1,
            wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND,
            3,
        )
        self.sizer_6.Add(
            self.button_2,
            1,
            wx.ALIGN_BOTTOM
            | wx.ALIGN_RIGHT
            | wx.BOTTOM
            | wx.EXPAND
            | wx.LEFT
            | wx.TOP,
            3,
        )
        sizer_5.Add(self.sizer_6, 1, wx.ALL | wx.EXPAND, 3)
        self.sizer_4.Add(sizer_5, 0, wx.EXPAND, 0)
        self.SetSizer(self.sizer_4)
        self.Layout()
        # end wxGlade

    def onSaveSettings(self, event):  # wxGlade: Settings.<event_handler>
        line_Lenght = self.spin_ctrl_1.GetValue()
        max_Char = self.spin_ctrl_2.GetValue()
        max_Gap = self.spin_ctrl_3.GetValue()
        file_suffix = self.tctrl_1.GetValue()
        # config.write()
        konf = [line_Lenght, max_Char, max_Gap, file_suffix]
        a = konf[0]
        b = konf[1]
        c = konf[2]
        d = konf[3]  # ; e = konf[4]; f = konf[5]; g = konf[6]; h = konf[7]
        with shelve.open(
            os.path.join('resources', 'var', 'dialog_settings.db'),
            flag='writeback',
        ) as s:
            s['key2'] = {
                'l_lenght': a,
                'm_char': b,
                'm_gap': c,
                'f_suffix': d,
            }

        with open(
            os.path.join("resources", "var", "m_extensions.pkl"), "wb"
        ) as f:
            pickle.dump(file_suffix, f)

            self.Destroy()
        event.Skip()

    def onCloseSettings(self, event):  # wxGlade: Settings.<event_handler>
        self.Destroy()
        event.Skip()

    def onClose(self, event):
        self.Destroy()
        event.Skip()


# end of class Settings
class MyApp(wx.App):
    """"""

    def OnInit(self):
        """Constructor"""
        dialog_1 = Settings()
        # self.SetTopWindow(dialog_1)
        dialog_1.ShowModal()
        # dialog_1.Destroy()
        return True


if __name__ == "__main__":
    app = MyApp(False)
    # dialog_1 = Settings(None, -1, "")
    # dialog_1.ShowModal()
    # dialog_1.Destroy()
    app.MainLoop()
