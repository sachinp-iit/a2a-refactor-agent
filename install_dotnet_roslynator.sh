#!/bin/bash
set -e

# Ensure PATH is set
export DOTNET_ROOT=$HOME/.dotnet
export PATH=$PATH:$HOME/.dotnet:$HOME/.dotnet/tools

# Install .NET 8 SDK if not present
if ! command -v dotnet &> /dev/null; then
    echo "Installing .NET 8 SDK..."
    wget -q https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
    chmod +x dotnet-install.sh
    ./dotnet-install.sh --channel 8.0 --install-dir $HOME/.dotnet
    rm dotnet-install.sh
fi

# Install Roslynator if not present
if ! command -v roslynator &> /dev/null; then
    echo "Installing Roslynator..."
    $HOME/.dotnet/dotnet tool install -g Roslynator.DotNet.Cli --version 0.8.4
fi

# Update current session PATH
export PATH=$HOME/.dotnet:$HOME/.dotnet/tools:$PATH

# Verify Roslynator installation
if command -v roslynator &> /dev/null; then
    echo "[Main] Roslynator CLI installation complete."
else
    echo "[Error] Roslynator CLI installation failed."
    exit 1
fi
