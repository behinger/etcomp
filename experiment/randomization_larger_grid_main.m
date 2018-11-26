
ix= [];

while size(ix,1) < 10
[ix2] = randomization_larger_grid();
ix= [ix; ix2];
[ix] = unique([ix],'rows');
end


save('randomization_larger_grid','ix')