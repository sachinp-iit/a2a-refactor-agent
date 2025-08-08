#!/bin/bash
set -e

# Install .NET 8 SDK
echo "Installing .NET 8 SDK..."
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --version 8.0.100

# Install Roslynator CLI
echo "Installing Roslynator..."
~/.dotnet/dotnet tool install -g Roslynator.DotNet.Cli

# Update PATH
export DOTNET_ROOT=$HOME/.dotnet
export PATH=$PATH:$HOME/.dotnet:$HOME/.dotnet/tools

# Verify installations
echo "Verifying installations..."
dotnet --version
roslynator --version
