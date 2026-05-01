from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from pathlib import Path

from .database import engine, Base
from .routers import data_management
from .models import AccessLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Visit Counter API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    data_management.router,
    prefix="/api",
    tags=["data-management"]
)

# Serve static files
static_path = Path(__file__).parent.parent.parent / "frontend"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page"""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Visit Counter API", "docs": "/docs"}


@app.get("/api/visit")
async def record_visit(request: Request):
    """Record a visit and return current count"""
    from .database import SessionLocal
    from datetime import datetime
    
    db = SessionLocal()
    try:
        # Create new visit record
        visit = AccessLog(
            timestamp=datetime.now(),
            ip=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        db.add(visit)
        db.commit()
        
        # Get total count
        count = db.query(AccessLog).count()
        logger.info(f"Visit recorded from {request.client.host}, total: {count}")
        
        return {"count": count}
    except Exception as e:
        logger.error(f"Error recording visit: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
