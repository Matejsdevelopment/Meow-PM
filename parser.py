from argparse import ArgumentParser

def create_parser():
    parser = ArgumentParser(description="The Meow package manager — a simple package manager for Linux systems!")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    install_parser = subparsers.add_parser('install', help='Install a package')

    install_parser.add_argument(
        'package',
        type=str,
        help='The package to install'
    )

    install_parser.add_argument(
        '-src',
        type=str,
        nargs='?',
        default=None,
        choices=['pac', 'pacman', 'flathub', 'fb', 'fk', 'flatpak', 'aur', 'meow'],
        help='Source to install the package from'
    )

    
    search_parser = subparsers.add_parser('search', help='Search for packages')  
    search_parser.add_argument(
        'query',
        type=str,
        help='The search query'
    )
    
    update_parser = subparsers.add_parser('update', help='update a package')  
    update_parser.add_argument(
        'package',
        type=str,
        help='The package to update'
    )
    update_parser.add_argument(
        '--source', '-src',
        type=str,
        required=False,
        default=None,
        choices=['pac', 'pacman', 'flathub', 'fb', 'fk', 'flatpak', 'aur', 'meow'],
        help='Source to update the package from (pac/pacman, flathub/fb/fk/flatpak, aur)'
    )
    
    selfupdate_parser = subparsers.add_parser('selfupdate', help='Install a package')  
    
    check_parser = subparsers.add_parser('check', help='Check if a package exists')
    check_parser.add_argument(
        'pkg',
        type=str,
        help='The package name to check'
    )
    
    subparsers.add_parser('fetch', help='Fetch info about your computer')  
    
    return parser