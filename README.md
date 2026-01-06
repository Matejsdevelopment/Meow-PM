# Meow Package Manager - Server-Side API

REST API for managing packages in the Meow package manager.

## Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python MeowAPI/MeowAPI.py
```

Or using uvicorn directly:
```bash
uvicorn MeowAPI.MeowAPI:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Package Management

- `POST /api/packages` - Create a new package
- `GET /api/packages` - Get all packages (with pagination)
- `GET /api/packages/{name}` - Get package by name
- `GET /api/packages/id/{package_id}` - Get package by ID
- `PUT /api/packages/{name}` - Update a package
- `DELETE /api/packages/{name}` - Delete a package (soft delete by default)
- `POST /api/packages/{name}/download` - Increment download count
- `GET /api/packages/{name}/versions` - Get package version info

### Utility

- `GET /` - API information
- `GET /health` - Health check

## Package Schema

Each package requires:
- **name** (string, required): Package name (unique)
- **owner** (string, required): Package owner/maintainer
- **version** (string, required): Package version
- **giturl** (string, required): Git URL to download the package from

Optional fields:
- **description** (string): Package description
- **license** (string): Package license
- **dependencies** (string): Package dependencies (comma-separated or JSON)
- **homepage** (string): Package homepage URL
- **repository** (string): Package repository URL
- **tags** (string): Package tags (comma-separated)

## Example Usage

### Create a Package

```bash
curl -X POST "http://localhost:8000/api/packages" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example-package",
    "owner": "john_doe",
    "version": "1.0.0",
    "giturl": "https://github.com/john_doe/example-package.git",
    "description": "An example package",
    "license": "MIT",
    "tags": "example,test"
  }'
```

### Get All Packages

```bash
curl "http://localhost:8000/api/packages"
```

### Get Package by Name

```bash
curl "http://localhost:8000/api/packages/example-package"
```

### Update a Package

```bash
curl -X PUT "http://localhost:8000/api/packages/example-package" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.1.0",
    "description": "Updated description"
  }'
```

### Delete a Package

```bash
# Soft delete (default)
curl -X DELETE "http://localhost:8000/api/packages/example-package"

# Hard delete
curl -X DELETE "http://localhost:8000/api/packages/example-package?hard_delete=true"
```

## Database

The API uses SQLite by default (`meow_registry.db`). The database is automatically created and tables are initialized on first run.

To use a different database, set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="sqlite:///./custom_path.db"
python MeowAPI/MeowAPI.py
```


