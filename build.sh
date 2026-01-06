#!/bin/bash

# ===================================
#    Meow Package Manager Builder
# ===================================

set -e

echo "Building Meow Package Manager..."
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Project root detected at: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# --------------------------------------------------
# 1. Verify required client-side files exist
# --------------------------------------------------

REQUIRED_FILES=(
    "main.py"
    "builder.py"
    "installer.py"
    "meowinstaller.py"
)

echo "Checking required files..."

for FILE in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$FILE" ]; then
        echo "Missing required file: $FILE"
        echo "Build aborted."
        exit 1
    fi
done

echo "✔ All required client files found!"

# --------------------------------------------------
# 2. Create combined runnable script: `meow`
# --------------------------------------------------

INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

TARGET="$INSTALL_DIR/meow"

echo ""
echo "⚙️ Generating executable: $TARGET"

cat > "$TARGET" <<EOF
#!/usr/bin/env python3
# Auto-generated Meow PM command wrapper

import sys
import os

# Add project directory to import path
sys.path.insert(0, "$PROJECT_ROOT")

# Start Meow PM
from main import main

if __name__ == "__main__":
    main()
EOF

chmod +x "$TARGET"

echo "✔ Installed Meow PM → $TARGET"

# --------------------------------------------------
# 3. Ensure ~/.local/bin is in PATH
# --------------------------------------------------

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "~/.local/bin is not in your PATH"
    echo "→ Adding it automatically"

    SHELL_NAME=$(basename "$SHELL")

    if [ "$SHELL_NAME" = "bash" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo "✔ Updated ~/.bashrc"
    elif [ "$SHELL_NAME" = "zsh" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        echo "✔ Updated ~/.zshrc"
    else
        echo "⚠ Unknown shell ($SHELL_NAME). Add this manually:"
        echo 'export PATH="$HOME/.local/bin:$PATH"'
    fi
else
    echo "✔ ~/.local/bin already in PATH"
fi

echo ""
echo "Meow Package Manager installed successfully!"
echo "Run it using:"
echo "   meow"
echo ""
