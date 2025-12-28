from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = StockAnalyzer()

@app.get("/")
def root():
    return {
        "message": "Alpha Intelligence API", 
        "version": "2.0.0", 
        "status": "running",
        "endpoints": ["/health", "/api/stocks/{ticker}"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Alpha Intelligence API"}

@app.get("/api/stocks/{ticker}")
async def get_stock_analysis(ticker: str):
    """Get comprehensive stock analysis"""
    try:
        return {
            "ticker": ticker,
            "quote": analyzer.get_stock_quote(ticker),
            "financials": analyzer.get_basic_financials(ticker),
            "metrics": analyzer.get_performance_metrics(ticker),
            "profile": analyzer.get_company_profile(ticker)
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

if __name__ == "__main__":
    import uvicorn
    # Use Railway's PORT environment variable
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
