from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from analyzer import StockAnalyzer

app = FastAPI(
    title="Alpha Intelligence API",
    description="Financial intelligence platform API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "https://*.vercel.app",   # Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = StockAnalyzer()

@app.get("/")
def root():
    return {"message": "Alpha Intelligence API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

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

@app.get("/api/stocks/{ticker}/chart")
async def get_stock_chart(ticker: str):
    """Get stock chart data"""
    try:
        # This will return chart image path or data
        return {"ticker": ticker, "chart": "chart_data"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
