#!/bin/bash

DIR="$(dirname "$0")"
cd $DIR

source ./env/bin/activate || (python3 -m venv ./env; source ./env/bin/activate; pip install -e ".[interface]")

python3 main.py

deactivate
exit