#!/bin/bash
set -e

# Ensure PATH is set
export DOTNET_ROOT=$HOME/.dotnet
export PATH=$HOME/.dotnet:$HOME/.dotnet/tools:$PATH

# Install .NET 8 Runtime and SDK
echo "Installing .NET 8 Runtime and SDK..."
wget -q https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 8.0 --install-dir $HOME/.dotnet --runtime dotnet
./dotnet-install.sh --channel 8.0 --install-dir $HOME/.dotnet
rm dotnet-install.sh

# Verify .NET installation
if ! $HOME/.dotnet/dotnet --version &> /dev/null; then
    echo "[Error] .NET SDK installation failed."
    exit 1
fi
echo "[Main] .NET SDK and Runtime installation complete."

# Check if Roslynator is already installed
if $HOME/.dotnet/tools/roslynator --version &> /dev/null; then
    echo "[Main] Roslynator CLI already installed."
else
    echo "Installing Roslynator..."
    $HOME/.dotnet/dotnet tool install -g Roslynator.DotNet.Cli --no-cache --version 0.10.0
fi

# Verify Roslynator installation
if ! $HOME/.dotnet/tools/roslynator --version &> /dev/null; then
    echo "[Error] Roslynator CLI installation failed."
    exit 1
fi
echo "[Main] Roslynator CLI installation complete."

# Ensure PATH is exported for current session
export PATH=$HOME/.dotnet:$HOME/.dotnet/tools:$PATH

# Update shell profile to persist PATH
echo "export DOTNET_ROOT=$HOME/.dotnet" >> $HOME/.bashrc
echo "export PATH=\$PATH:\$HOME/.dotnet:\$HOME/.dotnet/tools" >> $HOME/.bashrc
