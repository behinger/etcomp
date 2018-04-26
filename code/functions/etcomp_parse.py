# -*- coding: utf-8 -*-

import pandas as pd



def parse_message(msg):
    # Input: message to be parsed
    #        (e.g. notification from pldata['notifications'])
    # Output: pandas Series of the parsedmsg
    #         see ?Documentation? for whole dataframe
    
    #print(msg)
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
    
    split = string.split(' ')
    
    parsedmsg = pd.DataFrame()
    
    # if msg has label "GRID element", then extract infos:
    # msg_time:  timestamp when msg was sent
    # posx/posy: position of presented fixation point (ground truth) in pix on screen
    # total:     49=large Grid ; 13=calibration Grid
    # block:     block of experiment
    if split[0] == 'GRID' and split[1] == 'element':
        parsedmsg = dict(
              msg_time = msg_time,  
              element=int(split[2]),
             posx = float(split[4]),
             posy = float(split[6]),
             total = int(split[8]),
             block = int(split[10])
                )
 
    #TODO: other GRID labels  small GRID before / after
    
    
    
    # label "DILATION"
    # msg_time: timestamp when msg was sent
    # lum:      intensity of luminance
    # block:    block of experiment
    
    #??? 'DILATION start' ???
    
    if split[0] == 'DILATION' and split[1] == 'lum':
        parsedmsg = dict(
              msg_time = msg_time,  
              lum=int(split[2]),
              block = int(split[4])
                )
    
    
    # label "YAW"
    # msg_time: timestamp when msg was sent
    # trial:    trial number
    # block:    block of experiment
    if split[0] == 'YAW' and split[1] == 'trial':
        parsedmsg = dict(
              msg_time = msg_time,  
              trial = int(split[2]),
              block = int(split[4])
                )


    #['BLINK', 'start,', 'block', '2']
    #['BLINK', 'beep', '1', 'block', '2']
    #['BLINK', 'stop,'                     

    # label "BLINK"
    # msg_time: timestamp when msg was sent
    # exp_event:  experimental event of smooth pursuit (start, beep, stop)
    # beep:    number of beep
    # block:    block of experiment
    if split[0] == 'BLINK':
        print(msg)
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
        # TODO
        if split[1] == 'start' or 'stop':
            parsedmsg.update(dict(
                beep = int(split[2]),
                block = int(split[2])
                ))



    #['SMOOTH', 'PURSUIT', 'trialstart,', '', 'velocity', '16,', 'angle', '75,', 'trial', '20,', 'block', '2,']
    #['SMOOTH', 'PURSUIT', 'trialend,', '', 'trial', '20,', 'block', '2,']
    #['SMOOTH', 'PURSUIT', 'stop,', 'block', '2']

    # label "SMOOTH PURSUIT"
    # msg_time:   timestamp when msg was sent
    # exp_event:  experimental event of smooth pursuit (trialstart, trialend, stop)
    # vel:        velocity of stimulus
    # angl:       angle of moving stim in reference to ?vertical line? ?where 3 oclock equals 90 degrees? 0 <= angle <= 360
    # trial:      trial number
    # block:      block of experiment
    if split[0] == 'SMOOTH' and split[1] == 'PURSUIT':
        split = [remove_punctuation(elem) for elem in split]
        parsedmsg = dict(
              msg_time = msg_time,
              exp_event = split[2]
              )
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





    #['FREEVIEW', 'start,', 'block', '2']
    #['FREEVIEW', 'fixcross']
    #['FREEVIEW', 'trial', '1', 'id', '5', 'block', '2']
    #['FREEVIEW', 'stop,', 'block', '2']

    # label "FREEVIEW"
    # msg_time: timestamp when msg was sent
    # pic_id:   picture id
    # trial:    trial number
    # block:    block of experiment
    if split[0] == 'FREEVIEW' and split[1] == 'trial':
        parsedmsg = dict(
              msg_time = msg_time,  
              trial = int(split[2]),
              block = int(split[6]),
              pic_id = int(split[4])
                )


    # label "MICROSACC"
    # msg_time: timestamp when msg was sent
    # start:    if applicable True
    # stop:     if applicable True
    # block:    block of experiment
    if split[0] == 'MICROSACC':
        parsedmsg = dict(
              msg_time = msg_time,
              ms_startstop = split[1],
              block = int(split[3])              
                )
                 


    # label "Connect Pupil"
    # msg_time:         timestamp when msg was sent
    # connect_pupil:    True?????????
    if split[0] == 'Connect Pupil':
        parsedmsg = dict(
              msg_time = msg_time,
              connect_pupil = True
                )

    # I think this isnt in the test data yet
    # label "Rotation"
    # msg_time:         timestamp when msg was sent
    # rot:              True?????????
    if split[0] == 'Rotation':
        print(split)
        parsedmsg = dict(
              msg_time = msg_time,
              rot = True
                )
        
    # label "starting ET calib"
    # msg_time:         timestamp when msg was sent
    # calib_ET:         True?????????
    if split[0] == 'starting' and split[1] == 'ET':
        parsedmsg = dict(
              msg_time = msg_time,
              block = split[4],
              calib_ET = True
                )
        split[0] = 'startingET'

    # TODO : ['Finished']  ?Instruction?
    
    
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
