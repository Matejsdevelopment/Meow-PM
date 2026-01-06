# Quick Start: Setting Up Security

## 1. Generate Your Admin API Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated key.

## 2. Set the Environment Variable

```bash
export MEOW_ADMIN_API_KEY="your-generated-key-here"
```

To make it permanent, add to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export MEOW_ADMIN_API_KEY="your-generated-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## 3. Start the Server

```bash
python MeowAPI/MeowAPI.py
```

The server will use your API key. If you don't set it, a temporary key will be generated (shown in console - **copy it!**).

## 4. Use Admin Functions

### With Python Client:
```python
from MeowAPI.client import MeowAPIClient

# API key is automatically loaded from MEOW_ADMIN_API_KEY env var
client = MeowAPIClient()

# Verify a package
client.verify_package("package-name", verified=True)

# Update package info
client.update_package_info("package-name", version="2.0.0", description="New version")

# Delete a package
client.delete_package("package-name", hard_delete=False)
```

### With curl:
```bash
curl -X POST "http://localhost:8000/api/packages/package-name/verify" \
  -H "X-API-Key: your-admin-api-key" \
  -H "Content-Type: application/json" \
  -d '{"verified": true}'
```

## That's It!

Now only you can:
- ✅ Verify/unverify packages
- ✅ Update packages
- ✅ Delete packages

Everyone else can:
- ✅ View packages
- ✅ Create packages (they start unverified)
- ✅ Search packages

See `SECURITY.md` for more details.

