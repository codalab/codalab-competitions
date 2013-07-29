#!/usr/bin/env bash
 
script_dir="$( cd "$( dirname "$0" )" && pwd )"
venv=${VENV:-"venv"}
 
default_requirements="$script_dir/codalab/requirements/dev.txt"
 
python=$(which ${PYTHON:-python2.7})
if [ ! -f $python ]; then
        echo "Could not locate python interpreter: $python"
        exit 1
fi
 
# Check we're using python3
python_ver=$($python -c 'import sys; print(sys.version_info[:])')
echo "Python version: $python_ver"
 
$python -c 'import sys; sys.exit(0) if sys.version_info[0] == 2 else sys.exit(1)'
is_python2=$?
if [ ! $is_python2 -eq 0 ]; then
        echo "ERROR: Python 2 is required!"
        exit $is_python2
fi
 
venv_dir="$script_dir/$venv"
 
if [ "$1" == "clean" ]; then
        if [[ -e $venv_dir ]];then
                echo "Removing existing test venv: $venv_dir"
                rm -rf "$venv_dir"
        fi
fi
 
if [ ! -f "$venv_dir/bin/python" ]; then
        echo "Creating VirtualEnv in: $venv_dir"
        virtualenv --clear --distribute $venv_dir
fi
 
venv_pip="$venv_dir/bin/pip"
requirements_file=${REQUIREMENTS:-$default_requirements}
codalab_requirements_file=${CODALAB_REQUIREMENTS:-"$script_dir/codalab/requirements/dev.txt"}
 
if [ -f $venv_pip ]; then
        echo "Installing development requirements from: $requirements_file"
        echo "The following requirements will be installed:"
        cat "$requirements_file"
        $venv_pip install -v -M -r "$requirements_file"
        pip_res=$?
        if [ ! $pip_res -eq 0 ]; then
                echo "ERROR: Failed to install requirements: $requirements_file"
                exit $pip_res
        fi
else
        echo "ERROR: Could not locate pip in virtualenv: $venv_pip"
        exit 1
fi

venv_python="$venv_dir/bin/python"

if [ -f $venv_python ]; then
	echo "Running syncdb for Django"
	python codalab/manage.py syncdb

	echo "Running data migrations"
	python codalab/manage.py migrate
else
	echo "ERROR: Could not locate python in virtualenv: $venv_python"
	exit 1
fi

echo "You should now run:"
echo "  > source $venv_dir/bin/activate"
echo "  > python codalab/manage.py runserver 0.0.0.0:8000"
