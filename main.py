#!/usr/bin/env python3
import subprocess
import requests
import platform
import argparse
import re
from pathlib import Path
from datetime import datetime

# === Color Function ===
def color(text, c):
    codes = {"green": 32, "red": 31, "yellow": 33}
    return f"\033[{codes.get(c, 0)}m{text}\033[0m"

# === Run Shell Command ===
def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

# === Run with live output ===
def run_live(cmd):
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            print(color(line.rstrip(), "green"))
        proc.wait()
        return proc.returncode == 0
    except FileNotFoundError:
        print(color(f"command not found: {cmd[0]}", "red"))
        return False

# === Logger ===
def log_action(action):
    log_dir = Path("~/.cache/meow").expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "meow.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs = []
    if log_file.exists():
        logs = log_file.read_text().splitlines()
    logs.append(f"[{timestamp}] {action}")
    logs = logs[-50:]
    log_file.write_text("\n".join(logs))

# === Parse and pretty-print Pacman info output ===
def print_pacman_info(output):
    fields_of_interest = [
        "Name", "Version", "Description", "Architecture",
        "URL", "Licenses", "Groups", "Provides",
        "Depends On", "Optional Deps", "Conflicts With",
        "Replaces", "Download Size", "Installed Size",
        "Packager", "Build Date", "Validated By"
    ]

    lines = output.splitlines()
    info = {}
    current_field = None

    for line in lines:
        if not line.strip():
            continue

        m = re.match(r'^([A-Za-z ]+?)\s*:\s*(.*)$', line)
        if m:
            current_field = m.group(1).strip()
            value = m.group(2).strip()
            if current_field in fields_of_interest:
                info[current_field] = value
        else:
            if current_field and current_field in fields_of_interest:
                info[current_field] += " " + line.strip()

    for field in fields_of_interest:
        if field in info:
            print(color(f"{field}: ", "green") + f"{info[field]}")

# === Package Existence Checks ===
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

# === Check Package Command ===
def check_package(args):
    pkg = args.pkg
    pacman_found = exists_in_pacman(pkg)
    yay_found = exists_in_yay(pkg)
    flathub_found = exists_in_flathub(pkg)

    sources = []
    if yay_found:
        sources.append("Yay")
    if flathub_found:
        sources.append("Flathub")
    if pacman_found:
        sources.append("Pacman")

    if sources:
        print(color(f"[✓] Package '{pkg}' is available on {', '.join(sources)}.", "green"))
    else:
        print(color(f"[✗] Package '{pkg}' is not available on Yay, Flathub, or Pacman.", "red"))

    log_action(f"check {pkg}")




from parser import create_parser
from installer import choose_source, search_packages, choose_update_source


def fetch_system_info():
    try:
        info = {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
        for key, value in info.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.command == 'install':
        if args.src!= None:
            choose_source(args.src, args.package)
        else:
            choose_source(None,args.package)
    elif args.command == 'search':
        search_packages(args.query)

    elif args.command == 'fetch':
        fetch_system_info()

    elif args.command == "update":
        choose_update_source(args.package, args.src)
    
    elif args.command == "check":
        check_package(args)
    
    else:
        parser.print_help()
