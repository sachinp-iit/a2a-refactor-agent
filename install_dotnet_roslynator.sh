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
if ! command -v dotnet &> /dev/null; then
    echo "[Error] .NET SDK installation failed."
    exit 1
fi
echo "[Main] .NET SDK and Runtime installation complete."

# Ensure .NET runtime is accessible
if ! $HOME/.dotnet/dotnet --version &> /dev/null; then
    echo "[Error] .NET runtime not accessible."
    exit 1
fi

# Check if Roslynator is already installed
if command -v roslynator &> /dev/null; then
    echo "[Main] Roslynator CLI already installed."
else
    echo "Installing Roslynator..."
    $HOME/.dotnet/dotnet tool install -g Roslynator.DotNet.Cli --no-cache
fi

# Verify Roslynator installation
if command -v roslynator &> /dev/null; then
    echo "[Main] Roslynator CLI installation complete."
else
    echo "[Error] Roslynator CLI installation failed."
    exit 1
fi

# Ensure PATH is exported for current session
export PATH=$HOME/.dotnet:$HOME/.dotnet/tools:$PATH
