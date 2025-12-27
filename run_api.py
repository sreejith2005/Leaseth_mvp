"""
FastAPI Application Runner
Start the Leaseth scoring API
"""

import uvicorn
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 70)
    logger.info("Starting Leaseth AI Scoring API")
    logger.info("=" * 70)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_VERSION}")
    logger.info(f"Running on http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Swagger UI: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    logger.info(f"ReDoc: http://{settings.API_HOST}:{settings.API_PORT}/redoc")
    logger.info("=" * 70)

    uvicorn.run(
        "src.api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
