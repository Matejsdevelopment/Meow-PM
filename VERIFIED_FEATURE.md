# Verified Packages Feature

## Overview

The Meow Package Manager API now includes a **verified** field to mark trusted packages. This helps users identify which packages have been reviewed and verified by administrators.

## How It Works

### For Package Creators
- Anyone can POST packages to the API (no authentication required)
- **All new packages start as `verified: false` by default**
- Packages remain unverified until an admin verifies them

### For Administrators
- Use the `/api/packages/{name}/verify` endpoint to verify or unverify packages
- **Note**: In production, you should add authentication/authorization to this endpoint

### For Users
- Packages show a verified status badge:
  - `✓ VERIFIED` - Package has been verified by admins
  - `⚠ UNVERIFIED` - Package has not been verified yet
- You can filter to show only verified packages when searching or listing

## API Endpoints

### Verify a Package
```bash
POST /api/packages/{name}/verify
Content-Type: application/json

{
  "verified": true
}
```

### Get Only Verified Packages
```bash
GET /api/packages?verified_only=true
```

## Client Usage

### Search with Verified Filter
```python
from MeowAPI.client import MeowAPIClient

client = MeowAPIClient()
# Search only verified packages
results = client.search_packages("example", verified_only=True)
```

### List Only Verified Packages
```python
client.list_packages(verified_only=True)
```

### Verify a Package (Admin)
```python
client.verify_package("package-name", verified=True)
```

## Database Migration

If you have an existing database, you'll need to add the `verified` column. SQLAlchemy will attempt to create it automatically, but if you have existing data, you may need to:

1. **Option 1**: Delete the database and let it recreate (loses all data)
   ```bash
   rm meow_registry.db
   # Restart the server - it will create a new database
   ```

2. **Option 2**: Manually add the column (preserves data)
   ```sql
   ALTER TABLE packages ADD COLUMN verified BOOLEAN DEFAULT 0;
   ```

3. **Option 3**: Use SQLAlchemy migrations (recommended for production)
   - Consider using Alembic for proper database migrations

## Security Note

**Important**: The verify endpoint currently has no authentication. In production, you should:

1. Add authentication (API keys, JWT tokens, etc.)
2. Add authorization to ensure only admins can verify packages
3. Consider adding rate limiting to prevent abuse

Example with FastAPI dependencies:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Check if token is valid admin token
    if credentials.credentials != "your-admin-token":
        raise HTTPException(status_code=403, detail="Not authorized")
    return True

@app.post("/api/packages/{name}/verify", dependencies=[Depends(verify_admin)])
async def verify_package(...):
    # ... existing code
```

