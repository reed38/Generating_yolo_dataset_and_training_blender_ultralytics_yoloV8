
#!/bin/bash

BLENDER_DOWNLOAD_LINK="https://download.blender.org/release/Blender3.6/blender-3.6.17-linux-x64.tar.xz"
CURRENT_DIR=$(pwd)
REQUIREMENT_FILE="$CURRENT_DIR/requirements.txt"
BLENDER_ARCHIVE="blender-3.6.17-linux-x64.tar.xz"
BLENDER_FOLDER="blender-3.6.17-linux-x64"
BLENDER_PYTHON_PATH="$CURRENT_DIR/$BLENDER_FOLDER/3.6/python/bin/python3.10"
BLENDER_BIN="$CURRENT_DIR/$BLENDER_FOLDER"


echo "Downloading Blender..."
wget $BLENDER_DOWNLOAD_LINK

echo "Extracting Blender..."
# Le point après -xf n'est pas nécessaire
tar -xf "$BLENDER_ARCHIVE"

echo "Installing python modules in blender..."
# Attendre que l'extraction soit terminée
sleep 2
$BLENDER_PYTHON_PATH -m pip install -r "$REQUIREMENT_FILE"

echo "Adding blender to PATH..."
# Correction de la syntaxe (un seul $)
echo "export PATH=\$PATH:$BLENDER_BIN" >> "$HOME/.bashrc"

# Recharger .bashrc
source "$HOME/.bashrc"

echo "Starting blender to test..."
"$BLENDER_BIN/blenderr"





echo "Installing ultralytics in a venv for yolo..."
# Check if Python3 is installed
command -v python3 >/dev/null 2>&1 || { echo "Python3 is required but not installed. Aborting." >&2; exit 1; }

# Check if venv exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
    source venv/bin/activate || { echo "Failed to activate virtual environment" >&2; exit 1; }
else
    echo "Creating new virtual environment..."
    python3 -m venv venv || { echo "Failed to create virtual environment" >&2; exit 1; }
    source venv/bin/activate || { echo "Failed to activate virtual environment" >&2; exit 1; }
fi

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install ultralytics
echo "Installing ultralytics..."
python3 -m pip install ultralytics || { echo "Failed to install ultralytics" >&2; exit 1; }

echo "Ultralytics installation completed successfully"



echo "oppenning blender..."
blender