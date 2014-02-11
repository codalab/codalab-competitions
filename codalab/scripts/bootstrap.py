import os
import argparse


argparser = argparse.ArgumentParser(
    description='Bootstrap for codalab project')
argparser.add_argument(
    '-v', '--venv', help='Virtual Environment Name', required=True)
args = argparser.parse_args()

VENV_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PATH = os.path.join(VENV_BASE_PATH, args.venv)

print VENV_BASE_PATH
print VENV_PATH
if os.getenv('VIRTUAL_ENV'):
    print("Virtual Environment already activated. Deactivate and restart")
    exit(1)

if not os.path.exists(VENV_PATH):
    print("%s does not exist" % VENV_PATH)
