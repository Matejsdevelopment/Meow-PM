import re
import requests
from parser import create_parser
from meowinstaller import installMeowpkg
import subprocess
import os
import json
 

def search_flathub(pkgname, pkgid=None):
    try:
        print(f"Searching for '{pkgname}' on Flathub 🔍")
        url = "https://flathub.org/api/v2/search"
        payload = {"query": pkgname, "filters": []}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code != 200:
            print("Failed to fetch data from Flathub API. Status:", response.status_code)
            print("Response text:", response.text)
            return []

        data = response.json()
        results = data.get("hits", [])
        if not results:
            print("No results found.")
            return []

        print(f"\nFound {len(results)} results:\n")

        for app in results:
            name = app.get("name", "Unknown")
            app_id = app.get("app_id", "Unknown ID")  
            summary = app.get("summary", "")
            print(f"{name} ({app_id})")
            if summary:
                print(f"  ↳ {summary}")
            print()

        
        return [app.get("app_id") for app in results if app.get("app_id")]

    except requests.RequestException as e:
        print("Network error:", e)
        return []
    except Exception as e:
        print("Unexpected error:", e)
        return []
#that was painful...

def check_pkg_version(pkgname: str, pkgmanager: str):
    try:
        if pkgmanager == "aur":
            command = subprocess.run(['yay', '-Qi', pkgname], capture_output=True, text=True)
            if command.returncode == 0:
                return extract_version(command.stdout)
            return "unknown"
        elif pkgmanager == "pac":
            command = subprocess.run(['pacman', '-Qi', pkgname], capture_output=True, text=True)
            if command.returncode == 0:
                return extract_version(command.stdout)
            return "unknown"
        elif pkgmanager == "flathub":
            pkgid = get_first_flathub_id(pkgname)
            if not pkgid:
                return "unknown"
            result = subprocess.run(['flatpak', 'info', pkgid], capture_output=True, text=True)
            if result.returncode == 0:
                return extract_version(result.stdout)
            return "unknown"
        else:
            return f"Unknown package manager: {pkgmanager}"
    except Exception as e:
        print(f"Error checking version: {e}")
        return "unknown"

def extract_version(output):
    match = re.search(r'Version\s*:\s*(.+)', output)
    return match.group(1) if match else "Version not found"




def create_package_info(pkgname, version, packagemanager, ID=None, deleted: bool = False):
    """
    FIX THIS
    - pkgname (str): The name of the package.
    - version (str): The version of the package.
    - packagemanager (str): The package manager used.
    - ID (str, optional): The ID of the package. Defaults to None.
    - Deleted (bool): Is the package deleted?
    """
    package_info = {
        "pkgname": pkgname,
        "version": version,
        "source": packagemanager
    }
    if ID is not None:
        package_info["ID"] = ID
    if deleted is not False:
        package_info["deleted"] = deleted

    try:
        with open("info.json", 'w') as json_file:
            json.dump(package_info, json_file, indent=4)
    except Exception as e:
        print(f"Error creating package info: {e}")

def edit_package_info(**updates):
    """
    Update existing fields in info.json.
    Example:
        edit_package_info(version="2.0", deleted=True)
    """
    path = "info.json"
    if not os.path.exists(path):
        print("info.json not found.")
        return

    try:
        with open(path, "r") as f:
            data = json.load(f)

        data.update({k: v for k, v in updates.items() if v is not None})

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        print("info updated successfully.")

    except Exception as e:
        print(f" Failed to edit info.json: {e}")


def parse_search_results(output):
    return output.splitlines()


def search_pacman(pkgname):
    try:
        print(f"Searching for '{pkgname}' in Pacman repositories 🔍\n")
        result = subprocess.run(
            ['pacman', '-Ss', pkgname],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            print("No results found.")
            return
        
        lines = result.stdout.strip().split('\n')
        count = 0
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith(' '):
                i += 1
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                pkg_info = parts[0]
                version = parts[1] if len(parts) > 1 else ""
                
                description = ""
                if i + 1 < len(lines) and lines[i + 1].startswith(' '):
                    description = lines[i + 1].strip()
                    i += 1
                
                print(f"{pkg_info} {version}")
                if description:
                    print(f"  ↳ {description}")
                print()
                count += 1
            i += 1
        
        if count == 0:
            print("No results found.")
        else:
            print(f"Found {count} result(s)")
            
    except FileNotFoundError:
        print("Error: pacman command not found")
    except Exception as e:
        print(f"Error searching Pacman: {e}")


def search_aur(pkgname):
    try:
        print(f"Searching for '{pkgname}' in AUR 🔍\n")
        result = subprocess.run(
            ['yay', '-Ss', pkgname],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            print("No results found.")
            return
        
        lines = result.stdout.strip().split('\n')
        count = 0
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith(' '):
                i += 1
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                pkg_info = parts[0]
                version = parts[1] if len(parts) > 1 else ""
                
                description = ""
                if i + 1 < len(lines) and lines[i + 1].startswith(' '):
                    description = lines[i + 1].strip()
                    i += 1
                
                print(f"{pkg_info} {version}")
                if description:
                    print(f"  ↳ {description}")
                print()
                count += 1
            i += 1
        
        if count == 0:
            print("No results found.")
        else:
            print(f"Found {count} result(s)")
            
    except FileNotFoundError:
        print("Error: yay command not found. Install yay to search AUR.")
    except Exception as e:
        print(f"Error searching AUR: {e}")


def search_packages(pkgname):
    print(f"\n{'='*60}")
    print(f"Searching for '{pkgname}' across all sources")
    print(f"{'='*60}\n")
    
    print(f"{'-'*60}")
    print("FLATHUB RESULTS")
    print(f"{'-'*60}")
    search_flathub(pkgname)
    
    print(f"\n{'-'*60}")
    print("PACMAN RESULTS")
    print(f"{'-'*60}")
    search_pacman(pkgname)
    
    print(f"\n{'-'*60}")
    print("AUR RESULTS (via yay)")
    print(f"{'-'*60}")
    search_aur(pkgname)
    
    print(f"\n{'='*60}\n")


def exists_in_pacman(pkg):
    try:
        output = subprocess.run(
            ['pacman', '-Ss', pkg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return bool(output.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def exists_in_yay(pkg):
    try:
        output = subprocess.run(
            ['yay', '-Ss', pkg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )  # ADD UPDATE SUPPORT
        return bool(output.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def exists_in_flathub(pkg):
    url = f"https://flathub.org/api/v1/apps/search/{pkg}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return False

        data = resp.json()
        for app in data:
            app_id = app.get('flatpakAppId', '').lower()
            app_name = app.get('name', '').lower()
            if pkg.lower() == app_id or pkg.lower() == app_name or pkg.lower() in app_id or pkg.lower() in app_name:
                return True
        return False
    except Exception:
        return False

def choose_source(source, pkgname):
    if source in ["flathub", "fb", "fk", "flatpak"]:
        install_packagefh(pkgname)
    elif source in ["pacman", "pac"]:
        install_packagepacman(pkgname)
    elif source == "aur":
        install_packageaur(pkgname)
    elif source == "meow":
        installMeowpkg(pkgname)
    elif source==None:
        choosesourcewithuser(pkgname)
    else:
        print(f"Unknown source: {source}")

def choosesourcewithuser(pkg):
    source = int(input("which source do you want to use\nflatpak:1 pacman:2 aur:3 meow:4                     "))
    if source == 1:
        install_packagefh(pkg)
    elif source == 2:
        install_packagepacman(pkg)
    elif source == 3:
        install_packageaur(pkg)
    elif source == 4:
        installMeowpkg(pkg)


def choose_source_search(source, pkgname):
    parser = create_parser()
    args = parser.parse_args()
    if args.source in ["flathub", "fb", "fk", "flatpak"]:
        return "flathub"
    elif args.source in ["pacman", "pac"]:
        return "pacman"
    elif args.source == "aur":
        return "aur"



def install_packageaur(pkgname, env=None, cwd=None):
    areyousureuwannainstallthisrn = input(f"Are you sure you want to install {pkgname}? y/n: ")
    if areyousureuwannainstallthisrn.lower() in ["y", "yes"]:   
        try:
            command = ["yay", "-S", "--nocleanmenu", "--nodiffmenu", pkgname]
            result = subprocess.run(command, capture_output=False, text=True, env=env, cwd=cwd)
            if result.returncode == 0:
                version = check_pkg_version(pkgname, pkgmanager="aur")
                create_package_info(pkgname, version, "aur")
                print("Command executed successfully")
            else:
                print("Command failed")
        except Exception as e:
            print(f"An error occurred: {e}")
    elif areyousureuwannainstallthisrn.lower() in ["no", "nah", "n"]:
        return "userDeniedInstallation"
    else:
        print("You mispelled. \nTry again.")

def install_packagepacman(pkgname, env=None, cwd=None):
    areyousureuwannainstallthisrn = input(f"Are you sure you want to install {pkgname}? y/n: ")
    if areyousureuwannainstallthisrn.lower() in ["y", "yes"]:    
        try:
            command = ["sudo", "pacman", "-S", pkgname]
            result = subprocess.run(command, capture_output=False, text=True, env=env, cwd=cwd)
            if result.returncode == 0:
                version = check_pkg_version(pkgname, pkgmanager="pac")
                create_package_info(pkgname, version, "pac")
                print("Command executed successfully")
            else:
                print("Command failed")
        except Exception as e:
            print(f"An error occurred: {e}")
    elif areyousureuwannainstallthisrn.lower() in ["no", "nah", "n"]:
        return "userDeniedInstallation"
    else:
        print("You mispelled. \nTry again.")

def get_first_flathub_id(pkgname):
    try:
        r = requests.post("https://flathub.org/api/v2/search",
                          json={"query": pkgname, "filters": []},
                          headers={"Content-Type": "application/json"},
                          timeout=10)
        if r.status_code != 200:
            return None
        data = r.json().get("hits", [])
        if not data or len(data) == 0:
            return None
        return data[0].get("app_id")
    except Exception as e:
        print(f"Error fetching Flathub ID: {e}")
        return None

def install_packagefh(pkgname, env=None, cwd=None):
    pkgid = get_first_flathub_id(pkgname)
    if not pkgid:
        print(f"Could not find Flathub ID for {pkgname}. Aborting install.")
        return
    
    areyousureuwannainstallthisrn = input(f"Are you sure you want to install {pkgid}? y/n: ")
    if areyousureuwannainstallthisrn.lower() in ["y", "yes"]:   
        try:
            subprocess.run(["flatpak", "remote-add", "--if-not-exists", "flathub", "https://flathub.org/repo/flathub.flatpakrepo"])
            command = ["flatpak", "install", "--user", "flathub", "--noninteractive", "--assumeyes", pkgid]
            result = subprocess.run(command, capture_output=False, text=True, env=env, cwd=cwd)
            if result.returncode == 0:
                version = check_pkg_version(pkgname, pkgmanager="flathub")
                create_package_info(pkgname, version, "flathub", ID=pkgid)
                print("Command executed successfully")
            else:
                print("Command failed")
        except Exception as e:
            print(f"An error occurred: {e}")
    elif areyousureuwannainstallthisrn.lower() in ["no", "nah", "n"]:
        return "userDeniedInstallation"
    else:
        print("You mispelled. \nTry again.")



def choose_update_source(pkgname: str, source: str | None = None, limit: bool = False):
    choices = ['pac', 'pacman', 'flathub', 'fb', 'fk', 'flatpak', 'aur', 'meow']

    if source in choices:
        if source in ["flathub", "fb", "fk", "flatpak"]:
            update_packagefh(pkgname)
        elif source in ["pacman", "pac"]:
            update_packagepacman(pkgname)
        elif source == "aur":
            update_packageaur(pkgname)
        else:
            print(f"Unknown source: {source}")

    elif not limit:
        choose_update_source(pkgname, get_source(pkgname), True)

    else:
        print(f"Uknown source {source} for {pkgname}.")

        



def update_packagepacman(pkgname, env=None, cwd=None):
    areyousureuwannainstallthisrn = input(f"Are you sure you want to update {pkgname}? y/n: ")
    if areyousureuwannainstallthisrn.lower() in ["y", "yes"]:   
        try:
            command = ["sudo", "pacman", "-S", pkgname]
            result = subprocess.run(command, capture_output=False, text=True, env=env, cwd=cwd)
            if result.returncode == 0:
                version = check_pkg_version(pkgname, pkgmanager="pac")
                create_package_info(pkgname, version, "pac")
                print("Command executed successfully")
            else:
                print("Command failed")
        except Exception as e:
            print(f"An error occurred: {e}")
    elif areyousureuwannainstallthisrn.lower() in ["no", "nah", "n"]:
        return "userDeniedInstallation"
    else:
        print("You mispelled. \nTry again.")

def update_packageaur(pkgname, env=None, cwd=None):
    areyousureuwannainstallthisrn = input(f"Are you sure you want to update {pkgname}? y/n: ")
    if areyousureuwannainstallthisrn.lower() in ["y", "yes"]:   
        try:
            command = ["yay", "-U", "--nocleanmenu", "--nodiffmenu", pkgname]
            result = subprocess.run(command, capture_output=False, text=True, env=env, cwd=cwd)
            if result.returncode == 0:
                version = check_pkg_version(pkgname, pkgmanager="aur")
                create_package_info(pkgname, version, "aur")
                print("Command executed successfully")
            else:
                print("Command failed")
        except Exception as e:
            print(f"An error occurred: {e}")
    elif areyousureuwannainstallthisrn.lower() in ["no", "nah", "n"]:
        return "userDeniedInstallation"
    else:
        print("You mispelled. \nTry again.")

def update_packagefh(pkgname, env=None, cwd=None):
    pkgid = get_first_flathub_id(pkgname)
    if not pkgid:
        print(f"[ERROR] Could not find Flathub ID for {pkgname}. Aborting update.")
        return

    areyousure = input(f"Are you sure you want to update {pkgid}? y/n: ")
    if areyousure.lower() in ["y", "yes"]:
        try:
            subprocess.run([
                "flatpak", "remote-add", "--if-not-exists",
                "flathub", "https://flathub.org/repo/flathub.flatpakrepo"
            ])
            command = ["flatpak", "update", "--user", "--noninteractive", pkgid]
            subprocess.run(command, check=True, env=env, cwd=cwd)

            version = check_pkg_version(pkgname, pkgmanager="flathub")
            create_package_info(pkgname, version, "flathub", ID=pkgid)
            print(f"{pkgname} updated successfully!")

        except subprocess.CalledProcessError:
            print("Flatpak update command failed.")
        except Exception as e:
            print(f"An error occurred: {e}")

    elif areyousure.lower() in ["n", "no", "nah"]:
        print("Update canceled by user.")
    else:
        print("You mispelled. Try again.")








def get_source(pkgname):
    if isinstance(pkgname, list):
        if pkgname:
            pkgname = pkgname[0]
        else:
            return None

    if not isinstance(pkgname, str):
        print(f"[WARN] Invalid pkgname type: {type(pkgname)}")
        return None

    if not os.path.exists("info.json"):
        print("[WARN] info.json not found")
        return None

    try:
        with open("info.json", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("[WARN] info.json corrupted")
        return None

    if isinstance(data, list):
        for pkg in data:
            if (
                pkgname.lower() == pkg.get("pkgname", "").lower()
                or pkgname.lower() == pkg.get("ID", "").lower()
                or pkgname.lower() in pkg.get("ID", "").lower()
            ):
                print(f"[DEBUG] Matched {pkg.get('pkgname')} → source={pkg.get('source')}")
                return pkg.get("source")

    elif isinstance(data, dict):
        if pkgname.lower() == data.get("pkgname", "").lower():
            return data.get("source")

    print(f"[WARN] Package '{pkgname}' not found in info.json.")
    return None





#FIX UPDATE SUPPORT!!!
#ADD PyPi and C/Cpp pm support