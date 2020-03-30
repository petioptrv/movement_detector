#!/bin/bash

DIR="$(dirname "$0")"
cd $DIR

(source ./env/bin/activate; python3 main.py) || (printf "\nNo environment detected.\nInstalling...\n\n"; python3 -m venv ./env; source ./env/bin/activate; pip install -e ".[interface]"; printf "\nInstallation complete. Please run script again.\n\n")

deactivate
exit