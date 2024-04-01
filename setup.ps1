# Create a virtual environment and install the required packages
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Install Chocolatey (if not already installed) and yq (YAML processor) using Chocolatey
choco install yq

# Install mpv media player (using Chocolatey) and set the path in the config.yaml file
# Ensure Chocolatey is installed before running this script
choco install mpv

# Assuming yq is available in the Windows environment, otherwise, it needs to be installed manually.
# Setting the mpv_path in the config.yaml file. Adjust the mpv path according to your installation.
$mpvPath = (Get-Command mpv).Source
yq eval ".mpv_path = `"$mpvPath`"" -i config.yaml

Write-Host "Setup complete. Run '.venv\Scripts\Activate.ps1' to activate the virtual environment."
