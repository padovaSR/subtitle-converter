#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Mon Aug 26 00:33:16 2019
#

import wx
import wx.html as html
import os

page = os.path.join('resources','uputstvo.htm')

if not os.path.exists(page):
    # HTML String
    html = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
   <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">
   <META NAME="GENERATOR" CONTENT="Mozilla/4.06 [en] (X11; I; Linux
   2.0.35 i686) [Netscape]">

</HEAD>

<BODY TEXT="#808080" BGCOLOR="#ebf5fb" LINK="#0000FF" VLINK="#FF0000" ALINK="#000088">

<H1><FONT COLOR="#616B87">Subtitle Converter v-0.5.8</FONT></H1>

<BR>&nbsp;

<H2>
<FONT COLOR="#777F95">Prečice:</FONT></H2>

<P><B><FONT COLOR="#777F95">Ctrl+Shift+F</B></FONT>
: FileSettings dijalog, predefinisani "pre presufiks" novih fajlova(lat,cyr,utf8...)</P>

<BR>&nbsp;

<H2>
<FONT COLOR="#777F95">Ativirus alarm:</FONT></H2>
<P>Ako Avast ili neki drugi AV program prepoznaje SubtitleConverter.exe kao pretnju<br>
ili neku vrstu virusa, to je takozvani "False Positive" ili lažni alarm.</br>

<p><b><FONT COLOR="#777F95">Reference:</font></b>
<p>https://malware.wikia.org/wiki/False_positive<br>
https://support.avast.com/en-ww/article/168/</br>
<br>https://www.windowscentral.com/how-exclude-files-and-folders-windows-defender-antivirus-scans</br></p>

<br>&nbsp;

<h2><font color="#777F95">Actions</font></h2>
<p>Akcije iz menija <b>Actions</b> se nastavjaju jedna na drugu. Bilo kojim redom<br>
Promene će biti sačuvane kao što su prikazane u prozoru programa.<br>
Postoje opcije u meniju <b>Edit</b> Undo i Redo akcije.</br></p>

<br>&nbsp;

<h2><font color="#777F95">Preslovljavanje</font></h2>
<p>Teks titla se preslovljava iz Latinice u Ćirilicu i obratno. Tekst unutar tagova: <b>&lt; &gt;</b> ostaje u latinici.<br>
Slova unutar tagova kojih nema u kodnom rasporedu <b>windows-1251: ŠšđĐĆćČčŽž</b>, će se sačuvati samo u UTF-8 tekstu,<br>
u ANSI tekstu će umesto biti znakovi pitanja: <b>?</b>
Opcije za preslovljavanje iz Ćirilice u Latinicu nalaze se u meniju <b>Actions: Cyr to latin ansi, Cyr to latin utf8</b></br></p>

<br>&nbsp;

<h2><font color="#777F95">Reload</font></h2>
<p>U meniju <b>File</b> postoji opcija "Reload file" kojom se ponovo otvara i učitava trenutni fajl. Sve promene u fajlu<br>
koje su nastale u međuvremenu će biti učitane u radni tekst.<br>
U meniju <b>Edit</b> postoji opcija "Reload text", ova opcija samo ponovo učitava početni tekst a pri tome ne otvara ponovo fajl koji u međuvremenu može biti promenjen.</br></p>

<br>&nbsp;

</BODY>
</HTML>
    """
    
    # Write HTML String to file.html
    with open(page, "w") as file:
        file.write(html) 
    

class MyHtmlWindow(html.HtmlWindow):
    def __init__(self, parent, id):
        html.HtmlWindow.__init__(self, parent, id, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        
    def OnSetTitle(self, title):
        super(MyHtmlWindow, self).OnSetTitle(title)

class MyManual(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetTitle("Subtitle Converter - Uputstvo")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(os.path.join("resources","icons","tool.ico"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((780, 680))
        
        htmlwin = MyHtmlWindow(self, -1)
        htmlwin.LoadPage(page)        
        
        self.Layout()
        # end wxGlade

# end of class MyDialog

class MyApp(wx.App):
    def OnInit(self):
        self.dialog = MyManual(None, wx.ID_ANY, "")
        self.SetTopWindow(self.dialog)
        self.dialog.Show()
        # self.dialog.Destroy()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
