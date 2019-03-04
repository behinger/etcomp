dT1 = load('delayedTriggers.mat')
dT2 = load('delayedTriggers2.mat')
dT3 = load('delayedTriggers3.mat')

hist([dT1.elapsedTimes dT2.elapsedTimes dT3.elapsedTimes]*1000,1000)

