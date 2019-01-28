function Mb=clearMouse;

[Mx My Mb]=GetMouse;
while ~all(Mb==0)
    [Mx My Mb]=GetMouse;
end