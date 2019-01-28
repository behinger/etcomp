function imgdata=resizeImg(imgdata,const)
% resize image without distortions

%% resize image
[iy, ix, id] = size(imgdata);
wW = diff(const.coor([1 3]));
wH = diff(const.coor([2 4]));
if ix > wW
    x0 = 1;
    dx = ix / wW;
else
    x0 = 1;
    dx = 1;
end
if iy>wH
    y0 = 1;
    dy = iy / wH;
else
    y0 = 1;
    dy = 1;
end

dx = max(dx,dy);  % otherwise the image gets distorted
dy = dx; 		  % otherwise the image gets distorted

% imdata is the subsampled version of the image.
imgdata = imgdata(round(y0:dy:iy), round(x0:dx:ix),:);