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
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "https://*.vercel.app",   # Vercel deployments
        "https://alphaintelligence.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = StockAnalyzer()

# Only initialize database if DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL != "sqlite:///./alpha_intelligence.db":
    try:
        from app.routes import goals, theses, watchlist
        from app.database import engine
        from app import models
        
        # Create database tables
        models.Base.metadata.create_all(bind=engine)
        
        # Include routers
        app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
        app.include_router(theses.router, prefix="/api/theses", tags=["theses"])
        app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
        
        print("✅ Database connected and routes loaded")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("Running in stock-analysis-only mode")
else:
    print("⚠️ No DATABASE_URL set. Running in stock-analysis-only mode")

@app.get("/")
def root():
    return {"message": "Alpha Intelligence API", "version": "2.0.0", "status": "running"}

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
        return {"ticker": ticker, "chart": "chart_data"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
