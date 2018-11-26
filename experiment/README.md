# How to start
run ```ETcomp.m ```

# Combining Pupilabs and Psychotoolbox 
- we display  pupillabs surface markers using a modified flip screen functions [1] 
- we connect to pupillabs using zmq [2];  read [3] how we had to compile the mex under ubuntu - the available zmq-interfaces for matlab are buggy
- we send messages to pupil labs and record with our own plugin [4]. I recommend to exchange the special strings e.g. "r" for start recording with more sensible commands. "recording start" <- else strings like "remoteTrial" (due to initial "r") would trigger start recording as well. This script is adapted from pupillabs
- Important: Synchronization issues: checkout this line [5] in the pupillabs plugin. Here we get the timestamp of the most current timestamp. This is necessary because sometimes (in 30-40% of cases) we observed large drifts between cameras and recording computer clocks (github issue forthcoming) - and therefore also between the message/trigger-timestamp and the actual recording

The experimental code is collaborative work with Inga Ibs

----- Analysis ----
Here it gets more interesting. We want a fully reproducible analysis pipeline without manual steps (we dont want things like "start pupil player now and detect surfaces"). Therefore we interface calibration-functions and surface-detection functions directly from pupillabs. This unfortunately requires many libraries of pupillab to be compiled. Skip if you have compiled the pupillabs sofware already: Good news is: there is a make file & we do not need SUDO rights for most things, bad news there are 1 or 2 libraries that need to be installed using sudo [6]

If you need a detailed analysis pipeline, I think its best to look into the scripts [7] and [8]. There is quite a bit of overload because we need to analyse Eyelink  + Pupillabs at the same time. But I think the code is factored OK :smiley:
[1] https://github.com/behinger/etcomp/blob/master/experiment/flip_screen.m 
[2] https://github.com/behinger/etcomp/blob/master/experiment/ETcomp.m#L60 
[3] https://github.com/behinger/etcomp/blob/master/experiment/zmq/compile.m 
[4] https://github.com/behinger/etcomp/blob/master/experiment/plugins/nbp_pupil_remote.py 
[5] https://github.com/behinger/etcomp/blob/master/experiment/plugins/nbp_pupil_remote.py#L237 
