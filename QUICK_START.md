# Quick Start Guide - Personalized Setup

## Your Configuration

✅ **Telegram Chat ID**: `936814417` (already configured!)

## What You Need to Get

### 1. Telegram Bot Token (2 minutes)

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow prompts to create your bot
5. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
6. **Important**: Search for your new bot and click "Start" to activate it

### 2. Finnhub API Key (2 minutes)

1. Go to [finnhub.io/register](https://finnhub.io/register)
2. Sign up with email
3. Copy your API key from dashboard

## Setup Steps

```bash
# 1. Navigate to project
cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent

# 2. Create .env file
cp .env.example .env

# 3. Edit .env file
nano .env
```

**Add your credentials** (Chat ID is already filled in!):
```
FINNHUB_API_KEY=paste_your_finnhub_key_here
TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
TELEGRAM_CHAT_ID=936814417  # Already set!
```

Save with `Ctrl+O`, `Enter`, then `Ctrl+X`

## Quick Test

```bash
# Run the setup script
./setup.sh

# If all tests pass, start the agent
cd src
python3 main.py
```

You'll receive a message on Telegram (Chat ID: 936814417) confirming the agent started! 🎉

## Free Cloud Deployment

For 24/7 operation, see `FREE_CLOUD_DEPLOYMENT.md` for completely free options (no credit card needed).

**Recommended**: Render.com - Just upload files, add your 3 credentials, and deploy!
