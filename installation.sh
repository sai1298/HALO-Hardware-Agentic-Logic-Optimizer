#!/bin/bash
set -e  # Exit immediately if a command fails

BASE_DIR="/content/HLS"
BAMBU_DIR="$BASE_DIR/bamboo"
MACHSUITE_DIR="$BASE_DIR/MachSuite"

echo "Initializing HLS setup pipeline..."

# -----------------------------
# Clean and prepare directories
# -----------------------------
echo "Preparing directories..."

if [ -d "$BAMBU_DIR" ]; then
    rm -rf "$BAMBU_DIR"
fi

if [ -d "$MACHSUITE_DIR" ]; then
    rm -rf "$MACHSUITE_DIR"
fi

mkdir -p "$BAMBU_DIR"

echo "Directories prepared at $BASE_DIR."

# -----------------------------
# Install Bambu HLS
# -----------------------------
echo "Starting Bambu installation..."
cd "$BAMBU_DIR"

echo "Adding Git PPA..."
echo "deb http://ppa.launchpad.net/git-core/ppa/ubuntu $(grep UBUNTU_CODENAME /etc/os-release | sed 's/.*=//g') main" > /etc/apt/sources.list.d/git-core.list

apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A1715D88E1DF1F24

echo "Updating packages..."
apt-get update

echo "Installing dependencies..."
apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    gcc-multilib \
    g++-multilib \
    git \
    libtinfo5 \
    verilator \
    wget

echo "Downloading Bambu..."
wget https://release.bambuhls.eu/appimage/bambu-latest.AppImage

chmod +x bambu-*.AppImage

echo "Creating symlinks..."
ln -sf "$PWD"/bambu-*.AppImage /bin/bambu
ln -sf "$PWD"/bambu-*.AppImage /bin/panda_shell
ln -sf "$PWD"/bambu-*.AppImage /bin/spider

echo "Cloning PandA-bambu repo..."
git clone --depth 1 --filter=blob:none --branch dev/panda --sparse https://github.com/ferrandi/PandA-bambu.git

cd PandA-bambu
git sparse-checkout set documentation/bambu101

echo "Moving documentation..."
cd "$BAMBU_DIR"
mv PandA-bambu/documentation/bambu101/* .

echo "Bambu installation completed."

# -----------------------------
# Clone MachSuite
# -----------------------------
echo "Cloning MachSuite..."
cd "$BASE_DIR"

if [ ! -d "$MACHSUITE_DIR" ]; then
    git clone https://github.com/breagen/MachSuite.git
    echo "MachSuite cloned successfully."
else
    echo "MachSuite directory already exists. Skipping clone."
fi

echo "Full setup pipeline finished successfully."
echo "Installing Python dependencies..."

pip install langchain langgraph
pip install -U langchain-google-genai langchain-core