[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2553447.svg)](https://doi.org/10.5281/zenodo.2553447)

# Eye Tracking Comparison

This project procides:
  - **Visual Test Battery**  with 9 different Eye Tracking Tasks (Matlab/PsychophysicsToolbox-3)
  - **Preprocessing Pipeline** for **Pupil Labs glasses** & **EyeLink 1000**. Modular for other eye trackers (Python)
  - **Analysis Scripts** for **Ehinger, Groß et al 2019** (Python)
  - **Makefile** for all requirements, including **Pupil Labs Software WITHOUT root/sudo** necessity (see below for restrictions)
  - Pupil Labs **Eye Videos** + World Video of **15 subjects** + **concurrent EyeLink** data [at figshare](https://doi.org/10.6084/m9.figshare.c.4379810.v1)
  
# Instructions
Get the project GIT and initialize the submodules

```
git clone https://github.com/behinger/etcomp
git submodule update --init
```

This Makefile generates a virtualenv, downloads all required python modules, installs all requisits for Pupil Labs. This includes opencv, it my take quite a while!
```
make
```

## Visual Test Battery
#### Acuity TEST
[We used this acuity test](http://www.openoptometry.com/Alpha/v4_0/OTC.html#lineSize=1.8&lineUnits=cm&distance=1&distanceUnits=meters&chartType=2&optoType=0&displayType=1&rowIndex=14&mirror=false&animate=false&crowd=false&nearFar=near&col1=#dedede&col2=#f10708&col3=#20e4fa&col4=#000000&mode3d=0). 
Be sure to setup monitor size correctly!
#### Run Experiment
The experiment can be run by ./experiment/ETcomp.m

Ubuntu: The experiment communicates with Pupil Labs using ZMQ. To get this to work, you have to load a library before running matlab:
```
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab
```

## Python Preprocessing Pipeline

**Update 2021-12-10**: You could also check out [this fork](https://github.com/teresa-canasbajo/bdd-driveratt/tree/master/eye_tracking/preprocessing) for a (potentially) cleaned up version. Haven't checked or tried it personally - citation would still be appreciated :-)

You can run a subject using the preprocessing pipeline (from the folder "code").
We took some care to make it modular, but the pipeline should be more thought as a starting base and needs modification for your own setup.
```
import functions.et_preprocess
from functions.detect_events import make_blinks,make_saccades,make_fixations
data = preprocess_et(et='pl', datapath='/net/store/nbp/projects/etcomp/sub-1/raw', eventfunctions=(make_blinks,make_saccades,make_fixations))
```
- The datapath should be a pupil labs folder (if et='pl'), or a folder with an eyelink-EDF file (if et='el')
- The eventfunctions are modular, here we use the default ones implemented by us, but you could simply replace them with other functions. The eventfunctions are executed sequentially.
- We are using loggers for messages, try to use the "debug" flag if you want more information!

## Python Analysis Pipeline
Our analyses (and all results included in the paper) can be found in the notebook: code/main.ipynb

Further analyses can be found in the capital notebooks eg. SMOOTH.ipynb, GRID.ipynb. 
Functions for each tasks are in SMOOTH.py, or GRID.py


## Makefile

We made great efforts to not need root rights but still be able to use pupil labs from source. The GUI is non-functional. pyAV somehow is a newer version and we need to fix some things in pupillabs (forked version is linked)

You need these packages definitely installed  using sudo/ root (there might be more):
```
automake
cmake
pkgconfig
python3-dev
libglew-dev <-- this one is usually not installed
xorg-dev libglu1-mesa-dev <-- needed for libglew
```
(In principle you can also try to compile glew, but I could not manage properly.)

### Add Paths
After installation run 
``` make export-paths```

and everytime before running Spyder or Python, you need to run these to add some dependencies for Python to use.

You can put these in your `~./bashrc` so that everytime you run a terminal, you will also have the paths automatically (highly recommend)

### EDFread


Pyedfread also needs a dependencie from SR-research (libedfapi.so), which is not publicly available. Checkout the Sr research forum!

-------------------------------------------------------------

# Old instructions
These instructions here are notes on how to instlal different versions of Pupil Labs glasses.

# How to start the compiled binary of pupil player / capture locally under ubuntu:

- Get the linux release zip file from https://github.com/pupil-labs/pupil/releases
- unzip the .deb files from it
- run ```dpkg -x pupil_capture_linux_os_x64_v1.6.13.deb /folder/to/be/extracted/to```
- Optional: Copy the file to a more useful directory e.g. ```/net/store/nbp/users/yourRZname```
- go to the folder ```cd /folder/to/be/extracted/to``` and run ```./pupil_player```



## What follows now is old installation instruction, they were merged to make install
## Python EDFREAD


- go to ```lib/pyedfread```
- make new folder: ```lib```
- copy ```/net/store/nbp/projects/lib/edfread/build/linux64/libedfapi.so``` to ```lib/libedfapi.so```
- make new folder ```include```
- copy ```/net/store/nbp/projects/lib/edfread/*.h``` to ```lib/include/*.h```
- activate your virtualenv
- run ```python setup.py install```


## install opencv
- compile opencv3 as pupil-labs
```
  git clone https://github.com/itseez/opencv
  cd opencv
  mkdir build &&  cd build
  cmake -D CMAKE_BUILD_TYPE=RELEASE -D BUILD_TBB=ON -D WITH_TBB=ON -D WITH_CUDA=OFF -D BUILD_opencv_python2=OFF -DBUILD_opencv_python3=ON  -D CMAKE_INSTALL_PREFIX='XXX/opencv-build'
  make -j4
  make install
  
  ```
## isntalling pyav under linux
This one was difficult
- get ffmpeg3 (only v.2 is installed by defaul)
- I used https://launchpad.net/ubuntu/+archive/primary/+files/ffmpeg_3.3.4.orig.tar.xz
- Unzip it
- you likely need yasm, but its straight forward to build
    - `git clone https://github.com/yasm/yasm`
    - `cd yasm`
    - `sh autoconfig.sh`
    - `./configure --prefix=../yasm-build` # or cmake?
    - `make yasm`
    - `make install`
    - `export PATH=$PATH:/net/store/nbp/users/behinger/tmp/pupil_src_test/yasm-build/bin`
    - should be done, I did not have trouble here at all

- run `./configure --prefix=../ffmpeg-build --enable-shared --enable-pic --cc="gcc -m64 -fPIC"  --extra-cflags="-fPIC"
`  (the enabled shared is key, else we later get errors compiling av)
- run `make` and then `make install`
- add the newly build ffmpeg libraries to the pkg-config path: `export PKG_CONFIG_PATH=:folder/to/install/ffmpeg/:$PKG_CONFIG_PATH` 
- in your python3 venv, run "pip install av'
- you always have to add `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/net/store/nbp/users/behinger/tmp/pupil_src_test/ffmpeg-build/lib/` before import av (you should else get an error `ImportError: libavfilter.so.6: cannot open shared object file: No such file or directory`)
- I often ran into the problem `avformat_open_input` while installing pip av. Not sure what solved this. I cloned the pyav-git, and removed both instances of avformat_open_input (just commented them out). Compiled then successfully, put them back in, and compiled again - now it worked... strange
- start python and type `import av` - if it works, I'm happy for you... took me 2.5h 
