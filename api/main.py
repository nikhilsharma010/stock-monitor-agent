from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from local directory (copied files)
from analyzer import StockAnalyzer

app = FastAPI(
    title="Alpha Intelligence API",
    description="Financial intelligence platform API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
logger.info("Initializing StockAnalyzer...")
analyzer = StockAnalyzer()
logger.info("StockAnalyzer initialized successfully")

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up...")
    logger.info(f"Running on port: {os.getenv('PORT', '8000')}")

@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {
        "message": "Alpha Intelligence API", 
        "version": "2.0.0", 
        "status": "running",
        "endpoints": ["/health", "/api/stocks/{ticker}"]
    }

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy", "service": "Alpha Intelligence API", "port": os.getenv("PORT", "unknown")}

@app.get("/api/stocks/{ticker}")
async def get_stock_analysis(ticker: str):
    """Get comprehensive stock analysis"""
    logger.info(f"Stock analysis requested for: {ticker}")
    try:
        return {
            "ticker": ticker,
            "quote": analyzer.get_stock_quote(ticker),
            "financials": analyzer.get_basic_financials(ticker),
            "metrics": analyzer.get_performance_metrics(ticker),
            "profile": analyzer.get_company_profile(ticker)
        }
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        return {"error": str(e), "ticker": ticker}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting uvicorn on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
