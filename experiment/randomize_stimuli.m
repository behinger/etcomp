function rand = randomize_stimuli()
rng(1)
subjectlist = 1:40;
max_block = 6;
numberimagesperblock = 3;

randomization = load('randomization_larger_grid.mat');
rand_grid_large=randomization.ix;

monitorluminanceLookup = [0,64,128,192,255];
% 1.5s per value => 7.5s, in 30s => 5 repetitions
monitorluminance = repmat(1:length(monitorluminanceLookup),1,5);

%smooth pursuit
smooth_angle = 0:15:360 - 15;
smooth_speed = [16, 18, 20, 22, 24];


smooth_angle_sub = sort(repmat(smooth_angle,1,length(smooth_speed)));
smooth_speed_sub = repmat(smooth_speed,1,length(smooth_angle));

smooth_trials_per_block = length(smooth_angle_sub)/max_block;
%initialize fields
rand = struct();
for fn = {'smallBefore','smallAfter','large','pupildilation','smoothpursuit_speed','smoothpursuit_angle','block','subject','freeviewing','firstmovement'}
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
        
        % pupildilation
        while true
            % make sure no two following numbers are equal
            ix = randperm(length(monitorluminance));
            if all(diff(monitorluminance(ix))~=0)
                break
                
            end
        end
        rand.pupildilation = [rand.pupildilation {monitorluminanceLookup(monitorluminance(ix))}];
        
        
        % smooth pursuit
        smooth_ix(1) = (block-1) * smooth_trials_per_block + 1;
        smooth_ix(2) = (block) * smooth_trials_per_block;
        rand.smoothpursuit_speed = [rand.smoothpursuit_speed {smooth_speed_sub(smoothPerm(smooth_ix(1):smooth_ix(2)))}];
        rand.smoothpursuit_angle = [rand.smoothpursuit_angle  {smooth_angle_sub(smoothPerm(smooth_ix(1):smooth_ix(2)))}];
        
        free_ix(1) = (block-1)*3+1;
        free_ix(2) = (block)*3;
        rand.freeviewing = [rand.freeviewing {freeviewing(free_ix(1):free_ix(2))}];

        rand.block =    [rand.block block];
        rand.subject = [rand.subject subject];
        movements = {'ROTATE','TILT'};
        rand.firstmovement =[rand.firstmovement  movements(1+mod(subject+block,2))];
        
    end
    
end


save('data/stimuli_randomization', 'rand')