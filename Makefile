

installfolder = local
VENV = ${installfolder}/etcompvenv

#export VIRTUAL_ENV := $(abspath ${VENV})
#export PATH := ${VIRTUAL_ENV}/bin:${PATH}


install: git-reqs ${VENV} python-reqs compile-dependencies
		echo 'installation done, whew.. you should be very happy that this worked ;)'

git-reqs:
			git submodule update --init

${VENV}:
	virtualenv -p python3 --system-site-packages ${VENV}
	#python3 -m venv --system-site-packages ${VENV}#


python-reqs: ${VENV}
	( \
	. ${VENV}/bin/activate; \
	pip3 install --upgrade -r requirements.pip;\
	pip3 install git+https://github.com/pupil-labs/pyglui;\
	)


compile-dependencies: pyav edfread opencv glfw printexport
		echo 'done'

printexport:
		echo 'use this command before starting python/spyder'
		echo 'export LD_LIBRARY_PATH=${CURDIR}/${ffmpegbuild}/lib/:${CURDIR}/${glfwbuild}/lib/:$$LD_LIBRARY_PATH'

glfwsrc = ${installfolder}/build/src_glfw
glfwbuild = ${installfolder}/build/build_glfw
glfw: ${glfwsrc} ${glfwbuild}
		echo 'done'

${glfwsrc}:
		git clone https://github.com/glfw/glfw ${glfwsrc}

${glfwbuild}:
		mkdir ${glfwsrc}/build
		cd ${glfwsrc}/build && \
		cmake -DCMAKE_INSTALL_PREFIX='../../build_glfw' -DBUILD_SHARED_LIBS=ON ../ &&\
		make -j && \
		make install


pyavsrc = ${installfolder}/build/src_pyav

${pyavsrc}:
		git clone https://github.com/pupil-labs/PyAV ${pyavsrc}

pyav: ${VENV} ${pyavsrc} ffmpeg
		cd ${pyavsrc} && \
		git checkout setup.py && \
		sed -e "s/'avformat_open_input'/'avformat_open_input'/g" setup.py --> test.py && \
		export PKG_CONFIG_PATH=:${CURDIR}/${ffmpegbuild}/lib/pkgconfig:${PKG_CONFIG_PATH} && \
		python3 setup.py install

edfread: ${VENV} lib/pyedfread/include/ lib/pyedfread/lib/
		git submodule update --init
		cp /net/store/nbp/projects/lib/edfread/build/linux64/libedfapi.so lib/pyedfread/lib/libedfapi.so
		cp /net/store/nbp/projects/lib/edfread/include64/* lib/pyedfread/include/
		cd lib/pyedfread && \
		python setup.py install

lib/pyedfread/include/:
		mkdir lib/pyedfread/include/

lib/pyedfread/lib/:
		mkdir lib/pyedfread/lib/

opencvsrc = ${installfolder}/build/src_opencv
opencvbuild = ${installfolder}/build/build_opencv
${opencvsrc}:
			git clone https://github.com/itseez/opencv ${opencvsrc}

opencv: ${opencvsrc}
		mkdir ${opencvbuild}
		mkdir ${opencvsrc}/build
	  cd ${opencvsrc}/build && \
	  cmake -D CMAKE_BUILD_TYPE=RELEASE -D BUILD_TBB=ON -D WITH_TBB=ON -D WITH_CUDA=OFF -D BUILD_opencv_python2=OFF -DBUILD_opencv_python3=ON  -D CMAKE_INSTALL_PREFIX='../../build_opencv' ../ && \
	  make -j4 && \
	  make install
		# now add opencv to python
		ln -s ${opencvbuild}/lib/python3.5/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so ${VENV}/lib/python3.5/site-packages/cv2.cpython-35m-x86_64-linux-gnu.so

cleanopencv:
		rm -r ${opencvbuild}
		rm -r ${opencvsrc}/build

ffmpegsrc = ${installfolder}/build/src_ffmpeg
ffmpegbuild = ${installfolder}/build/build_ffmpeg

yasmsrc =  ${installfolder}/build/src_yasm/
yasmbuild = ${installfolder}/build/build_yasm/

${ffmpegsrc}:
		wget http://launchpad.net/ubuntu/+archive/primary/+files/ffmpeg_3.3.4.orig.tar.xz &&\
		mkdir ${ffmpegsrc}
		tar -xf ffmpeg_3.3.4.orig.tar.xz ffmpeg-3.3.4
		mv ffmpeg-3.3.4/* ${ffmpegsrc}
		rm -r ffmpeg-3.3.4
		rm ffmpeg_3.3.4.orig.tar.xz

ffmpeg: ${ffmpegbuild}
		echo 'installed ffmpeg'

${ffmpegbuild}: ${yasmbuild} ${ffmpegsrc}
		export PATH=${PATH}:${CURDIR}/${yasmbuild}/bin && \
		cd ${ffmpegsrc} && \
		./configure --prefix='../build_ffmpeg' --enable-shared --enable-pic --cc="gcc -m64 -fPIC" --extra-cflags="-fPIC" && \
		make -j4 && \
		make install

cleanffmpeg:
		rm -r ${ffmpegsrc}
		rm -r ${ffmpegbuild}

${yasmsrc}:
		git clone https://github.com/yasm/yasm ${yasmsrc}

yasm: ${yasmbuild}
	echo 'installed yasm'

${yasmbuild}: ${yasmsrc}
		cd ${yasmsrc} && \
		./autogen.sh && \
		./configure --prefix=${CURDIR}/${yasmbuild} && \
		make yasm && \
		make install

cleanyasm:
		rm -r ${yasmsrc}
		rm -r ${installfolder}/build/build_yasm

path: compile-dependencies python-reqs ${VENV}
		export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${ffmpegbuild}
