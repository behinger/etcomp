#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 12:42:47 2018

@author: behinger
"""


class Global_Container(object):
    pass


import functions.add_path
from video_capture import init_playback_source, EndofVideoError, FileSeekError
cap = init_playback_source(Global_Container(), '/net/store/nbp/projects/etcomp/pilot/inga/raw/world.mp4')