export LD_LIBRARY_PATH=/net/store/nbp/projects/IntoTheWild/ET_Analysis/etcomp/local/build/build_ffmpeg/lib/:/net/store/nbp/projects/IntoTheWild/ET_Analysis/etcomp/local/build/build_glfw/lib/:/local/build/build_ceres/lib:/net/store/nbp/projects/IntoTheWild/ET_Analysis/etcomp/local/build/build_opencv/lib:$LD_LIBRARY_PATH

source local/etcompvenv/bin/activate &&\
jupyter lab 

