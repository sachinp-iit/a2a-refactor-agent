#!/bin/bash
set -e

# Install .NET dependencies if needed
apt-get update -qq
apt-get install -y apt-transport-https ca-certificates wget

# Add Microsoft repository
echo "Adding Microsoft repository..."
wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Install .NET SDK 8.0
apt-get update -qq
apt-get install -y dotnet-sdk-8.0

# Verify .NET installation
if ! command -v dotnet &> /dev/null; then
    echo "[Error] .NET SDK installation failed."
    exit 1
fi
echo "[Main] .NET SDK installation complete."

# Install Roslynator if not present
if ! command -v roslynator &> /dev/null; then
    echo "Installing Roslynator..."
    dotnet tool install -g Roslynator.DotNet.Cli
fi

# Verify Roslynator installation
if command -v roslynator &> /dev/null; then
    echo "[Main] Roslynator CLI installation complete."
else
    echo "[Error] Roslynator CLI installation failed."
    exit 1
fi

# Update PATH for tools (global tools are in ~/.dotnet/tools)
export PATH=$PATH:$HOME/.dotnet/tools
