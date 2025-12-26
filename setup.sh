#!/bin/bash
# Quick setup script for local testing

echo "🚀 Stock Monitor Agent - Quick Setup"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your credentials:"
    echo "   1. FINNHUB_API_KEY (from finnhub.io)"
    echo "   2. TELEGRAM_BOT_TOKEN (from @BotFather)"
    echo "   3. TELEGRAM_CHAT_ID (from @userinfobot)"
    echo ""
    echo "After editing .env, run this script again."
    exit 1
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🧪 Testing components..."
echo ""

# Test Telegram
echo "1️⃣ Testing Telegram connection..."
cd src
python3 telegram_notifier.py
if [ $? -eq 0 ]; then
    echo "✅ Telegram test passed!"
else
    echo "❌ Telegram test failed. Check your credentials."
    exit 1
fi

echo ""
echo "2️⃣ Testing stock data fetching..."
python3 stock_monitor.py
if [ $? -eq 0 ]; then
    echo "✅ Stock monitor test passed!"
else
    echo "❌ Stock monitor test failed. Check your Finnhub API key."
    exit 1
fi

echo ""
echo "✅ All tests passed!"
echo ""
echo "🎉 Ready to start monitoring!"
echo ""
echo "To start the agent, run:"
echo "  cd src && python3 main.py"
echo ""
echo "Or run in background:"
echo "  cd src && nohup python3 main.py > ../monitor.log 2>&1 &"
echo ""
