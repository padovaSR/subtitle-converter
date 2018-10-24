#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import zipfile
import sys
import os
import pysrt
import pickle
import wx
from textwrap import TextWrapper

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
        if t1 > t2 or t2 - t1 < 85:
            k += 1
            t_fix = pysrt.SubRipTime.from_ordinal((second.start.ordinal) - 70)
            sub = pysrt.SubRipItem(first.index, first.start, t_fix, first.text)
            new_j.append(sub)
        else:
            sub = pysrt.SubRipItem(first.index, first.start, first.end, first.text)
            new_j.append(sub)

    sub = pysrt.SubRipItem(subs[-1].index, subs[-1].start, subs[-1].end, subs[-1].text)
    new_j.append(sub)
    
    new_f = pysrt.SubRipFile()
    fsub = pysrt.SubRipItem(new_j[0].index, new_j[0].start, new_j[0].end, new_j[0].text)
    new_f.append(fsub)

    for first, second in zip(new_j, new_j[1:]):

        t1 = first.end.ordinal
        t2 = second.start.ordinal
        if t2 - t1 < 100:

            t1_fix = pysrt.SubRipTime.from_ordinal((second.start.ordinal) + 15)
            subf = pysrt.SubRipItem(second.index, t1_fix, second.end, second.text)
            new_f.append(subf)
        else:
            subf = pysrt.SubRipItem(second.index, second.start, second.end, second.text)
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
        
    def line_adjust(self, intext):
        # function for text wrapping and filling
        def myWrapper(intext):
            f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
            n = len(intext) // 2
            wrapper = TextWrapper(break_long_words=False, break_on_hyphens=False, width=n)
            te = wrapper.fill(intext)
            if te.count('\n') >= 2:
                te = f_rpl.sub(r'\1 ', te)
            elif te.count('\n') >= 3:
                te = f_rpl.sub(r'\1 ', te)
            elif te.count('\n') >= 4:
                te = f_rpl.sub(r'\1 ', te)
            elif te.count('\n') >= 5:
                te = f_rpl.sub(r'\1 ', te)
            elif te.count('\n') == 6:
                te = f_rpl.sub(r'\1 ', te)
            return te            
        # function to move words and characters by its position
        def movPos(text, n):
            # where - pozicija gde se nalazi zeljeni spejs
            text = text.replace('\n', ' ')
            where = [m.start() for m in re.finditer(' ', text)][n-1]
            # before - tekst ispred pozicije
            before = text[:where]
            # after - tekst iza pozicije
            after = text[where:]
            after = after.replace(' ', '\n', 1)  # zameni prvi spejs
            newText = before + after
            return newText
        
        n = intext
        f_rpl = re.compile(r'^((.*?\n.*?){1})\n')
        s_rpl = re.compile(' +')
        tag_rpl = re.compile(r'<[^<]*>')
        new_s = pysrt.SubRipFile()        
        n = n.replace('\r', '').replace('\n', ' ')
        n = s_rpl.sub(' ', n)  # vise spejseva u jedan
        ln = n.replace(',', '').replace('.', '').replace('!', '').replace("'", "")
        ln = tag_rpl.sub(' ', ln)
        ln = s_rpl.sub(' ', ln)
        if len(ln) >= 30:
            s1 = myWrapper(n)
            prva = s1.split('\n')[0]
            druga = s1.split('\n')[-1]
            druga = tag_rpl.sub(' ', druga)
            druga = s_rpl.sub(' ', druga)                
            len_prva = len("".join(prva)); len_druga = len("".join(druga))
            tar1 = len_prva - len_druga
            tar2 = len_druga - len_prva
            if tar1 >= 4 or tar2 >= 4:
                s1 = myWrapper(s1)
                fls1 = tag_rpl.sub(' ', s1)
                fls1 = s_rpl.sub(' ', fls1)                        
                drugaS = len("".join(fls1.split('\n')[-1]))
                prvaS = len("".join(fls1.split('\n')[0]))
                if drugaS - prvaS >= 4:
                    fls1 = tag_rpl.sub(' ', s1)
                    fls1 = s_rpl.sub(' ', fls1)
                    lw = fls1.split('\n')[-1].split()
                    lw = [i.replace('.', '').replace('!', '').replace(',', '').replace("'", "") for i in lw]
                    dw = [len(x) for x in lw]           # duzine reci u listi
                    c1 = s1.split('\n')[0].count(' ') + 1
                    if len(lw) >= 1:
                        if (dw[0] + prvaS) <= (drugaS - dw[0]) + 2:
                            c = c1 + 1
                            s1 = movPos(s1, c)
                            c1 = s1.split('\n')[0].count(' ') + 1
                            fls1 = tag_rpl.sub(' ', s1)
                            fls1 = s_rpl.sub(' ', fls1)                                 
                            drugaS = len("".join(s1.split('\n')[-1]))
                            prvaS = len("".join(s1.split('\n')[0]))
                            lw = s1.split('\n')[-1].split()
                            lw = [i.replace('.', '').replace('!', '').replace(',', '').replace("'", "") for i in lw]
                            dw = [len(x) for x in lw]                            
                            if len(lw) >= 2:
                                if (dw[1] + prvaS) <= (drugaS - dw[1]) + 1:
                                    c = c1 + 1
                                    s1 = movPos(s1, c)
                                    c1 = s1.split('\n')[0].count(' ') + 1
                                    fls1 = tag_rpl.sub(' ', s1)
                                    fls1 = s_rpl.sub(' ', fls1)                                         
                                    drugaS = len("".join(fls1.split('\n')[-1]))
                                    prvaS = len("".join(fls1.split('\n')[0]))                            
                sub = s1
            else:
                sub = s1
        else:
            sub = n
        return sub
        
