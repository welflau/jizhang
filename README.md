# FastAPI Project

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Application

```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 4. Test Health Endpoint

```bash
curl http://localhost:8080/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0"
}
```

## Project Structure

```
app/
├── api/           # API endpoints
│   └── health.py  # Health check routes
├── core/          # Core configuration
│   ├── config.py  # Settings management
│   └── logger.py  # Logging setup
├── models/        # Database models (future)
├── schemas/       # Pydantic schemas (future)
├── services/      # Business logic (future)
├── utils/         # Utility functions (future)
└── main.py        # Application entry point
```

## Configuration

All configuration is managed through environment variables (`.env` file):

- `PROJECT_NAME`: Application name
- `ENVIRONMENT`: `development` or `production`
- `DEBUG`: Enable debug mode
- `PORT`: Server port (default: 8080)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)
- `LOG_TO_FILE`: Enable file logging
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)

## Logging

- Console logging enabled by default
- File logging: set `LOG_TO_FILE=true` in `.env`
- Log files stored in `logs/` directory
- Log level configurable via `LOG_LEVEL`

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Development

### Adding New Endpoints

1. Create router in `app/api/`
2. Define Pydantic schemas in `app/schemas/`
3. Register router in `app/main.py`

### Code Style

- All code identifiers in English
- Follow PEP 8 naming conventions
- Use async/await for all I/O operations
- Type hints required for function signatures
- Docstrings for all public APIs

## Security Notes

- Never commit `.env` file (already in `.gitignore`)
- Store secrets in environment variables
- Use `python-dotenv` for local development
- Production: use proper secret management service
