function [] = expPupilDilation(screen,randomization, eyetracking, requester, block)
showInstruction('DILATION',screen,requester,eyetracking, block);

dilation.win = screen.win;
sendETNotifications(eyetracking,requester,sprintf('DILATION start, block %d',block));

newVersion = 1
if newVersion

  for color_id = 1:length(randomization)
      dilation.background_color = randomization(color_id);

      Screen('FillRect', screen.win, [randomization(color_id) randomization(color_id) randomization(color_id)]);
      drawTarget(screen.screen_width/2, screen.screen_height/2,dilation,20,'fixbulleye');

      if randomization(color_id) == 0 %if black, wait 10s, else wait 3 second
        waitBaseTime = 10;
      else
        waitBaseTime = 3;
      end

      if color_id == 1
        LastFlip = flip_screen(screen, 0);
      else
        LastFlip = flip_screen(screen, LastFlip + waitBaseTime + rand(1) * 0.5 - 0.25);
      end
      sendETNotifications(eyetracking,requester,sprintf('DILATION lum %d block %d',randomization(color_id),block))



  end

else
  %run old version
for color_id = 1:length(randomization)
    dilation.background_color = randomization(color_id);

    Screen('FillRect', screen.win, [randomization(color_id) randomization(color_id) randomization(color_id)]);
    drawTarget(screen.screen_width/2, screen.screen_height/2,dilation,20,'fixbulleye');

    if color_id == 1
      LastFlip = flip_screen(screen, 0);
    else
      LastFlip = flip_screen(screen, LastFlip + 7.5 + rand(1) * 0.5 - 0.25);
    end
    sendETNotifications(eyetracking,requester,sprintf('DILATION lum %d block %d',randomization(color_id),block))



end

end % newversion if

sendETNotifications(eyetracking,requester,sprintf('DILATION stop, block %d', block));
