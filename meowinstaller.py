import subprocess
import requests 
import json
import importlib.util
from builder import MeowBuilder
# --- API STUFF (BORING) --- #

MeowAPIClient = "/usr/local/lib/meow/MeowAPI/client.py"
spec = importlib.util.spec_from_file_location("MeowAPIclient", MeowAPIClient)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def handle_publish_command(name, version, giturl,owner, description=None):
    client = MeowAPIClient()
    data = {
        "name": name,
        "owner": owner,
        "version": version,
        "giturl": giturl,
        "description": description or ""
    }
    client._make_request("POST", "/api/packages", json=data)


def getpackageurl(pkgname: str):
    client = MeowAPIClient()
    # Send request to get all packages or a specific one by query param
    response = client._make_request("GET", f"/api/packages?name={pkgname}")
    if pkgname.startswith("https://") or  pkgname.startswith("http://"):
        return pkgname


    if not response or "packages" not in response:
        return None

    # Assuming response["packages"] is a list of package info dicts
    for pkg in response["packages"]:
        if pkg["name"] == pkgname:
            return pkg.get("source") or pkg.get("url")

    return "Error while trying to get package url: could not find package. please try again with the git url"


def installMeowpkg(pkgname:str,env=None, cwd=None):
    pkgurl = getpackageurl(pkgname)
    areyousureuwannainstallthisrn = input(f"Are you sure you want to install {pkgname} from {pkgurl}?         y/n:")             
    if areyousureuwannainstallthisrn.lower() in ["y","yes"]:    
        command= ["git","clone",pkgurl]
        result = subprocess.run(command, capture_output=False, text=True, env=env, cwd=cwd)
        if result.returncode == "0":
            print("Command executed successfully")
            print("Output:")
            print(result.stdout)
            areyousureuwannabuildthisrn = input(f"Are you sure you want to install {pkgname} from {pkgurl}?         y/n:")
            if areyousureuwannabuildthisrn.lower() in ["y","yes"]:
                MeowBuilder.start_build_process()                                                                        
    elif areyousureuwannainstallthisrn.lower() in ["n","no"]:
        return "userDeniedInstallation"
    else:
        print("You mispelled. \nTry again.")
