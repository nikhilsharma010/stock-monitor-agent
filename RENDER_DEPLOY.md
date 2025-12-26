# Render.com Deployment Guide

## Quick Deploy to Render (5 minutes)

### Step 1: Prepare Your Project

Your project is ready! Just need to create one file:

```bash
cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent
```

### Step 2: Deploy on Render

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Background Worker"

2. **Connect Your Code**
   - Choose "Public Git repository" OR "Upload files"
   - If uploading: Select your `stock-monitor-agent` folder

3. **Configure the Service**
   - **Name**: `stock-monitor-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`

4. **Add Environment Variables**
   Click "Environment" tab and add these **exactly**:
   
   ```
   FINNHUB_API_KEY=d57bo49r01qrcrnai0fgd57bo49r01qrcrnai0g0
   TELEGRAM_BOT_TOKEN=8458864025:AAE6ZAP-zfNd4RprJg0-C5PL996cssb-n7s
   TELEGRAM_CHAT_ID=936814417
   CHECK_INTERVAL_MINUTES=15
   ```

5. **Deploy**
   - Click "Create Background Worker"
   - Wait 2-3 minutes for deployment
   - Check logs to confirm it's running

### Step 3: Verify It's Working

- Go to "Logs" tab in Render
- You should see: "Stock Monitor Agent initialized"
- Check your Telegram for startup notification

## Alternative: Upload Files Directly

If you don't want to use Git:

1. **Create a ZIP file**:
   ```bash
   cd /Users/nikhil/.gemini/antigravity/scratch
   zip -r stock-monitor.zip stock-monitor-agent -x "*.git*" -x "*__pycache__*" -x "*.db" -x ".env"
   ```

2. **Upload to Render**:
   - New Background Worker → "Upload files"
   - Upload `stock-monitor.zip`
   - Follow steps 3-5 above

## Your Configuration

✅ **Finnhub API**: `d57bo49r01qrcrnai0fgd57bo49r01qrcrnai0g0`  
✅ **Telegram Bot**: `8458864025:AAE6ZAP-zfNd4RprJg0-C5PL996cssb-n7s`  
✅ **Chat ID**: `936814417`  
✅ **Price Threshold**: 0.5% (updated!)

## Monitoring on Render

- **View Logs**: Dashboard → Your Service → Logs
- **Restart**: Dashboard → Manual Deploy → Deploy Latest
- **Suspend**: Dashboard → Settings → Suspend Service

## Free Tier Limits

- ✅ 750 hours/month (enough for 24/7)
- ✅ No credit card required
- ✅ Auto-restarts if crashes

## Troubleshooting

**Service keeps restarting?**
- Check logs for errors
- Verify environment variables are correct

**No notifications?**
- Check Telegram bot token is correct
- Verify you started chat with @Trade_stalker_010_bot

**Want to stop it?**
- Dashboard → Settings → Suspend Service

---

## Summary

1. Go to [render.com/dashboard](https://dashboard.render.com)
2. New → Background Worker
3. Upload your folder or connect Git
4. Add 4 environment variables
5. Deploy!

Your agent will run 24/7 for free! 🎉
