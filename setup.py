import os
import sys
import json
import subprocess
from pathlib import Path


def check_python_version():
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required to run this application.")
        sys.exit(1)


def create_venv(venv_dir: Path) -> bool:
    if not venv_dir.exists():
        print("🔧 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            print(f"✅ Virtual environment created at {venv_dir.resolve()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("ℹ️ Virtual environment already exists")
        return True


def install_setuptools(python_path: Path):
    print("🧩 Ensuring setuptools (for distutils compatibility)...")
    try:
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "setuptools"], check=True, text=True)
        print("✅ setuptools installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install setuptools: {e}")
        sys.exit(1)


def install_requirements(pip_path: Path, requirements_file: Path = Path("requirements.txt")):
    print("📦 Installing dependencies from requirements.txt...")
    if not requirements_file.exists():
        print(f"❌ Missing {requirements_file}")
        sys.exit(1)
    try:
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True, text=True)
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)


def check_gradio_version(python_path: Path):
    print("🔍 Checking Gradio version...")
    try:
        result = subprocess.run(
            [str(python_path), "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        gradio_pkg = next((pkg for pkg in packages if pkg["name"].lower() == "gradio"), None)
        if gradio_pkg:
            current = gradio_pkg["version"]
            print(f"📦 Gradio version installed: {current}")
            if current < "4.0.0":
                print("⚠️ A newer version of Gradio is available.")
                upgrade = input("Would you like to upgrade to the latest Gradio version? [Y/n]: ").strip().lower()
                if upgrade in ["", "y", "yes"]:
                    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "gradio"], check=True)
                    print("✅ Gradio upgraded successfully.")
        else:
            print("⚠️ Gradio not found in environment.")
    except Exception as e:
        print(f"⚠️ Could not check Gradio version: {e}")


def create_config(config_path: Path):
    if not config_path.exists():
        print("\n🛠 Creating configuration file...")
        key = input("Enter your D-ID API key (press Enter to skip): ").strip()
        if not key:
            print("⚠️ No API key entered. You can configure it later in api_config.json or through the app.")

        config = {
            "key": key,
            "url": "https://api.d-id.com"
        }
        config_path.write_text(json.dumps(config, indent=2))
        print(f"✅ Configuration file created at: {config_path}")
    else:
        print("ℹ️ Configuration file already exists")


def print_activation_instructions(venv_dir: Path):
    print("\n🎉 Setup complete! To use the application:")
    if os.name == 'nt':
        print(f"1. Activate the virtual environment:\n   .\\{venv_dir}\\Scripts\\activate")
    else:
        print(f"1. Activate the virtual environment:\n   source {venv_dir}/bin/activate")
    print("2. Run the app:\n   python app.py")


def run_app(python_path: Path):
    try:
        subprocess.run([str(python_path), "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application closed by user.")


if __name__ == "__main__":
    print("\033[96m🔧 Setting up D-ID Studio Pro...\033[0m")
    check_python_version()

    venv_dir = Path("venv")
    if create_venv(venv_dir):
        pip_path = venv_dir / ("Scripts" if os.name == "nt" else "bin") / "pip"
        python_path = venv_dir / ("Scripts" if os.name == "nt" else "bin") / "python"

        install_setuptools(python_path)
        install_requirements(pip_path)
        check_gradio_version(python_path)

        config_path = Path.cwd() / 'api_config.json'
        create_config(config_path)

        print_activation_instructions(venv_dir)

        run_now = input("\n🚀 Would you like to run the application now? [y/N]: ").strip().lower()
        if run_now == 'y':
            run_app(python_path)
