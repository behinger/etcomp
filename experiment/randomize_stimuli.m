function randomize_stimuli()
rand_grid_small=randperm(13); % small grid randomization
rand_grid_large=randperm(49);
rand_img=randperm(15);
%randomization dilation
%smooth pursuit

rand.small                = rand_grid_small;
rand.large                = rand_grid_large;
rand.img = rand_img;
save('data/stimuli_randomization', 'rand')