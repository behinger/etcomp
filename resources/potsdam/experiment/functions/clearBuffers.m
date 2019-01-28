function clearBuffers
% clear mouse and keyboard buffers

[Mx My Mb]=GetMouse;
while KbCheck | ~all(Mb==0)
    [Mx My Mb]=GetMouse;
end