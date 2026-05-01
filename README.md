# FastAPI Application

## Project Structure

```
app/
├── api/          # API route handlers
├── core/         # Core configuration (config, logger)
├── models/       # Database models
├── schemas/      # Pydantic schemas (request/response)
├── services/     # Business logic layer
├── utils/        # Utility functions
└── main.py       # Application entry point
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and adjust settings:

```bash
cp .env.example .env
```

### 3. Run Application

**Development mode (with auto-reload):**

```bash
python app/main.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Production mode:**

```bash
DEBUG=false uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## API Endpoints

- `GET /` - Root endpoint (health check)
- `GET /health` - Detailed health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Configuration

All configuration is managed through environment variables (see `.env.example`):

- **PROJECT_NAME**: Application name
- **ENVIRONMENT**: `development` or `production`
- **DEBUG**: Enable debug mode (auto-reload, verbose logging)
- **HOST/PORT**: Server binding
- **ALLOWED_ORIGINS**: CORS allowed origins (comma-separated)
- **LOG_LEVEL**: Logging level (DEBUG/INFO/WARNING/ERROR)
- **LOG_TO_FILE**: Enable file logging (creates `logs/app.log`)

## Logging

- **Console**: Always enabled, outputs to stdout
- **File**: Optional (set `LOG_TO_FILE=true`), rotates at 10MB with 5 backups
- **Format**: `YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message`

## Development Guidelines

- All route handlers use `async def`
- Use Pydantic models for request/response validation
- Database operations via `aiosqlite` (async)
- HTTP calls via `httpx.AsyncClient`
- File I/O via `aiofiles`
- Error handling: raise `HTTPException` for business errors
- Naming: English identifiers, snake_case for functions/variables

## Security Notes

- Never commit `.env` files (already in `.gitignore`)
- Store secrets in environment variables, not in code
- CORS origins should be restricted in production
- Use HTTPS in production deployments
