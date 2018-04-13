# How to start the compiled binary of pupil player / capture locally under ubuntu:

- Get the linux release zip file from https://github.com/pupil-labs/pupil/releases
- unzip the .deb files from it
- run ```dpkg -x pupil_capture_linux_os_x64_v1.6.13.deb /folder/to/be/extracted/to```
- Optional: Copy the file to a more useful directory e.g. ```/net/store/nbp/users/yourRZname```
- go to the folder ```cd /folder/to/be/extracted/to``` and run ```./pupil_player```

# Git
```
git clone https://github.com/behinger/etcomp
git submodule init --update
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
