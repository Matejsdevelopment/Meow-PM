# Security Guide

## Overview

The Meow Package Manager API includes comprehensive security measures to protect against unauthorized access and malicious input.

## Authentication

### Admin API Key

Only you (the admin) can perform sensitive operations like:
- Verifying/unverifying packages
- Updating packages
- Deleting packages

### Setting Your Admin API Key

**Option 1: Environment Variable (Recommended)**
```bash
export MEOW_ADMIN_API_KEY="your-secure-api-key-here"
python MeowAPI/MeowAPI.py
```

**Option 2: Generate a Secure Key**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Option 3: Use the Generated Key**
If you don't set `MEOW_ADMIN_API_KEY`, the server will generate one and display it on startup. **Copy this key and set it as an environment variable for production!**

### Using the API Key

#### With curl:
```bash
curl -X POST "http://localhost:8000/api/packages/example/verify" \
  -H "X-API-Key: your-admin-api-key" \
  -H "Content-Type: application/json" \
  -d '{"verified": true}'
```

#### With Python Client:
```python
from MeowAPI.client import MeowAPIClient

# Option 1: Set environment variable
import os
os.environ["MEOW_ADMIN_API_KEY"] = "your-admin-api-key"
client = MeowAPIClient()

# Option 2: Pass directly
client = MeowAPIClient(api_key="your-admin-api-key")

# Now you can use admin functions
client.verify_package("example-package", verified=True)
```

## Protected Endpoints

The following endpoints require admin authentication (X-API-Key header):

- `POST /api/packages/{name}/verify` - Verify/unverify packages
- `PUT /api/packages/{name}` - Update packages
- `DELETE /api/packages/{name}` - Delete packages
- `GET /admin/info` - Get admin information

## Public Endpoints

These endpoints are publicly accessible (no authentication required):

- `GET /api/packages` - List packages
- `GET /api/packages/{name}` - Get package info
- `GET /api/packages/id/{id}` - Get package by ID
- `POST /api/packages` - Create package (starts as unverified)
- `POST /api/packages/{name}/download` - Increment download count
- `GET /health` - Health check

## Security Features

### 1. Input Validation
- Package names: Only alphanumeric, dots, hyphens, underscores
- Git URLs: Validated against git URL patterns
- String length limits on all fields
- Sanitization of control characters and null bytes

### 2. Security Headers
The API automatically adds security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### 3. CORS Configuration
Configure allowed origins via environment variable:
```bash
export CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

### 4. Logging
All admin actions are logged:
- Package verification/unverification
- Package updates
- Package deletions
- Failed authentication attempts

### 5. Verified Field Protection
- Users **cannot** set `verified: true` when creating packages
- Users **cannot** update the `verified` field via PUT endpoint
- Only admins can verify packages via the `/verify` endpoint

## Production Checklist

Before deploying to production:

- [ ] Set a strong `MEOW_ADMIN_API_KEY` environment variable
- [ ] Configure `CORS_ORIGINS` to restrict allowed origins
- [ ] Use HTTPS (set up reverse proxy with SSL/TLS)
- [ ] Review and adjust logging levels
- [ ] Set up database backups
- [ ] Consider adding rate limiting
- [ ] Review and test all security measures
- [ ] Keep dependencies updated

## Example: Setting Up for Production

```bash
# Generate a secure API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variables
export MEOW_ADMIN_API_KEY="your-generated-key-here"
export CORS_ORIGINS="https://yourdomain.com"
export DATABASE_URL="sqlite:///./meow_registry.db"

# Run the server
python MeowAPI/MeowAPI.py
```

## Troubleshooting

### "API key required" error
- Make sure you've set `MEOW_ADMIN_API_KEY` environment variable
- Check that you're including the `X-API-Key` header in requests
- Verify the API key matches what's configured on the server

### "Invalid API key" error
- Double-check the API key is correct
- Check for extra spaces or newlines in the key
- Regenerate the key if needed

### Can't verify packages
- Ensure you're using the admin API key (not a regular user)
- Check server logs for authentication errors
- Verify the endpoint requires authentication (it should)

## Additional Security Recommendations

1. **Rate Limiting**: Consider adding rate limiting to prevent abuse
2. **IP Whitelisting**: For extra security, whitelist admin IPs
3. **Two-Factor Authentication**: For production, consider 2FA for admin operations
4. **Audit Logging**: Keep detailed logs of all admin actions
5. **Regular Security Audits**: Periodically review and update security measures

