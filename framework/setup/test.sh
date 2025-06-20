sudo apt update -y" "Updating package list..."
sudo apt install -y ifupdown pip curl aircrack-ng john dsniff tmux git" "Installing required tools..."

# Adding Submodules to safe.directory
git config --global --add safe.directory /home/kali/WifiForge/framework/mininet-wifi

# Initialize Submodules
git submodule init

# Update Submodules
git submodule update

sudo -E pip config set global.break-system-packages true

# Set global pip variable to break system packages
sudo -E pip install -r requirements.txt --break-system-packages

# Install Mininet
sudo apt install -y mininet --allow-downgrades

# Run Install Script
../mininet-wifi/util/install.sh -Wlnf

../mininet-wifi/util/install.sh -Wn
../mininet-wifi/util/install.sh -l
../mininet-wifi/util/install.sh -v
../mininet-wifi/util/install.sh -f

# Compile
sudo make install

sudo apt install openvswitch-testcontroller -y
sudo ln /usr/bin/ovs-testcontroller /usr/bin/controller
sudo service openvswitch-switch start
sudo cp ./main_menu /usr/bin
sudo chmod +x /usr/bin/main_menu 
