function rand = randomize_stimuli()
rng(1)
subjectlist = 1:40;
max_block = 6 ;
numberimagesperblock = 3;

randomization = load('randomization_larger_grid.mat');
rand_grid_large=randomization.ix;

monitorluminanceLookup = [64,128, 192,255];
dilation_blank_color = 0;% 0 is black

% currently we can make only 4 blocks, ~52s.
monitorluminance = repmat(1:length(monitorluminanceLookup),1,1);

%smooth pursuit
smooth_angle = 0:15:360 - 15;
smooth_speed = [16, 18, 20, 22, 24];


smooth_angle_sub = sort(repmat(smooth_angle,1,length(smooth_speed)));
smooth_speed_sub = repmat(smooth_speed,1,length(smooth_angle));

smooth_trials_per_block = length(smooth_angle_sub)/max_block;


tilt_angles = [0 5 -5 10 -10 15 -15];
tilt_angles = [tilt_angles tilt_angles];

shake_points = [2/3 1/3 0 -1/3 -2/3];
shake_points = [shake_points shake_points shake_points];

%initialize fields
rand = struct();
for fn = {'smallBefore','smallAfter','large','pupildilation','smoothpursuit_speed','smoothpursuit_angle','block','subject','freeviewing','firstmovement','shake','tilt'}
rand.(fn{1}) = [];
end

% generate randomization
for subject = subjectlist

    largeBlockPerm = randperm(max_block);
    smoothPerm = randperm(length(smooth_speed_sub));
    freeviewing = randperm(max_block*numberimagesperblock);

    for block = 1:max_block

        % accuracy tests / grids
        rand.smallBefore       = [rand.smallBefore {randperm(13)}];
        rand.smallAfter        = [rand.smallAfter  {randperm(13)}];
        rand.large             = [rand.large       {rand_grid_large(largeBlockPerm(block),:)}];


        % every luminance interdisperced by gray
        ix = randperm(length(monitorluminance));
        lum = ones(length(monitorluminance)*2,1)*dilation_blank_color;
        lum(2:2:2*length(monitorluminance)) = monitorluminanceLookup(monitorluminance(ix));
        rand.pupildilation = [rand.pupildilation {lum}];


        % smooth pursuit
        smooth_ix(1) = (block-1) * smooth_trials_per_block + 1;
        smooth_ix(2) = (block) * smooth_trials_per_block;
        rand.smoothpursuit_speed = [rand.smoothpursuit_speed {smooth_speed_sub(smoothPerm(smooth_ix(1):smooth_ix(2)))}];
        rand.smoothpursuit_angle = [rand.smoothpursuit_angle  {smooth_angle_sub(smoothPerm(smooth_ix(1):smooth_ix(2)))}];

        free_ix(1) = (block-1)*3+1;
        free_ix(2) = (block)*3;
        rand.freeviewing = [rand.freeviewing {freeviewing(free_ix(1):free_ix(2))}];

        % shake and Tilt
        movements = {'SHAKE','TILT'};
        rand.firstmovement =[rand.firstmovement  movements(1+mod(subject+block,2))];

        % shake
        while true
            % make sure no two following numbers are equal
            ix = randperm(length(shake_points));
            if all(diff(shake_points(ix))~=0)
                break

            end
        end
        rand.shake = [rand.shake {shake_points(ix)}];
        % Tilt
        while true
            % make sure no two following numbers are equal
            ix = randperm(length(tilt_angles));
            if all(diff(tilt_angles(ix))~=0)
                break

            end
        end
        rand.tilt = [rand.tilt {tilt_angles(ix)}];


        rand.block =    [rand.block block];
        rand.subject = [rand.subject subject];


    end

end


save('data/stimuli_randomization', 'rand')
