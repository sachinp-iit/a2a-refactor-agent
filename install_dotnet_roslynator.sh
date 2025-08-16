#!/bin/bash
set -e

# Ensure PATH is set before checking
export DOTNET_ROOT=$HOME/.dotnet
export PATH=$PATH:$HOME/.dotnet:$HOME/.dotnet/tools

# Install .NET SDK only if not present
if ! command -v dotnet &> /dev/null; then
    echo "Installing .NET 8 SDK..."
    wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
    chmod +x dotnet-install.sh
    ./dotnet-install.sh --version 8.0.100
else
    echo ".NET SDK already installed."
fi

# Install Roslynator only if not present
if ! command -v roslynator &> /dev/null; then
    echo "Installing Roslynator..."
    ~/.dotnet/dotnet tool install -g Roslynator.DotNet.Cli
else
    echo "Roslynator already installed."
fi
