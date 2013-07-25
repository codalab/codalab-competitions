wget -c http://sourceforge.net/projects/weka/files/weka-3-7/3.7.9/weka-3-7-9.zip || exit 1
unzip weka-3-7-9.zip weka-3-7-9/weka-src.jar weka-3-7-9/weka.jar || exit 1
make || exit 1
