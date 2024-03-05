markdown
# Installation Guide

## Install Git LFS for Managing Large Files

### Windows
- Visit [Git LFS](https://git-lfs.github.com/) and follow the instructions for Windows installation.

### macOS
- Open Terminal and run:
```
brew install git-lfs
```

### Linux
- Open Terminal and run:
```
sudo apt update
sudo apt install git-lfs
```

## Bundle Installation

- To setup Git LFS, run:
```
git lfs install
```

- For the production bundle of the application, clone the repository:
```
git clone https://github.com/Genentech/spex_bundle.git .
```

- Set executable permissions (Ubuntu & macOS):
```
chmod -R +x .
```

## Install Docker desktop || OrbStack 
## on Your Local Machine 

### Ubuntu & macOS
- Execute the application demo script:
```
./app_demo.sh up
```

### Windows
- Run the PowerShell script:
```
./app_demo.ps1 up
```