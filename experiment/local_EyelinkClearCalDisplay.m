function local_EyelinkClearCalDisplay(el)

Screen( 'FillRect',  el.window, el.backgroundcolour );	% clear_cal_display()
flip_screen(el.screen);
