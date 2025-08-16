import subprocess
import os
import sys

def install_requirements():
    """Install all Python packages from requirements.txt"""
    if not os.path.exists("requirements.txt"):
        print("[Error] requirements.txt not found!")
        sys.exit(1)
    print("[Setup] Installing Python packages from requirements.txt...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("[Setup] Python packages installation complete!")

def run_shell_script(script_path):
    """Make shell script executable and run it"""
    if not os.path.exists(script_path):
        print(f"[Error] Shell script {script_path} not found!")
        sys.exit(1)
    os.chmod(script_path, 0o755)
    print(f"[Setup] Running shell script: {script_path}...")
    subprocess.run(["bash", script_path], check=True)
    print(f"[Setup] Shell script {script_path} completed!")

def main():
    install_requirements()
    run_shell_script("./install_dotnet_roslynator.sh")
    print("[Setup] Environment setup complete!")

if __name__ == "__main__":
    main()
