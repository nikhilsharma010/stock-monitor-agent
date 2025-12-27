# Interactive Bot Commands Guide

## 🎮 Control Your Stock Monitor via Telegram!

You can now manage your stock monitor directly from Telegram using simple commands.

## Available Commands

### 📊 Stock Management

**Add a stock to monitor:**
```
/add TICKER
```
Example: `/add AAPL` - Adds Apple stock to monitoring

**Remove a stock:**
```
/remove TICKER
```
Example: `/remove BYND` - Stops monitoring Beyond Meat

**List all stocks:**
```
/list
```
Shows all active and disabled stocks with current settings

### 🧠 AI Analysis & Expert Commentary

**Detailed Analysis:**
```
/analyse TICKER
```
Example: `/analyse CCCC` - Returns fundamental data (P/E, Market Cap) + AI Buy/Hold/Sell recommendation.

**Ask the AI Expert:**
```
/ask TICKER QUESTION
```
Example: `/ask CCCC Who are their main competitors?` - Returns a factored answer about the company.

### ⚙️ Settings

**Change check interval:**
```
/interval MINUTES
```
Examples:
- `/interval 1` - Check every 1 minute
- `/interval 5` - Check every 5 minutes  
- `/interval 15` - Check every 15 minutes (default)
- `/interval 60` - Check every hour

**Check current status:**
```
/status
```
Shows how many stocks you're monitoring and current settings

**Get help:**
```
/help
```
Shows all available commands

## Quick Examples

### Add Multiple Stocks
```
/add AAPL
/add TSLA
/add NVDA
/list
```

### Change to Fast Updates
```
/interval 1
```
Now you'll get updates every minute!

### Remove a Stock
```
/remove BYND
/list
```

## ✨ Live Updates

The agent now supports **Live Configuration Updates**. Changes you make via Telegram commands (like adding a stock or changing the interval) take effect **immediately** without needing to restart the bot! 🚀

## Current Configuration

Your bot: `@Trade_stalker_010_bot`

Currently monitoring:
- CCCC (C4 Therapeutics)
- BYND (Beyond Meat)

Check interval: 15 minutes
Price threshold: 0.5%

## Try It Now!

Open Telegram and send:
```
/help
```

to see all commands!
