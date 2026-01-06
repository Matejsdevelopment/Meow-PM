import subprocess

confirmifuv = input("do you have the UV package manager for pip installed?  y/n")

def installpackages(confirmifuv):
    if confirmifuv.lower in ["y"]:
        dependancies = ["typing", "argparse", "json"]
        command = ["uv", "pip","install", dependancies]
        subprocess.run(command)
    else:
        print("userdeniedinput")
        return "userdeniedinput"
    
from setuptools import setup, find_packages

setup(
    name="meowpm",
    version="0.1.0",
    packages=find_packages(exclude=["MeowAPI"]),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "meow=main:cli_entrypoint"
        ]
    },
)
