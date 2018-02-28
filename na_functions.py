#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import zipfile
import sys
import os
import pysrt
import wx

from dictionaries import dictionary_0, dictionary_1, dictionary_2, specialReplace

def fixGaps(filein, kode):

    subs = pysrt.open(filein, encoding=kode)

    new_j = []
    for first, second in zip(subs, subs[1:]):  
        t1 = first.end.ordinal
        t2 = second.start.ordinal
        if t1 > t2 or t2 - t1 < 75:
            first.shift(milliseconds=-25)
            t_fix = pysrt.SubRipTime.from_ordinal((second.start.ordinal) - 100)
            new_j.extend((first.index, format(first.start), format(t_fix), first.text))
        else:
            new_j.extend((first.index, format(first.start), format(first.end), first.text))
    
    new_1 = [new_j[i:i+4] for i in range(0,len(new_j), 4)]
    
    new_f = ''''''
    for i in new_1:
        new_f += '{0}\n{1} --> {2}\n{3}\n\n'.format(i[0], i[1], i[2], i[3])
    if not (len(subs) % 2) == 0:
        new_f += '{0}\n{1} --> {2}\n{3}\n\n{4}'.format(subs[-1].index, subs[-1].start, subs[-1].end, subs[-1].text, '')

    with open(filein, 'w', encoding=kode) as fw:
        new_f = new_f.replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').replace('</i> <i>', ' ').replace('</i><i>', '').replace('</i>\n<i>', '\n')
        fw.write(new_f)
    

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
        
