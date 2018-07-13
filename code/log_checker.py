#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 20:46:59 2018

@author: kgross
"""

import glob

logfiles = glob.glob('/net/store/nbp/projects/etcomp/log_files/*.log')

for logfile in logfiles:
    with open(logfile) as lf:
        content = lf.read()
        
        needle = 'Error, even after reloading the data once, found sampling time above 1*e100. This is clearly wrong. Investigate'
        
        if needle in content:
            print(logfile)
        
