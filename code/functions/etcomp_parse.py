# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def parse_message(msg):
    # Input: message to be parsed
    #        (e.g. notification from pldata['notifications'])
    # Output: pandas Series of the parsedmsg
    #         see "overview dataframe pdf"
    
    try:
        # for EyeLink
        msg_time = msg['msg_time']
        string = msg['trialid '] # space on purpose
        
    except:
        try:
        # for Pupillabs
            msg_time = msg['timestamp']
            string = msg['label']
        except:
                return(np.nan)
    
    # splits msg into list of str and removes punctuation
    split = string.split(' ')
    split = [remove_punctuation(elem) for elem in split]
    
    parsedmsg = pd.DataFrame()
        
    
    # if msg has label "GRID", then extract infos:
    # msg_time:  timestamp when msg was sent
    # exp_event: experimental event of GRID (buttonpress, element, start, stop)
    # block:     block of experiment
        # for GRID element:    
        # element:   count of elements shown
        # posx/posy: position of presented fixation point (ground truth) in pix on screen
        # grid_size:     49=large Grid ; 13=calibration Grid

    if split[0] == 'GRID':
        #print(split)
        parsedmsg = dict(
                msg_time = msg_time,
                exp_event = split[1])
        
        # buttonpress is an exp_event with no additional information
        
        # TODO mit if abfrage LARGEGG in LARGEGRID umbennen
        
        if split[1] == 'element':
            #print(split)
            parsedmsg.update(dict(
                    element = int(split[2]),
                    posx = float(split[4]),
                    posy = float(split[6]),
                    grid_size = int(split[8]),
                    block = int(split[10])
                    ))
            
        #TODO did you mean this with grid_small_before
        # but how do i know if it is before or after ??
        elif split[1] == 'element' and split[8] == '13':
            parsedmsg.update(dict(
                    exp_event = 'small_grid_before',
                    element = int(split[2]),
                    posx = float(split[4]),
                    posy = float(split[6]),
                    grid_size = int(split[8]),
                    block = int(split[10])
                    ))            

        elif split[1] == 'start':
            parsedmsg.update(dict(
                    block = int(split[3])))

        elif split[1] == 'stop':
            parsedmsg.update(dict(
                    block = int(split[3])))

    
    # label "DILATION"
    # msg_time: timestamp when msg was sent
    # exp_event: experimental event of DILATION (start, stop, lum)
    # lum:      intensity of luminance
    # block:    block of experiment

    if split[0] == 'DILATION':
        parsedmsg = dict(
              msg_time = msg_time,  
              exp_event = split[1])
        
        if split[1] == 'lum':
            parsedmsg.update(dict(
                  lum=int(split[2]),
                  block = int(split[4])
                    ))
            
        elif split[1] == 'start' or split[1] == 'stop':
            parsedmsg.update(dict(
                  block = int(split[3])
                    ))
           
                

    # label "BLINK"
    # msg_time: timestamp when msg was sent
    # exp_event:  experimental event of BLINK (start, beep, stop)
    # beep:    number of beep
    # block:    block of experiment

    if split[0] == 'BLINK':
        parsedmsg = dict(
              msg_time = msg_time,  
              exp_event = split[1]
              )

        if split[1] == 'beep':
            parsedmsg.update(dict(
                beep = int(split[2]),
                block = int(split[4])
                ))

        if split[1] == 'start' or split[1] == 'stop':
            parsedmsg.update(dict(
                block = int(split[3])
                ))


    # label "SMOOTH PURSUIT"
    # msg_time:   timestamp when msg was sent
    # exp_event:  experimental event of SMOOTH PURSUIT (trialstart, trialend, stop)
        # for "trialstart":
        # vel:        velocity of stimulus
        # angle:       angle of moving stim in reference to ?vertical line? ?where 3 oclock equals 90 degrees? 0 <= angle <= 360
        # trial:      trial number
        # block:      block of experiment
        
    if split[0] == 'SMOOTH' and split[1] == 'PURSUIT':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[2])

        if split[2] == 'start':
            parsedmsg.update(dict(
                block = int(split[4])
                ))
        
        if split[2] == 'trialstart':
            parsedmsg.update(dict(
                vel = int(split[4]),
                angle = int(split[6]),
                trial = int(split[8]),
                block = int(split[10])
                ))

        if split[2] == 'trialend':
            parsedmsg.update(dict(
                trial = int(split[4]),
                block = int(split[6])
                ))

        if split[2] == 'stop':
            parsedmsg.update(dict(
                block = int(split[4])
                ))


    # label "FREEVIEW"
    # msg_time: timestamp when msg was sent
    # exp_event:  experimental event of FREEVIEW (trial, fixcross, start, stop)
    # trial:    trial number
    # pic_id:   picture id
    # block:    block of experiment
   
    if split[0] == 'FREEVIEW':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[1])

        if split[1] == 'trial':
            parsedmsg.update(dict(    
                  trial = int(split[2]),
                  pic_id = int(split[4]),
                  block = int(split[6])
                  ))

        if split[1] == 'start' or split[1] == 'stop':
            parsedmsg.update(dict(
                block = int(split[3])
                ))


    # label "MICROSACC"
    # msg_time: timestamp when msg was sent
    # exp_event:  experimental event of MICROSACC (start, stop)
    # block:    block of experiment

    if split[0] == 'MICROSACC':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[1],
              block = int(split[3]))
               

    # label "Connect Pupil"
    # msg_time:         timestamp when msg was sent
    # exp_event:        connectpupil
    
    # TODO: check is this is correct
    if split[0] == 'Connect'and split[1] == 'Pupil':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = "ConnectPupil")
     
        
    # label "starting ET calib"
    # msg_time:         timestamp when msg was sent
    # block:            block of experiment
    
    if split[0] == 'starting' and split[1] == 'ET':
        parsedmsg = dict(
              msg_time = msg_time,
              block = int(split[4]))
        split[0] = 'startingET'


    # label "Finished"
    # msg_time:         timestamp when msg was sent
    # exp_event:        True when Experiment is finished  ??

    if split[0] == 'Finished':
        print(split)
        parsedmsg = dict(
              msg_time = msg_time,                
              exp_event = 'exp_finished')


    # label "Instruction"
    # msg_time:         timestamp when msg was sent
    # exp_event:        specifys for which condition Instruction was sent (start, end)
    # block:            block of experiment
  
    if split[0] == 'Instruction':
        parsedmsg = dict(
              msg_time = msg_time,                
              exp_event = str(split[2]) + '_' + str(split[3]),
              block = int(split[5]))


    # label "SHAKE"
    # msg_time:         timestamp when msg was sent
    # exp_event:        experimental event of SHAKE (start, center, stop)
    # block:            block of experiment
  
    if split[0] == 'SHAKE':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[1])
    
        if split[3] == 'x':
            parsedmsg.update(dict(
                shake_x = int(split[4]),
                shake_y = int(split[6]),
                block = int(split[2]),
                exp_event = 'SHAKE_point'
                ))

        if split[1] == 'start' or split[1] == 'stop':
            parsedmsg.update(dict(
                block = int(split[3])
                ))

        elif split[3] == 'center':
            parsedmsg.update(dict(
                block = int(split[2]),
                exp_event = 'shake_center',
                # is it okay that i put (0,540) as center?
                shake_x = 0,
                shake_y = 540,
                ))     
        
        
    # label "TILT"
    # msg_time:         timestamp when msg was sent
    # exp_event:        experimental event of TILT (start, stop, trial)
    # block:            block of experiment
    
    # TODO  I dont find tilt in PL
    
    if split[0] == 'TILT':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[1])
    
        if split[1] == 'angle':
            parsedmsg.update(dict(
                angle = int(split[2]),
                block = int(split[4])
                ))

        if split[1] == 'start' or split[1] == 'stop':
            parsedmsg.update(dict(
                block = int(split[3])
                ))


    # TODO: check if parsed for everything
    #labels.add(split[0])
    
    # add column for condition
    parsedmsg['condition'] = split[0] 

    return(pd.Series(parsedmsg))
    
    
    


def remove_punctuation(s):
    string_punctuation = ".,;"
    no_punct = ""
    for letter in s:
        if letter not in string_punctuation:
            no_punct += letter
    return no_punct
