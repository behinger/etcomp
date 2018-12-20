function [dots]= gridCoordinates(screen_width, screen_height,surface_marker_size, num_dots) 
percent=0.9;
markersize = 1.48 * surface_marker_size;
markersize = 3 * surface_marker_size;


lost_x= markersize/screen_width;
lost_y= markersize /screen_height;

%lost = 90/screen_width: % markersize out
%pixel of spot in middle of screen
mid_x=screen_width/2;
mid_y=screen_height/2;

%get the smaller of both screen dimensions and use this because then the
%distance between the marker and the screen border is the same on the x and
%the y axis (otherwise 95% of the pixels on the longer exis are more then
%95% on the smaller axis and therefor the marker will be closer to one
%border than the other)
smaller=min(screen_width,screen_height);


%half of the dot_size in pixels
%(minimum size proportional to manual marker calibration is 90 pixels ->
%halfsize=45
halfsize=20;
screen_width_right=screen_width-screen_width*lost_x;
screen_width_left=screen_width*lost_x;
screen_height_down=screen_height-screen_height*lost_y;
screen_height_up=screen_height*lost_y;
%per row and column we show as many dots as the square of the whole dot
%number
dots_per_row=sqrt(49);

%calculate the coordinates of the dots on the x- and y-axis (equidistant)
x_coord=round(linspace(screen_width_left+halfsize,screen_width_right-halfsize,dots_per_row));
% x_coord=x_coord(2:end-1);
y_coord=round(linspace(screen_height_up+halfsize,screen_height_down-halfsize,dots_per_row));
% y_coord=y_coord(2:end-1);
[p,q] = meshgrid(x_coord, y_coord);
dots = [p(:) q(:)];
    
if num_dots == 49

   dots = dots; 
elseif num_dots == 13
    dots= dots([1,4,7,17,19,22,25,28,31,33,43,46,49],:);
end
% 
%     %pixels between outer spots and screen border
%     out_x=screen_width*lost_x+halfsize;
%     out_y=screen_height*lost_y+halfsize;
% 
%     %pixel between inner spots and screen border
%     in_x=out_x+((mid_x-out_x)/2);
%     in_y=out_y+((mid_y-out_y)/2);
%     dots=[];
%     % spot at middle of the screen in pixels for x_axis
%     dots(1,1)=mid_x;
%     % spot at middle of the screen in pixels for y_axis
%     dots(1,2)=mid_y;
%     %spot in upperleft corner
%     dots(2,1)=out_x;
%     dots(2,2)=out_y;
%     %left side middle
%     dots(3,1)=out_x;
%     dots(3,2)=mid_y;
%     %lower left corner
%     dots(4,1)=out_x;
%     dots(4,2)=screen_height-out_y;
%     %upper right corner
%     dots(5,1)=screen_width-out_x;
%     dots(5,2)=out_y;
%     %right side middle
%     dots(6,1)=screen_width-out_x;
%     dots(6,2)=mid_y;
%     %lower right corner
%     dots(7,1)=screen_width-out_x;
%     dots(7,2)=screen_height-out_y;
%     %inner upper left
%     dots(8,1)=in_x;
%     dots(8,2)=in_y;
%     %inner lower left
%     dots(9,1)=in_x;
%     dots(9,2)=screen_height-in_y;
%     %inner upper right
%     dots(10,1)=screen_width-in_x;
%     dots(10,2)=in_y;
%     %inner lower right
%     dots(11,1)=screen_width-in_x;
%     dots(11,2)=screen_height-in_y;
%     %upper middle
%     dots(12,1)=mid_x;
%     dots(12,2)=out_y;
%     %lower middle
%     dots(13,1)=mid_x;
%     dots(13,2)=screen_height-out_y;
end