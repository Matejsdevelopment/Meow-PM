import json
import subprocess
import os
from typing import List, Dict, Any, Optional


import os
import subprocess

def setexecutiondir():
    """Check and optionally change the current working directory for the package build"""
    print("Current working directory:", os.getcwd())
    confirmdirectory = input("Is that the directory of your package? (y/n): ").strip().lower()
    
    if confirmdirectory == "y":
        print("✅ Using current directory.")
    elif confirmdirectory == "n":
        new_dir = input("Enter the full path to your package directory: ").strip()
        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            os.chdir(new_dir)
            print(f"✅ Changed working directory to: {os.getcwd()}")
        else:
            print("❌ Invalid directory path. Staying in current directory.")
    else:
        print("⚠️ Invalid input. Staying in current directory.")

    # After setting directory, check for setup.py or build.py
    setup_exists = os.path.exists("setup.py")
    build_exists = os.path.exists("build.py")

    if setup_exists or build_exists:
        print("\n📦 Detected official build scripts:")
        if setup_exists:
            print("   - setup.py found")
        if build_exists:
            print("   - build.py found")

        method = input(
            "\nHow would you like to build?\n"
            "1. Manual (official setup.py / build.py)\n"
            "2. Automatic Meow Build (autobuild.py)\n"
            "Select 1 or 2: "
        ).strip()

        if method == "1":
            print("\n🛑 Manual mode selected.")
            print("Please run one of the following manually in your terminal:")
            if setup_exists:
                print("   python setup.py install")
            if build_exists:
                print("   python build.py")
            print("\nExiting without automatic build or dependency installation.")
            return "manual"
        
        elif method == "2":
            print("\n⚙️ Automatic Meow Build selected.")
            if os.path.exists("autobuild.py"):
                print("✅ autobuild.py found — launching automatic build.")
                subprocess.run(["python", "autobuild.py"])
                return "automatic"
            else:
                print("❌ autobuild.py not found. Cannot start automatic build.")
                return "missing_autobuild"
        else:
            print("⚠️ Invalid option. Canceling build process.")
            return "cancelled"

    else:
        print("\n⚠️ No setup.py or build.py detected.")
        print("Proceeding with automatic Meow dependency installation.")
        # Here you can later trigger your dependency installer if desired.
        return "no_manual_scripts"




class Color:
    """ANSI color codes for terminal output"""
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

import os

def setexecutiondir():
    """Check and optionally change the current working directory for the package build"""
    print("Current working directory:", os.getcwd())
    confirmdirectory = input("Is that the directory of your package? (y/n): ").strip().lower()
    
    if confirmdirectory == "y":
        print( f" {Color.GREEN}Using current directory.")
        return os.getcwd()
    elif confirmdirectory == "n":
        new_dir = input("Enter the full path to your package directory: ").strip()
        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            os.chdir(new_dir)
            print(f"{Color.GREEN} Changed working directory to: {os.getcwd()}")
            return os.getcwd()
        else:
            print(f"{Color.RED}Invalid directory path. Staying in current directory.")
            return os.getcwd()
    else:
        print(f"{Color.YELLOW}Invalid input. Staying in current directory.")
        return os.getcwd()



class MeowBuilder:
    """Builder for installing packages from requirements files"""

    def _print_warning(self, pkg_name: str, source: str):
        """Print a big warning message for failed installations"""
        warning_text = f"[WARNING]    COULD NOT INSTALL {pkg_name} FROM {source}"
        border = "=" * len(warning_text)
        print(f"\n{Color.YELLOW}{Color.BOLD}{border}")
        print(warning_text)
        print(f"{border}{Color.RESET}\n")

    def installfromgit(self, repo_url: str) -> bool:
        """Install package from git repository"""
        try:
            subprocess.run(["git", "clone", repo_url], check=True, capture_output=True)
            return True
        except Exception:
            pkg_name = repo_url.split('/')[-1].replace('.git', '')
            self._print_warning(pkg_name, "git")
            return False

    def installfrompacman(self, pkg_name: str) -> bool:
        """Install package from pacman"""
        try:
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", pkg_name], check=True, capture_output=True)
            return True
        except Exception:
            self._print_warning(pkg_name, "pacman")
            return False

    def installfrompip(self, pkg_name: str) -> bool:
        """Install package from pip"""
        try:
            subprocess.run(["pip", "install", pkg_name], check=True, capture_output=True)
            return True
        except Exception:
            self._print_warning(pkg_name, "pip")
            return False

    def installfromaur(self, pkg_name: str) -> bool:
        """Install package from AUR"""
        try:
            subprocess.run(["yay", "-S", "--noconfirm", pkg_name], check=True, capture_output=True)
            return True
        except Exception:
            self._print_warning(pkg_name, "aur")
            return False

    def check_requirements_exist(self, directory: str = ".") -> Optional[str]:
        """Check if requirements file exists in directory"""
        possible_files = [
            os.path.join(directory, "requirements.py"),
            os.path.join(directory, "requirements.json"),
            os.path.join(directory, "requirements.txt")
        ]
        for filepath in possible_files:
            if os.path.exists(filepath):
                return filepath
        return None

    def load_requirements_py(self, filepath: str) -> Dict[str, List[Any]]:
        """Load requirements from Python file"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("requirements", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        requirements = {}
        for attr in dir(module):
            if attr.startswith('installfrom'):
                requirements[attr] = getattr(module, attr)
        return requirements

    def load_requirements_json(self, filepath: str) -> Dict[str, List[Any]]:
        """Load requirements from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def load_requirements_txt(self, filepath: str) -> Dict[str, List[Any]]:
        """Load requirements from TXT file"""
        requirements = {}
        current_section = None
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    requirements[current_section] = []
                elif current_section:
                    requirements[current_section].append(line)
        return requirements

    def install_from_requirements(self, filepath: str):
        """Install all packages from a requirements file"""
        if filepath.endswith('.py'):
            requirements = self.load_requirements_py(filepath)
        elif filepath.endswith('.json'):
            requirements = self.load_requirements_json(filepath)
        elif filepath.endswith('.txt'):
            requirements = self.load_requirements_txt(filepath)
        else:
            print(f"{Color.RED}Error: Unsupported file format. Use .py, .json or .txt{Color.RESET}")
            return

        source_map = {
            "installfromgit": self.installfromgit,
            "installfrompacman": self.installfrompacman,
            "installfrompip": self.installfrompip,
            "installfromaur": self.installfromaur
        }

        for source_key, packages in requirements.items():
            if source_key in source_map:
                install_func = source_map[source_key]
                print(f"\n{Color.BOLD}{Color.GREEN}→ Installing from {source_key}:{Color.RESET}")
                for pkg in packages:
                    print(f"   Installing {pkg}...")
                    install_func(pkg)
            else:
                print(f"{Color.YELLOW}[!] Unknown install source: {source_key}{Color.RESET}")

    def start_build_process(self, directory: str = "."):
        """Start the full build/dependency installation process"""
        print(f"{Color.BOLD}{Color.GREEN}Starting build process...{Color.RESET}")
        req_file = self.check_requirements_exist(directory)
        
        if not req_file:
            print(f"{Color.RED}No requirements file found in {directory}.{Color.RESET}")
            return
        
        print(f"Found requirements file: {req_file}")
        self.install_from_requirements(req_file)
        print(f"\n{Color.GREEN}Done installing dependancies!{Color.RESET}")
    


if __name__ == "__main__":
    mode = setexecutiondir()
    if mode == "no_manual_scripts":
        builder = MeowBuilder()
        builder.start_build_process()
