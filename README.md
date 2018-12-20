# Visual Test Battery
If you want to use the visual test battery, we recommend to use the scripts in the folder "experiment". The scripts in "experiment_ehinger2019" are for reproducability reasons. We updated several small things e.g. more consistent trigger messages and the likes which still need to be fixed in the analysis!

# How to use etcomp

We made great efforts to not need root rights but still be able to use pupil labs from source. The GUI is non-functional. pyAV somehow is a newer version and we need to fix some things in pupillabs (forked version is linked)
```
git clone https://github.com/behinger/etcomp
git submodule update --init
make
```
Should do all the magic for you.

You need these packages definitely installed  using sudo/ root (there might be more):
```
automake
cmake
pkgconfig
python3-dev
libglew-dev <-- this one is usually not installed
xorg-dev libglu1-mesa-dev <-- needed for libglew
```



# Old instructions
### ACUITY TEST
http://www.openoptometry.com/Alpha/v4_0/OTC.html#lineSize=1.8&lineUnits=cm&distance=1&distanceUnits=meters&chartType=2&optoType=0&displayType=1&rowIndex=14&mirror=false&animate=false&crowd=false&nearFar=near&col1=#dedede&col2=#f10708&col3=#20e4fa&col4=#000000&mode3d=0

# How to start the compiled binary of pupil player / capture locally under ubuntu:

- Get the linux release zip file from https://github.com/pupil-labs/pupil/releases
- unzip the .deb files from it
- run ```dpkg -x pupil_capture_linux_os_x64_v1.6.13.deb /folder/to/be/extracted/to```
- Optional: Copy the file to a more useful directory e.g. ```/net/store/nbp/users/yourRZname```
- go to the folder ```cd /folder/to/be/extracted/to``` and run ```./pupil_player```

# Git
```
git clone https://github.com/behinger/etcomp
git submodule update --init
```
The latter is necessary to get the files from pupillabs, which we partially will make use of.

# Change pupil labs code
- We need to comment out the 4 lines in references_surface init related to fonts (at least on Ubuntu)
- With our pyav we need to update ``` mode='time'``` to ```whence='time'```. This is in the file ```video_capture/file_backend.py``` twice
# NEW INSTALLATION

We have a large list of dependencies. Easiest is to install using:

``` make install ```

Then run 
``` make export-paths```

and everytime before running spider or python, you need to run these to add some dependencies for python to use.

You can put these in your `~./bashrc` so that everytime you run a terminal, you will also have the paths automatically (highly recommend)


You need these packages definitely installed (there might be more):
```
automake
cmake
pkgconfig
python3-dev
libglew-dev <-- this one is usually not installed
xorg-dev libglu1-mesa-dev <-- needed for libglew
```

In principle you can also try to compile glew, but I could not manage properly.

Pyedfread also needs a dependencie from SR-research (libedfapi.so), which is not publicly available. Checkout the Sr research forum!



# What follows now is old installation instruction, they were merged to make install
# Python EDFREAD


- go to ```lib/pyedfread```
- make new folder: ```lib```
- copy ```/net/store/nbp/projects/lib/edfread/build/linux64/libedfapi.so``` to ```lib/libedfapi.so```
- make new folder ```include```
- copy ```/net/store/nbp/projects/lib/edfread/*.h``` to ```lib/include/*.h```
- activate your virtualenv
- run ```python setup.py install```


# pip packages
so far, probably missed a few

```
Cython==0.25.2
h5py==2.7.1
ipython==6.3.1
msgpack-python==0.4.8
numpy==1.13.3
pandas==0.20.3
pyedfread==0.1
scipy==0.19.1
spyder==3.2.8
```
# install opencv
- compile opencv3 as pupil-labs
```
  git clone https://github.com/itseez/opencv
  cd opencv
  mkdir build &&  cd build
  cmake -D CMAKE_BUILD_TYPE=RELEASE -D BUILD_TBB=ON -D WITH_TBB=ON -D WITH_CUDA=OFF -D BUILD_opencv_python2=OFF -DBUILD_opencv_python3=ON  -D CMAKE_INSTALL_PREFIX='XXX/opencv-build'
  make -j4
  make install
  
  ```
# isntalling pyav under linux
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
