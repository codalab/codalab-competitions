#!/bin/bash
THIS_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd `pwd`
cd $THIS_DIR
source ../config/generated/startup_env.sh
python ./users.py
python ./competitions.py
popd

