#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# LOGGING INIT 

import time
import os,sys
import logging


# get a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# we want two handlers
# one for the sys.stdout (console)
# one for writing into the logfile

if len(logger.handlers) != 2:
    
    # create handlers
    logfile = os.path.join('/net/store/nbp/projects/etcomp/log_files', str('temp_' + time.strftime("%Y_%m_%d-%H-%M-%S") + '.log'))
    
    # final logfile name
    logfile = os.path.join('/net/store/nbp/projects/etcomp/log_files', str('log_preprocess_' + time.strftime("%Y_%m_%d-%H-%M-%S") + '.log'))
    
    # delete file if it already exists
    if os.path.isfile(logfile):
        os.remove(logfile)
    
    # define handlers    
    logging_file = logging.FileHandler(filename=logfile)
    logging_cons = logging.StreamHandler(sys.stdout)
    
    # set handler level
    logging_file.setLevel(logging.WARNING)
    logging_cons.setLevel(logging.DEBUG)
    
    # create a logging format
    formatter = logging.Formatter("%(asctime)s - %(name)-65s - %(levelname)-8s - %(message)s", "%Y-%m-%d %H:%M:%S")
    logging_file.setFormatter(formatter)
    logging_cons.setFormatter(formatter)
    
    # add the handlers to the logger
    logger.addHandler(logging_file)
    logger.addHandler(logging_cons)

else:
    print('Logger Already initialized? Found more than two handles')


# To close
#[h.close() for h in logger.handlers]
#[logger.removeHandler(h) for h in logger.handlers]


def update_logger_filepath(newpath):
    # delete old filehandler
    logger = logging.getLogger()
    for hdlr in logger.handlers[:]:  # remove all old handlers
        if isinstance(hdlr,logging.FileHandler):
            logger.removeHandler(hdlr)
    
    # delete file if it already exists
    if os.path.isfile(newpath):
        os.remove(newpath)
    
    # define handlers    
    logging_file = logging.FileHandler(filename=newpath)
    
    # set handler level
    logging_file.setLevel(logging.WARNING)
    
    # create a logging format
    formatter = logging.Formatter("%(asctime)s - %(name)-65s - %(levelname)-8s - %(message)s", "%Y-%m-%d %H:%M:%S")
    logging_file.setFormatter(formatter)
    
    # add the handlers to the logger
    logger.addHandler(logging_file)