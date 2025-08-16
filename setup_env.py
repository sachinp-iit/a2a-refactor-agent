import subprocess
import importlib.util
import os

# --- List of Python packages to ensure ---
packages = ["sentence-transformers", "chromadb", "pandas", "pyyaml", "openai", "gitpython"]

for pkg in packages:
    if importlib.util.find_spec(pkg) is None:
        print(f"[Setup] Installing Python package: {pkg}")
        subprocess.run(["pip", "install", pkg], check=True)
    else:
        print(f"[Setup] Python package {pkg} already installed.")

# --- Make sure shell script is executable ---
script_path = "./install_dotnet_roslynator.sh"
os.chmod(script_path, 0o755)

# --- Run the existing shell script (it already checks internally) ---
subprocess.run(["bash", script_path], check=True)

print("[Setup] Environment setup complete!")
