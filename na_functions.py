#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import zipfile
import sys
import os

import wx

from dictionaries import dictionary_0, dictionary_1, dictionary_2, specialReplace

def tc2ms(tc):
    ''' convert timecode to millisecond '''
    sign = 1
    if tc[0] in "+-":
        sign = -1 if tc[0] == "-" else 1
        tc = tc[1:]

    TIMECODE_RE = re.compile('(?:(?:(?:(\d?\d):)?(\d?\d):)?(\d?\d))?(?:[,.](\d?\d?\d))?')
    match = TIMECODE_RE.match(tc)
    try: 
        assert match is not None
    except AssertionError:
        print(tc)
    hh,mm,ss,ms = map(lambda x: 0 if x==None else int(x), match.groups())
    return ((hh*3600 + mm*60 + ss) * 1000 + ms) * sign


class fileOpened:
    def isCompressed(self, infile):
        basepath = os.path.dirname(infile)
        imeFajla = os.path.basename(infile)
        with zipfile.ZipFile(infile, 'r') as zf:
            if len(zf.namelist()) == 1:
                jedanFajl = zf.namelist()[0]
                print(jedanFajl)
                outfile = os.path.join(basepath, jedanFajl)
                with open(outfile, 'wb') as f:
                    f.write(zf.read(jedanFajl))
                return outfile
            elif len(zf.namelist()) > 1:
                izbor = [x for x in zf.namelist() if not x.endswith('/')]
                dlg = wx.SingleChoiceDialog(None, 'Pick one:', imeFajla, izbor)
                if dlg.ShowModal() == wx.ID_OK:
                    response = dlg.GetStringSelection()
                    if response:
                        namepath = os.path.basename(response)
                        outfile = os.path.join(basepath, namepath)
                        print(response)
                        try:
                            data = zf.read(response)
                        except IOError as e:
                            errno, strerror = e.args
                            print('I/O Error occured! ({0}): {1}'.format(errno, strerror))
                        else:
                            with open(outfile, 'wb') as f:
                                f.write(data)
                            return outfile
                    else: 
                        print('Canceled.')
        
