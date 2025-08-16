import subprocess
import os

# 1️⃣ Install Python dependencies (once)
subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

# 2️⃣ Make sure the shell script is executable
script_path = "./install_dotnet_roslynator.sh"
os.chmod(script_path, 0o755)

# 3️⃣ Run the existing shell script
subprocess.run(["bash", script_path], check=True)

print("[Setup] Environment setup complete!")
