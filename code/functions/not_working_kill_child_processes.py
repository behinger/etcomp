# -*- coding: utf-8 -*-


import subprocess, os, signal


def kill_child_processes():
    parent_id = os.getpid()
    ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_id, shell=True, stdout=subprocess.PIPE)
    ps_output = ps_command.stdout.read()
    ps_output = ps_output.decode()
    
    for pid_str in ps_output.strip().split("\n")[1:]:
        os.kill(int(pid_str), signal.SIGTERM)
np.sqrt(np.mean(np.square(np.diff(etsamples.loc[ix_fix, 'gx']))+np.square(np.diff(etsamples.loc[ix_fix, 'gy']))))