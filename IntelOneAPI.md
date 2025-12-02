### 1) Optional prereqs and offline installers

```
sudo apt install libdrm2 libgtk-3-0 libnotify4 xdg-utils libxcb-dri3-0 libgbm1 libatspi2.0-0

sudo apt update && sudo apt install -y \
    build-essential \
    gcc g++ gfortran \
    make cmake pkg-config \
    libncurses-dev \
    perl \
    wget \
    gpg-agent \
    lsb-release \
    libdrm2 libgtk-3-0t64 libnotify4 xdg-utils libxcb-dri3-0 libgbm1 libatspi2.0-0t64

#base and HPC toolkits, respectively
wget https://registrationcenter-download.intel.com/akdlm/IRC_NAS/9a98af19-1c68-46ce-9fdd-e249240c7c42/l_BaseKit_p_2024.2.0.634_offline.sh
wget https://registrationcenter-download.intel.com/akdlm/IRC_NAS/d4e49548-1492-45c9-b678-8268cb0f1b05/l_HPCKit_p_2024.2.0.635_offline.sh
```

make the scripts executable
```bash
chmod +x l_BaseKit_p_2024.2.0.634_offline.sh
chmod +x l_HPCKit_p_2024.2.0.635_offline.sh

./l_BaseKit_p_2024.2.0.634_offline.sh -a --cli --eula accept
```

follow the on screen prompts
start the virtual environment to utilize it
```
source ~/intel/oneapi/setvars.sh
```
only if we configured lmod, which we didnt
```
# Navigate to the location of your Intel oneAPI installation
cd ~/intel/oneapi/

# Execute the modulefiles setup script
./modulefiles-setup.sh

# Return to the top level of your $HOME directory and
# configure Lmod to make use of the newly created modules
# Alternatively, this line can be appended to /etc/profile or your .bashrc
ml use $HOME/modulefiles

# Make sure the newly created modules are available to use and have been correclty configured
ml avail
```



