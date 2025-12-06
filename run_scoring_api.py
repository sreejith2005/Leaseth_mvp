"""
Production runner for the two-stage tenant scoring API.
Provides flexible configuration for development and production deployments.
"""
import uvicorn
import os


def run_dev():
    """Run server in development mode with hot reload"""
    uvicorn.run(
        "scoring_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )


def run_prod():
    """Run server in production mode with optimized settings"""
    # Get config from environment variables or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8002))
    workers = int(os.getenv("WORKERS", 4))
    
    uvicorn.run(
        "scoring_api:app",
        host=host,
        port=port,
        workers=workers,
        log_level="warning",
        access_log=True,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )


if __name__ == "__main__":
    import sys
    
    # Check for environment or command-line argument
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "dev" if env == "development" else "prod"
    
    if mode == "prod" or mode == "production":
        print("🚀 Starting server in PRODUCTION mode...")
        run_prod()
    else:
        print("🔧 Starting server in DEVELOPMENT mode...")
        run_dev()
