function [slice] = select_randomization(rand,subject,block)
rand
% Example call:
% slice.(fn{1}) = rand.(fn{1}){select};
select = rand.block == block & rand.subject == subject;
if sum(select)~=1
    error('something went wrong, there should be 1 block, 1 subject only')
end
slice= struct();
for fn = fieldnames(rand)'
    if iscell(rand.(fn{1}))
        slice.(fn{1}) = rand.(fn{1}){select};
    else
        slice.(fn{1}) = rand.(fn{1})(select);
    end
end
end