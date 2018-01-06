#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import zipfile
import sys
import os

import wx

class fileOpened(object):
    def isCompressed(self, infile):
        basepath = os.path.split(infile)[0]
        imeFajla = os.path.split(infile)[-1]
        with zipfile.ZipFile(infile, 'r') as zf:
            singlefajl = len(zf.namelist())
            if singlefajl == 1:
                jedanFajl = zf.namelist()[0]
                print(jedanFajl)
                outfile = os.path.join(basepath, jedanFajl)
                with open(outfile, 'wb') as f:
                    f.write(zf.read(jedanFajl))
            elif singlefajl > 1:
                izbor = [x for x in zf.namelist() if not x.endswith('/')]
                dlg = wx.SingleChoiceDialog(None, 'Pick one:', imeFajla, izbor)
                if dlg.ShowModal() == wx.ID_OK:
                    respond = dlg.GetStringSelection()
                    if respond:
                        namepath = os.path.basename(respond)
                        path = os.path.join(basepath, namepath)
                        print(respond)
                        try:
                            data = zf.read(respond)
                        except IOError as e:
                            errno, strerror = e.args
                            print('I/O Error occured! ({0}): {1}'.format(errno, strerror))
                        else:
                            with open(path, 'wb') as f:
                                f.write(zf.read(respond))
