function [const]=getID
% get subject ID

const.vpnr = str2num(input('Wie lautet die Versuchspersonen-Nummer? ','s'));
const.code = sprintf('SpStMob_%.2d',const.vpnr);
if isempty(const.vpnr)
    const.vpnr = 00;
    const.code = sprintf('SpStMob_%.2d',const.vpnr);
end
