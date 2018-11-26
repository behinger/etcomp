function [px] = degToPix(deg, distance)
pixelsize = 0.276/10; % 1 px in cm

ppd =  rad2deg(atan2(.5*pixelsize, distance)) * 2;
px = deg/ppd;