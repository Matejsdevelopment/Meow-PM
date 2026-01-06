#!/usr/bin/env python3
"""
Meow Package Manager - Client-Side API Client
Handles all client-side interactions with the Meow package server API.
"""

import requests
import json
import os
import subprocess
import sys
from typing import Optional, List, Dict, Any
from urllib.parse import quote

class MeowAPIClient:
    """Client for interacting with the Meow Package Manager API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the Meow API server
            api_key: Admin API key for protected endpoints (optional, set via MEOW_ADMIN_API_KEY env var)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("MEOW_ADMIN_API_KEY", None)
        if self.api_key:
            self.session.headers.update({'X-API-Key': self.api_key})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to Meow API server at {self.base_url}")
            print("Make sure the server is running.")
            return None
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"Error: {response.json().get('detail', 'Not found')}")
            else:
                print(f"Error: {e}")
                if response.content:
                    try:
                        error_detail = response.json().get('detail', str(e))
                        print(f"Details: {error_detail}")
                    except:
                        print(f"Response: {response.text}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    # ============================================================================
    # CLIENT-SIDE FUNCTIONS (Search, Find, etc.)
    # ============================================================================
    
    def search_packages(self, query: str, limit: int = 50, verified_only: bool = False) -> List[Dict[str, Any]]:
        """
        Search for packages by name, description, tags, or owner
        This is a CLIENT-SIDE function that filters packages locally
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            verified_only: Only return verified packages
            
        Returns:
            List of matching packages
        """
        # Get all packages from server
        all_packages = self.get_all_packages(limit=1000, verified_only=verified_only)
        if not all_packages:
            return []
        
        query_lower = query.lower()
        results = []
        
        for package in all_packages:
            # Search in name, description, owner, tags
            if (query_lower in package.get('name', '').lower() or
                query_lower in package.get('description', '').lower() or
                query_lower in package.get('owner', '').lower() or
                query_lower in package.get('tags', '').lower()):
                results.append(package)
                if len(results) >= limit:
                    break
        
        return results
    
    def find_package(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a specific package by exact name match
        
        Args:
            name: Package name to find
            
        Returns:
            Package information or None if not found
        """
        return self._make_request('GET', f"/api/packages/{name}")
    
    def get_all_packages(self, skip: int = 0, limit: int = 100, active_only: bool = True, verified_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all packages from the server
        
        Args:
            skip: Number of packages to skip (for pagination)
            limit: Maximum number of packages to return
            active_only: Only return active packages
            verified_only: Only return verified packages
            
        Returns:
            List of packages
        """
        params = {
            'skip': skip,
            'limit': limit,
            'active_only': active_only,
            'verified_only': verified_only
        }
        result = self._make_request('GET', "/api/packages", params=params)
        return result if result else []
    
    def get_package_by_id(self, package_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a package by its ID
        
        Args:
            package_id: Package ID
            
        Returns:
            Package information or None if not found
        """
        return self._make_request('GET', f"/api/packages/id/{package_id}")
    
    # ============================================================================
    # PACKAGE INSTALLATION FUNCTIONS
    # ============================================================================
    
    def install_package(self, package_name: str, install_dir: str = "./packages") -> bool:
        """
        Install a package by downloading it from its git URL
        
        Args:
            package_name: Name of the package to install
            install_dir: Directory where packages should be installed
            
        Returns:
            True if installation was successful, False otherwise
        """
        # Get package information
        package = self.find_package(package_name)
        if not package:
            print(f"Package '{package_name}' not found in Meow registry.")
            return False
        
        giturl = package.get('giturl')
        if not giturl:
            print(f"Package '{package_name}' does not have a git URL.")
            return False
        
        # Create install directory if it doesn't exist
        os.makedirs(install_dir, exist_ok=True)
        package_install_path = os.path.join(install_dir, package_name)
        
        # Check if package is already installed
        if os.path.exists(package_install_path):
            print(f"Package '{package_name}' is already installed at {package_install_path}")
            response = input("Do you want to reinstall? (y/n): ")
            if response.lower() != 'y':
                return False
            # Remove existing installation
            import shutil
            shutil.rmtree(package_install_path)
        
        print(f"Installing '{package_name}' from {giturl}...")
        print(f"Version: {package.get('version')}")
        print(f"Owner: {package.get('owner')}")
        
        # Clone the repository
        try:
            result = subprocess.run(
                ['git', 'clone', giturl, package_install_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Successfully installed '{package_name}' to {package_install_path}")
            
            # Increment download count on server
            self.increment_download_count(package_name)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing package: {e.stderr}")
            return False
        except FileNotFoundError:
            print("Error: 'git' command not found. Please install Git.")
            return False
    
    def update_package(self, package_name: str, install_dir: str = "./packages") -> bool:
        """
        Update an installed package by pulling latest changes from git
        
        Args:
            package_name: Name of the package to update
            install_dir: Directory where packages are installed
            
        Returns:
            True if update was successful, False otherwise
        """
        package_install_path = os.path.join(install_dir, package_name)
        
        if not os.path.exists(package_install_path):
            print(f"Package '{package_name}' is not installed.")
            return False
        
        # Check if it's a git repository
        if not os.path.exists(os.path.join(package_install_path, '.git')):
            print(f"'{package_install_path}' is not a git repository. Reinstalling...")
            return self.install_package(package_name, install_dir)
        
        print(f"Updating '{package_name}'...")
        
        try:
            # Pull latest changes
            result = subprocess.run(
                ['git', 'pull'],
                cwd=package_install_path,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Successfully updated '{package_name}'")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error updating package: {e.stderr}")
            return False
    
    def increment_download_count(self, package_name: str) -> bool:
        """Increment download count for a package on the server"""
        result = self._make_request('POST', f"/api/packages/{package_name}/download")
        return result is not None
    
    # ============================================================================
    # PACKAGE INFORMATION FUNCTIONS
    # ============================================================================
    
    def get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a package
        
        Args:
            package_name: Name of the package
            
        Returns:
            Package information dictionary
        """
        return self.find_package(package_name)
    
    def print_package_info(self, package_name: str):
        """Print formatted package information"""
        package = self.get_package_info(package_name)
        if not package:
            return
        
        verified_badge = "✓ VERIFIED" if package.get('verified') else "⚠ UNVERIFIED"
        
        print(f"\n{'='*60}")
        print(f"Package: {package.get('name')} [{verified_badge}]")
        print(f"{'='*60}")
        print(f"Owner:        {package.get('owner')}")
        print(f"Version:      {package.get('version')}")
        print(f"Git URL:      {package.get('giturl')}")
        if package.get('description'):
            print(f"Description:  {package.get('description')}")
        if package.get('license'):
            print(f"License:      {package.get('license')}")
        if package.get('dependencies'):
            print(f"Dependencies: {package.get('dependencies')}")
        if package.get('homepage'):
            print(f"Homepage:     {package.get('homepage')}")
        if package.get('repository'):
            print(f"Repository:   {package.get('repository')}")
        if package.get('tags'):
            print(f"Tags:         {package.get('tags')}")
        print(f"Downloads:    {package.get('download_count', 0)}")
        print(f"{'='*60}\n")
    
    def list_packages(self, limit: int = 50, verified_only: bool = False):
        """List all available packages"""
        packages = self.get_all_packages(limit=limit, verified_only=verified_only)
        if not packages:
            print("No packages found.")
            return
        
        print(f"\n{'='*90}")
        print(f"{'Name':<30} {'Version':<15} {'Owner':<20} {'Verified':<10} {'Downloads':<10}")
        print(f"{'='*90}")
        for pkg in packages:
            verified_status = "✓ Yes" if pkg.get('verified') else "✗ No"
            print(f"{pkg.get('name', ''):<30} {pkg.get('version', ''):<15} "
                  f"{pkg.get('owner', ''):<20} {verified_status:<10} {pkg.get('download_count', 0):<10}")
        print(f"{'='*90}\n")
        print(f"Total: {len(packages)} packages")
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    def verify_package(self, package_name: str, verified: bool = True) -> bool:
        """
        Verify or unverify a package (ADMIN ONLY - requires API key)
        
        Args:
            package_name: Name of the package to verify/unverify
            verified: True to verify, False to unverify
            
        Returns:
            True if successful, False otherwise
            
        Note: Requires MEOW_ADMIN_API_KEY environment variable or api_key parameter
        """
        if not self.api_key:
            print("Error: Admin API key required. Set MEOW_ADMIN_API_KEY environment variable.")
            return False
        
        data = {"verified": verified}
        result = self._make_request('POST', f"/api/packages/{package_name}/verify", json=data)
        if result:
            status_text = "verified" if verified else "unverified"
            print(f"Package '{package_name}' has been {status_text}.")
            return True
        return False
    
    def update_package_info(self, package_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update package information (ADMIN ONLY - requires API key)
        
        Args:
            package_name: Name of the package to update
            **kwargs: Fields to update (owner, version, giturl, description, etc.)
            
        Returns:
            Updated package information or None if failed
            
        Note: Requires MEOW_ADMIN_API_KEY environment variable or api_key parameter
        """
        if not self.api_key:
            print("Error: Admin API key required. Set MEOW_ADMIN_API_KEY environment variable.")
            return None
        
        result = self._make_request('PUT', f"/api/packages/{package_name}", json=kwargs)
        return result
    
    def delete_package(self, package_name: str, hard_delete: bool = False) -> bool:
        """
        Delete a package (ADMIN ONLY - requires API key)
        
        Args:
            package_name: Name of the package to delete
            hard_delete: If True, permanently delete. If False, soft delete (default)
            
        Returns:
            True if successful, False otherwise
            
        Note: Requires MEOW_ADMIN_API_KEY environment variable or api_key parameter
        """
        if not self.api_key:
            print("Error: Admin API key required. Set MEOW_ADMIN_API_KEY environment variable.")
            return False
        
        params = {"hard_delete": hard_delete} if hard_delete else {}
        result = self._make_request('DELETE', f"/api/packages/{package_name}", params=params)
        if result is not None or result == {}:  # DELETE returns 204 No Content
            print(f"Package '{package_name}' has been deleted.")
            return True
        return False
    
    def get_admin_info(self) -> Optional[Dict[str, Any]]:
        """
        Get admin information (ADMIN ONLY - requires API key)
        
        Returns:
            Admin info or None if failed
            
        Note: Requires MEOW_ADMIN_API_KEY environment variable or api_key parameter
        """
        if not self.api_key:
            print("Error: Admin API key required. Set MEOW_ADMIN_API_KEY environment variable.")
            return None
        
        return self._make_request('GET', "/admin/info")
    
    def health_check(self) -> bool:
        """Check if the API server is healthy and reachable"""
        result = self._make_request('GET', "/health")
        if result:
            print(f"API Server Status: {result.get('status', 'unknown')}")
            return True
        return False


# ============================================================================
# PARSER INTEGRATION POINTS
# Add these function calls in main.py where parser arguments are handled
# ============================================================================

def handle_install_command(package_name: str, source: str = "meow"):
    """
    Handle 'install' command from parser
    CALL THIS FROM: main.py -> if args.command == 'install'
    
    Args:
        package_name: Name of package to install
        source: Source to install from (if 'meow', use API client)
    """
    if source == "meow":
        # Use Meow API client
        client = MeowAPIClient()
        client.install_package(package_name)
    else:
        # Use other sources (pacman, flathub, aur, etc.)
        # TODO: Integrate with existing choose_source() function
        from installer import choose_source
        choose_source(source, package_name)


def handle_search_command(query: str, verified_only: bool = False):
    """
    Handle 'search' command from parser
    CALL THIS FROM: main.py -> if args.command == 'search'
    
    Args:
        query: Search query string
        verified_only: Only show verified packages
    """
    client = MeowAPIClient()
    results = client.search_packages(query, verified_only=verified_only)
    
    if not results:
        print(f"No packages found matching '{query}'")
        return
    
    print(f"\nFound {len(results)} package(s) matching '{query}':\n")
    for pkg in results:
        verified_badge = " [✓ VERIFIED]" if pkg.get('verified') else " [⚠ UNVERIFIED]"
        print(f"  • {pkg.get('name')} (v{pkg.get('version')}) - {pkg.get('owner')}{verified_badge}")
        if pkg.get('description'):
            print(f"    {pkg.get('description')[:80]}...")
        print()


def handle_update_command(package_name: str, source: str = None):
    """
    Handle 'update' command from parser
    CALL THIS FROM: main.py -> if args.command == 'update'
    
    Args:
        package_name: Name of package to update (can be list from parser)
        source: Source to update from (if 'meow', use API client)
    """
    # Handle list input from parser
    if isinstance(package_name, list):
        package_name = package_name[0] if package_name else None
    
    if not package_name:
        print("Error: Package name required")
        return
    
    if source == "meow" or (isinstance(source, list) and source and source[0] == "meow"):
        # Use Meow API client
        client = MeowAPIClient()
        client.update_package(package_name)
    else:
        # Use other sources
        # TODO: Integrate with existing choose_update_source() function
        from installer import choose_update_source
        choose_update_source(package_name, source)


def handle_info_command(package_name: str):
    """
    Handle 'info' command (if you add it to parser)
    CALL THIS FROM: main.py -> if args.command == 'info'
    
    Args:
        package_name: Name of package to get info for
    """
    client = MeowAPIClient()
    client.print_package_info(package_name)


def handle_list_command(limit: int = 50):
    """
    Handle 'list' command (if you add it to parser)
    CALL THIS FROM: main.py -> if args.command == 'list'
    
    Args:
        limit: Maximum number of packages to list
    """
    client = MeowAPIClient()
    client.list_packages(limit=limit)


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example usage
    client = MeowAPIClient()
    
    # Health check
    print("Checking API server...")
    if not client.health_check():
        sys.exit(1)
    
    # Search packages
    print("\nSearching for packages...")
    results = client.search_packages("example")
    for pkg in results:
        print(f"  - {pkg.get('name')}")
    
    # Get package info
    print("\nGetting package info...")
    client.print_package_info("example-package")
    
    # List all packages
    print("\nListing all packages...")
    client.list_packages(limit=10)

