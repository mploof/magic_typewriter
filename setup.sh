#!/bin/bash

# Create a virtual environment and install the required packages
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install mpv media player and set the path in the config.yaml file
sudo apt update
sudo apt install -y yq
sudo apt install -y mpv
yq eval ".mpv_path = \"$(which mpv)\"" -i config.yaml

echo "Setup complete. Run 'source .venv/bin/activate' to activate the virtual environment."
