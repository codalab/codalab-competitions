# !/bin/bash
wget -c https://github.com/JohnLangford/vowpal_wabbit/archive/v7.3.zip || exit 1
unzip v7.3.zip && cd vowpal_wabbit-7.3 && ./autogen.sh | ./configure | make || exit 1

# add compile function as bundle
