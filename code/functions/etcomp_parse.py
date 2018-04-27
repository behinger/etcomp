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
        
    
    # if msg has label "GRID element", then extract infos:
    # msg_time:  timestamp when msg was sent
    # exp_event: experimental event of GRID (buttonpress, element, start, stop)
    # block:     block of experiment
        # for GRID element:    
        # element:   count of elements shown
        # posx/posy: position of presented fixation point (ground truth) in pix on screen
        # total:     49=large Grid ; 13=calibration Grid

    if split[0] == 'GRID':
        parsedmsg = dict(
                msg_time = msg_time,
                exp_event = split[1])
        
        # buttonpress is an exp_event with no additional information
        
        if split[1] == 'element':
            parsedmsg.update(dict(
                    element = int(split[2]),
                    posx = float(split[4]),
                    posy = float(split[6]),
                    total = int(split[8]),
                    block = int(split[10])
                    ))

        elif split[1] == 'start':
            parsedmsg.update(dict(
                    block = split[3]))
        
        #TODO check index again
        elif split[1] == 'stop':
            parsedmsg.update(dict(
                    block = split[2]))
           
         
    #TODO: other GRID labels  small GRID before / after
    
    
    
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
           
                
    # label "YAW"
    # msg_time: timestamp when msg was sent
    # exp_event: experimental event of YAW (start, stop, trial)
    # trial:    trial number
    # block:    block of experiment

    if split[0] == 'YAW':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[1])
        
        if split[1] == 'trial':
            parsedmsg.update(dict(
                  trial = int(split[2]),
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
              exp_event = split[2]
              )

        if split[1] == 'beep':
            parsedmsg.update(dict(
                beep = int(split[2]),
                block = int(split[2])
                ))

        if split[1] == 'start' or split[1] == 'stop':
            parsedmsg.update(dict(
                block = int(split[3])
                ))


    # label "SMOOTH PURSUIT"
    # msg_time:   timestamp when msg was sent
    # exp_event:  experimental event of SMOOTH PURSUIT (trialstart, trialend, stop)
    # block:      block of experiment
        # for "trialstart":
        # vel:        velocity of stimulus
        # angl:       angle of moving stim in reference to ?vertical line? ?where 3 oclock equals 90 degrees? 0 <= angle <= 360
        # trial:      trial number

    if split[0] == 'SMOOTH' and split[1] == 'PURSUIT':
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[2])
        
        # TODO: correct index again
        if split[2] == 'trialstart':
            parsedmsg.update(dict(
                vel = int(split[5]),
                angl = int(split[7]),
                trial = int(split[9]),
                block = int(split[11])
                ))

        if split[2] == 'trialend':
            parsedmsg.update(dict(
                trial = int(split[5]),
                block = int(split[7])
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
    # connect_pupil:    True
    
    # TODO: check is this is correct as there are no samples with this label
    if split[0] == 'Connect Pupil':
        print(split)
        parsedmsg = dict(
              msg_time = msg_time,
              connect_pupil = True
                )


    # label "Rotation"
    # msg_time:         timestamp when msg was sent
    # exp_event:        experimental event of Rotation ???
    # block:            block of experiment
    
    # TODO: check is this is correct as there are no samples with this label
    if split[0] == 'Rotation':
        print(split)
        parsedmsg = dict(
              msg_time = msg_time,
              rot = True
                )
        
        
    # label "starting ET calib"
    # msg_time:         timestamp when msg was sent
    # block:            block of experiment
    
    if split[0] == 'starting' and split[1] == 'ET':
        parsedmsg = dict(
              msg_time = msg_time,
              block = split[4],
              )
        split[0] = 'startingET'

  
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
