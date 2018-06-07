#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import zipfile
import sys
import os
import pysrt
import pickle
import wx

from dictionaries import dictionary_0, dictionary_1, dictionary_2, specialReplace

def fixGaps(filein, kode):

    subs = pysrt.open(filein, encoding=kode)

    new_j = pysrt.SubRipFile()
    k = 0
    pfp = 0
    for first, second in zip(subs, subs[1:]):  
        t1 = first.end.ordinal
        t2 = second.start.ordinal
        if t1 > t2:
            pfp += 1
        if t1 > t2 or t2 - t1 < 75:
            k += 1
            t_fix = pysrt.SubRipTime.from_ordinal((second.start.ordinal) - 50)
            sub = pysrt.SubRipItem(first.index, first.start, t_fix, first.text)
            new_j.append(sub)
        else:
            sub = pysrt.SubRipItem(first.index, first.start, first.end, first.text)
            new_j.append(sub)

    sub = pysrt.SubRipItem(subs[-1].index, subs[-1].start, subs[-1].end, subs[-1].text)
    new_j.append(sub)
    new_j.clean_indexes()
    
    new_f = pysrt.SubRipFile()
    fsub = pysrt.SubRipItem(new_j[0].index, new_j[0].start, new_j[0].end, new_j[0].text)
    new_f.append(fsub)

    for first, second in zip(new_j, new_j[1:]):

        t1 = first.end.ordinal
        t2 = second.start.ordinal
        if t1 > t2 or t2 - t1 < 100:

            t1_fix = pysrt.SubRipTime.from_ordinal((second.start.ordinal) + 25)
            subf = pysrt.SubRipItem(second.index, t1_fix, second.end, second.text)
            new_f.append(subf)
    
    new_f.clean_indexes()
    new_f.save(filein, encoding=kode)

    return k, pfp
     

class fileOpened:
    def isCompressed(self, infile):
        basepath = os.path.dirname(infile)
        imeFajla = os.path.basename(infile)
        with zipfile.ZipFile(infile, 'r') as zf:
            if len(zf.namelist()) == 1:
                jedanFajl = zf.namelist()[0]
                outfile = os.path.join(basepath, jedanFajl)
                with open('resources\\var\path0.pickle', 'wb') as pickl_file:
                    pickle.dump(outfile, pickl_file)
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
                        with open('resources\\var\path0.pickle', 'wb') as pickl_file:
                            pickle.dump(outfile, pickl_file)
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
                        
class fileProcessed:
    
    def writeTempStr(self, inFile, text, kode):
        with tempfile.TemporaryFile() as tfile:
            tfile.write(text.encode(kode))
            tfile.seek(0)
            content = tfile.read()
            with open(inFile, 'wb') as  out: #, encoding=enc) as out:
                out.write(content)
                
    def rm_dash(self, intext, kode):
        
        for_repls = re.compile(r'(?<=,\d\d\d\n)-+\s*')
        
        with open(intext, 'r', encoding=kode) as text_in:
            s = text_in.read()
            s1 = re.sub(for_repls, '', s)
            
        self.writeTempStr(intext, s1, kode) 
        
