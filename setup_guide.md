# Stock Monitor Agent - Setup Guide

This guide provides detailed instructions for setting up and deploying your stock monitoring agent.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Telegram Bot Setup](#telegram-bot-setup)
3. [Finnhub API Setup](#finnhub-api-setup)
4. [Testing](#testing)
5. [Deployment Options](#deployment-options)

---

## Initial Setup

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: macOS, Linux, or Windows
- **Internet**: Stable connection required

### Install Python Dependencies

```bash
cd stock-monitor-agent
pip install -r requirements.txt
```

If you prefer using a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Telegram Bot Setup

### Step 1: Create Your Bot

1. Open Telegram on your phone or desktop
2. Search for `@BotFather` (official Telegram bot)
3. Start a chat and send `/newbot`
4. Follow the prompts:
   - Choose a name for your bot (e.g., "My Stock Monitor")
   - Choose a username (must end in 'bot', e.g., "mystockmonitor_bot")
5. **Save the bot token** - it looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Get Your Chat ID

1. Search for `@userinfobot` on Telegram
2. Start a chat with it
3. It will automatically send you your user information
4. **Copy your Chat ID** - it's a number like: `123456789`

### Step 3: Start Your Bot

1. Search for your bot using the username you created
2. Click "Start" or send `/start` to activate it

---

## Finnhub API Setup

### Step 1: Create Account

1. Go to [finnhub.io/register](https://finnhub.io/register)
2. Sign up with your email
3. Verify your email address

### Step 2: Get API Key

1. Log in to [finnhub.io/dashboard](https://finnhub.io/dashboard)
2. Your API key is displayed on the dashboard
3. **Copy the API key** - it looks like: `abc123def456ghi789`

### Free Tier Limits

- 60 API calls per minute
- Sufficient for monitoring multiple stocks every 15 minutes
- No credit card required

---

## Configuration

### Create .env File

```bash
cd stock-monitor-agent
cp .env.example .env
```

Edit the `.env` file with your credentials:

```bash
# Use nano, vim, or any text editor
nano .env
```

Add your values:

```
FINNHUB_API_KEY=your_actual_api_key_here
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
CHECK_INTERVAL_MINUTES=15
```

**Important**: Never commit the `.env` file to version control!

### Configure Stocks

Edit `config/stocks.json` to customize which stocks to monitor:

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

---

## Testing

### Test 1: Telegram Connection

```bash
cd src
python telegram_notifier.py
```

**Expected output:**
```
Testing Telegram Notifier...
✅ Telegram bot connected: @your_bot_name
✅ Test message sent successfully!
```

You should receive a test message on Telegram.

### Test 2: Stock Data Fetching

```bash
python stock_monitor.py
```

**Expected output:**
```
Testing Stock Monitor...
==================================================
Fetching data for CCCC...
==================================================
✅ C4 Therapeutics Inc
   Price: $X.XX
   Change: +X.XX%
   ...
```

### Test 3: News Fetching

```bash
python news_monitor.py
```

**Expected output:**
```
Testing News Monitor...
==================================================
Fetching news for CCCC...
==================================================
✅ Found X articles
...
```

### Test 4: Full System

```bash
python main.py
```

**Expected output:**
```
============================================================
Stock Monitor Agent with Telegram Notifications
============================================================

✅ All systems ready!

Starting monitoring...
Press Ctrl+C to stop
```

You should receive a startup notification on Telegram.

---

## Deployment Options

### Option 1: Local Machine (Simple)

**Pros**: Easy, no additional costs  
**Cons**: Requires computer to stay on

```bash
cd src
python main.py
```

Keep the terminal window open. The agent will run until you stop it (Ctrl+C).

### Option 2: Background Process (macOS/Linux)

**Pros**: Runs in background, survives terminal close  
**Cons**: Stops when computer shuts down

```bash
cd src
nohup python main.py > ../monitor.log 2>&1 &
```

To check if it's running:
```bash
ps aux | grep main.py
```

To stop it:
```bash
ps aux | grep main.py
kill <process_id>
```

To view logs:
```bash
tail -f ../monitor.log
```

### Option 3: Cloud Server (Recommended for 24/7)

Deploy to a cloud provider for true 24/7 operation.

#### AWS EC2 (Free Tier Available)

1. Launch a t2.micro instance (free tier eligible)
2. SSH into the instance
3. Install Python and dependencies
4. Upload your code
5. Run as background process

```bash
# On EC2 instance
sudo yum install python3 -y
cd /home/ec2-user
git clone <your-repo> # or upload files
cd stock-monitor-agent
pip3 install -r requirements.txt
cd src
nohup python3 main.py > ../monitor.log 2>&1 &
```

#### DigitalOcean Droplet

1. Create a $5/month droplet (Ubuntu)
2. SSH into droplet
3. Follow similar steps as AWS

#### Google Cloud Compute Engine

1. Create a free tier e2-micro instance
2. SSH and set up similar to AWS

### Option 4: Docker (Advanced)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

Build and run:
```bash
docker build -t stock-monitor .
docker run -d --name stock-monitor --env-file .env stock-monitor
```

---

## Monitoring and Maintenance

### View Logs

```bash
# If running in foreground: check terminal output

# If running with nohup:
tail -f monitor.log

# If running as systemd service:
journalctl -u stock-monitor -f
```

### Update Stock List

1. Edit `config/stocks.json`
2. Restart the agent

### Troubleshooting

**Problem**: No notifications received

**Solutions**:
- Verify Telegram credentials in `.env`
- Check you started a chat with your bot
- Run `python telegram_notifier.py` to test

**Problem**: API errors

**Solutions**:
- Check Finnhub API key is correct
- Verify you haven't exceeded rate limits
- Check internet connection

**Problem**: Agent stops unexpectedly

**Solutions**:
- Check logs for errors
- Ensure system has enough memory
- Verify Python dependencies are installed

---

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use environment variables** for sensitive data
3. **Restrict file permissions** on `.env`:
   ```bash
   chmod 600 .env
   ```
4. **Regularly update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## Next Steps

1. ✅ Complete setup and testing
2. ✅ Run for 24 hours to verify stability
3. ✅ Adjust notification settings as needed
4. ✅ Consider cloud deployment for 24/7 operation
5. ✅ Monitor API usage to stay within free tier limits

---

## Support

If you encounter issues:

1. Check logs in `stock_monitor.log`
2. Verify all credentials in `.env`
3. Test components individually
4. Check API status pages:
   - [Finnhub Status](https://finnhub.io)
   - [Telegram Status](https://telegram.org)

Happy monitoring! 📊📈
