# Stock Monitor Agent 📊

An automated agent that monitors US stocks (C4 Therapeutics & Beyond Meat) and sends real-time Telegram notifications for news and price changes.

## Features

- 📈 **Real-time Stock Monitoring**: Track stock prices using Finnhub API
- 📰 **News Alerts**: Get notified about company news instantly
- 💬 **Telegram Notifications**: Receive alerts directly on Telegram
- 🔄 **Automated Scheduling**: Runs every 15 minutes automatically
- 🗄️ **Smart Deduplication**: Prevents duplicate notifications using SQLite cache
- ⚙️ **Easy Configuration**: Simple JSON config for stocks and settings

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Telegram account
- Finnhub API account (free)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd stock-monitor-agent

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

#### Get Finnhub API Key

1. Sign up at [finnhub.io](https://finnhub.io/register)
2. Copy your API key from the dashboard

#### Set up Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Search for `@userinfobot` on Telegram
5. Start a chat and copy your Chat ID

#### Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

Add your credentials:
```
FINNHUB_API_KEY=your_finnhub_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 4. Run the Agent

```bash
cd src
python main.py
```

You should receive a startup message on Telegram confirming the agent is running!

## Configuration

### Stocks Configuration

Edit `config/stocks.json` to add or remove stocks:

```json
{
  "stocks": [
    {
      "ticker": "CCCC",
      "name": "C4 Therapeutics",
      "enabled": true
    },
    {
      "ticker": "BYND",
      "name": "Beyond Meat",
      "enabled": true
    }
  ],
  "monitoring": {
    "check_interval_minutes": 15,
    "notify_all_news": true,
    "price_change_threshold_percent": 5.0
  }
}
```

### Settings Explained

- **check_interval_minutes**: How often to check for updates (default: 15)
- **notify_all_news**: Send notifications for all news (true) or major only (false)
- **price_change_threshold_percent**: Notify when price changes by this % or more

## Testing Individual Components

Test each component separately before running the full agent:

```bash
cd src

# Test Telegram connection
python telegram_notifier.py

# Test stock data fetching
python stock_monitor.py

# Test news fetching
python news_monitor.py
```

## Project Structure

```
stock-monitor-agent/
├── config/
│   └── stocks.json          # Stock configuration
├── src/
│   ├── main.py             # Main orchestrator
│   ├── stock_monitor.py    # Stock data fetcher
│   ├── news_monitor.py     # News monitoring
│   ├── telegram_notifier.py # Telegram integration
│   └── utils.py            # Helper functions
├── data/
│   └── cache.db            # SQLite cache (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

## Running 24/7

### Option 1: Keep Terminal Open

Simply run `python main.py` and keep the terminal window open.

### Option 2: Background Process (macOS/Linux)

```bash
cd src
nohup python main.py > ../monitor.log 2>&1 &
```

To stop:
```bash
ps aux | grep main.py
kill <process_id>
```

### Option 3: Cloud Deployment

Deploy to a cloud server (AWS, Google Cloud, DigitalOcean) for 24/7 operation. See `setup_guide.md` for detailed instructions.

## Troubleshooting

### No notifications received

1. Check Telegram bot token and chat ID in `.env`
2. Run `python telegram_notifier.py` to test connection
3. Check logs in `stock_monitor.log`

### API errors

1. Verify Finnhub API key is correct
2. Check API rate limits (free tier: 60 calls/minute)
3. Ensure internet connection is stable

### Duplicate notifications

The agent uses SQLite to track sent notifications. If you're getting duplicates:
1. Delete `data/cache.db` to reset
2. Check system time is correct

## API Rate Limits

**Finnhub Free Tier:**
- 60 API calls per minute
- Sufficient for monitoring multiple stocks every 15 minutes

**Telegram Bot API:**
- Completely free
- No practical limits for personal use

## Support

For issues or questions:
1. Check logs in `stock_monitor.log`
2. Verify all credentials in `.env`
3. Test individual components separately

## License

MIT License - Free to use and modify
