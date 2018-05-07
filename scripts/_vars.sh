#!/bin/sh
# Will require THIS_DIR be set from the calling script
set -eu
pushd `pwd` > /dev/null
cd $THIS_DIR

PROJECT_DIR=$(readlink -f ../codalab)
ROOT_DIR=$(readlink -f ..)

REQ_DIR=${REQ_DIR:-$PROJECT_DIR/requirements/}

VENV_DIR=$ROOT_DIR/venv
WHEEL_DIR=$ROOT_DIR/wheel_packages
PIP_BUILD_CMD="pip wheel --wheel-dir=$WHEEL_DIR"
PIP_INSTALL_CMD="pip install --use-wheel --no-deps"
popd > /dev/null
