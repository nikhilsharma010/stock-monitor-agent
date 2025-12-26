# Final Setup Instructions

## Your Configuration

I have the following information:

✅ **Finnhub API Key**: `d57bo49r01qrcrnai0fgd57bo49r01qrcrnai0g0`  
✅ **Telegram Chat ID**: `936814417`  
✅ **Bot Username**: `@Trade_stalker_010_bot`  
❓ **Bot Token**: *You need to provide this*

## Get Your Bot Token

When you created `@Trade_stalker_010_bot` with @BotFather, it gave you a token. 

If you don't have it:
1. Open Telegram
2. Search for `@BotFather`
3. Send `/mybots`
4. Select `@Trade_stalker_010_bot`
5. Click "API Token"
6. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Create .env File

```bash
cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent

# Create .env file with your bot token
cat > .env << 'EOF'
FINNHUB_API_KEY=d57bo49r01qrcrnai0fgd57bo49r01qrcrnai0g0
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=936814417
CHECK_INTERVAL_MINUTES=15
EOF
```

**Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token!**

## Test & Run

```bash
# Test all components
./setup.sh

# If tests pass, start the agent
cd src
python3 main.py
```

## Important

Make sure you've clicked "Start" on `@Trade_stalker_010_bot` in Telegram before running!

You'll receive notifications at Chat ID: 936814417 (your Telegram account).
