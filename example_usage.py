#!/usr/bin/env python3
"""
Example usage of the Meow Package Manager API
Run this after starting the API server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_package():
    """Example: Create a new package"""
    package_data = {
        "name": "example-package",
        "owner": "john_doe",
        "version": "1.0.0",
        "giturl": "https://github.com/john_doe/example-package.git",
        "description": "An example package for demonstration",
        "license": "MIT",
        "dependencies": "python>=3.8,requests",
        "homepage": "https://example.com",
        "repository": "https://github.com/john_doe/example-package",
        "tags": "example,test,demo"
    }
    
    response = requests.post(f"{BASE_URL}/api/packages", json=package_data)
    print(f"Create package: {response.status_code}")
    if response.status_code == 201:
        print(json.dumps(response.json(), indent=2))
    return response.json() if response.status_code == 201 else None

def get_all_packages():
    """Example: Get all packages"""
    response = requests.get(f"{BASE_URL}/api/packages")
    print(f"\nGet all packages: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    return response.json() if response.status_code == 200 else None

def get_package_by_name(name):
    """Example: Get a specific package by name"""
    response = requests.get(f"{BASE_URL}/api/packages/{name}")
    print(f"\nGet package '{name}': {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    return response.json() if response.status_code == 200 else None

def update_package(name):
    """Example: Update a package"""
    update_data = {
        "version": "1.1.0",
        "description": "Updated description for the package"
    }
    response = requests.put(f"{BASE_URL}/api/packages/{name}", json=update_data)
    print(f"\nUpdate package '{name}': {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    return response.json() if response.status_code == 200 else None

def increment_download(name):
    """Example: Increment download count"""
    response = requests.post(f"{BASE_URL}/api/packages/{name}/download")
    print(f"\nIncrement download for '{name}': {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    print("Meow Package Manager API - Example Usage")
    print("=" * 50)
    
    # Make sure the server is running first!
    try:
        # Create a package
        package = create_package()
        
        if package:
            # Get all packages
            get_all_packages()
            
            # Get specific package
            get_package_by_name("example-package")
            
            # Update package
            update_package("example-package")
            
            # Increment download count
            increment_download("example-package")
            
            # Get updated package
            get_package_by_name("example-package")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Make sure the server is running:")
        print("  python MeowAPI/MeowAPI.py")
    except Exception as e:
        print(f"\nError: {e}")


