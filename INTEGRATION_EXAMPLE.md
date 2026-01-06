# Integration Example

This shows how to integrate the client with your parser in `main.py`:

## Updated main.py Example

```python
#!/usr/bin/env python3
from parser import create_parser
from installer import choose_source, search_packages, choose_update_source
from MeowAPI.client import (
    handle_install_command,
    handle_search_command,
    handle_update_command,
    handle_info_command,
    handle_list_command
)
import requests
import platform
import argparse


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
        # ========================================================================
        # PARSER INTEGRATION POINT: install command
        # ========================================================================
        # If source is 'meow', use the API client
        # Otherwise, use existing installer functions
        if args.source == 'meow':
            handle_install_command(args.package, args.source)
        else:
            choose_source(args.source, args.package)

    elif args.command == 'search':
        # ========================================================================
        # PARSER INTEGRATION POINT: search command
        # ========================================================================
        # Use the client-side search function
        handle_search_command(args.query)
        # Or use existing: search_packages(args.query)

    elif args.command == 'fetch':
        fetch_system_info()

    elif args.command == "update":
        # ========================================================================
        # PARSER INTEGRATION POINT: update command
        # ========================================================================
        # If source is 'meow', use the API client
        # Otherwise, use existing installer functions
        if args.source and (args.source == 'meow' or (isinstance(args.source, list) and args.source[0] == 'meow')):
            handle_update_command(args.package, args.source)
        else:
            choose_update_source(args.package, args.source)
    
    # Optional: Add these commands to your parser
    # elif args.command == 'info':
    #     handle_info_command(args.package)
    # elif args.command == 'list':
    #     handle_list_command(args.limit)
    else:
        parser.print_help()
```

## Adding New Commands to Parser

If you want to add `info` and `list` commands, update `parser.py`:

```python
# Add to parser.py after the fetch command:

# --- INFO COMMAND ---
info_parser = subparsers.add_parser('info', help='Get information about a package')
info_parser.add_argument(
    'package',
    type=str,
    help='The package to get information about'
)

# --- LIST COMMAND ---
list_parser = subparsers.add_parser('list', help='List all available packages')
list_parser.add_argument(
    '--limit', '-l',
    type=int,
    default=50,
    help='Maximum number of packages to list'
)
```

Then in `main.py`:
```python
elif args.command == 'info':
    handle_info_command(args.package)
elif args.command == 'list':
    handle_list_command(args.limit)
```

