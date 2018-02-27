function randomize_stimuli()
rand_grid_small=randperm(13); % small grid randomization
rand_grid_big=randperm(49);
rand_img=randperm(15);
%randomization dilation
%smooth pursuit

rand.small                = rand_grid_small;
rand.big                = rand_grid_big;
rand.img = rand_img
save('/net/store/nbp/users/iibs/ETComp/data/stimuli_randomization', 'rand')