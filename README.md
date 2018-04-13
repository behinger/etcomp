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
