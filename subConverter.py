#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import wx

import os
import sys
import re
import string
import codecs

class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    def OnDropFiles(self, x, y, filenames):
        for name in filenames:
            
        return True
