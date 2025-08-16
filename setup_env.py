import subprocess
import os
import sys
import pkg_resources

def install_requirements_if_needed(requirements_file='requirements.txt'):
    # Read the requirements file
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    # Check which packages are missing
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg in requirements if pkg.lower().split('==')[0] not in installed_packages]

    # Install only if there are missing packages
    if missing_packages:
        print(f"Installing missing packages: {missing_packages}")
        subprocess.check_call(['pip', 'install', '-r', requirements_file])
    else:
        print("All packages already installed. No need to call requirements.txt.")

def run_shell_script(script_path):
    """Make shell script executable and run it"""
    if not os.path.exists(script_path):
        print(f"[Error] Shell script {script_path} not found!")
        sys.exit(1)
    os.chmod(script_path, 0o755)
    print(f"[Setup] Running shell script: {script_path}...")
    try:
        result = subprocess.run(["bash", script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"[Setup] Shell script {script_path} completed!")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Shell script execution failed: {e.stderr}")
        sys.exit(1)

def main():
    install_requirements_if_needed()
    run_shell_script("./install_dotnet_roslynator.sh")

    dotnet_root = os.path.expanduser("~/.dotnet")
    dotnet_tools = os.path.join(dotnet_root, "tools")
    os.environ["DOTNET_ROOT"] = dotnet_root
    os.environ["PATH"] = f"{dotnet_root}{os.pathsep}{dotnet_tools}{os.pathsep}{os.environ.get('PATH', '')}"

    # Force PATH update in current Python session
    os.putenv("PATH", os.environ["PATH"])

    # Verify .NET installation
    from shutil import which
    if which("dotnet") is None:
        print("[Error] .NET SDK not found in PATH after installation!")
        sys.exit(1)
    else:
        print("[Setup] .NET SDK is ready!")

    # Verify Roslynator installation
    if which("roslynator") is None:
        print("[Error] Roslynator not found in PATH after installation!")
        sys.exit(1)
    else:
        print("[Setup] Roslynator is ready!")

    print("[Setup] Environment setup complete!")

if __name__ == "__main__":
    main()
