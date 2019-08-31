#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Mon Aug 26 00:33:16 2019
#

import wx
import wx.html as html
import os

page = 'resources\\uputstvo.htm'

if not os.path.exists(page):
    # HTML String
    html = """
    <table border=1>
         <tr>
           <th>Number</th>
           <th>Square</th>
         </tr>
         <indent>
         <% for i in range(10): %>
           <tr>
             <td><%= i %></td>
             <td><%= i**2 %></td>
           </tr>
         </indent>
    </table>
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
        self.SetSize((574, 495))
        self.SetTitle("Subtitle Converter - Uputstvo")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("resources\\icons\\tool.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((574, 495))
        
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