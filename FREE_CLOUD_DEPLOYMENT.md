# Free Cloud Deployment Guide

This guide covers **100% FREE** cloud deployment options for your stock monitoring agent.

## Best Free Options (Ranked)

### 🥇 Option 1: Oracle Cloud Free Tier (RECOMMENDED)

**Why it's best:**
- ✅ **Always Free** (not a trial)
- ✅ 2 AMD-based VMs (1/8 OCPU, 1 GB RAM each)
- ✅ No credit card required after trial
- ✅ No time limit
- ✅ 200 GB block storage

**Setup Steps:**

1. **Sign up**: Go to [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
   - Create account (requires credit card for verification, but won't be charged)
   - After trial ends, free tier continues forever

2. **Create VM Instance**:
   ```
   - Go to Compute → Instances → Create Instance
   - Choose: VM.Standard.E2.1.Micro (Always Free)
   - OS: Ubuntu 22.04
   - Download SSH key
   ```

3. **Connect to VM**:
   ```bash
   ssh -i your-key.pem ubuntu@<your-vm-ip>
   ```

4. **Install Python & Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git -y
   ```

5. **Upload Your Code**:
   ```bash
   # On your local machine
   cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent
   
   # Create a zip file
   zip -r stock-monitor.zip . -x "*.git*" -x "*__pycache__*" -x "*.db"
   
   # Upload to VM
   scp -i your-key.pem stock-monitor.zip ubuntu@<your-vm-ip>:~/
   
   # On VM, unzip
   ssh -i your-key.pem ubuntu@<your-vm-ip>
   unzip stock-monitor.zip
   cd stock-monitor-agent
   ```

6. **Configure & Run**:
   ```bash
   # Create .env file on VM
   nano .env
   # Paste your credentials
   
   # Install dependencies
   pip3 install -r requirements.txt
   
   # Run in background
   cd src
   nohup python3 main.py > ../monitor.log 2>&1 &
   ```

**Pros**: Most generous free tier, no time limit  
**Cons**: Requires credit card for signup (but won't charge)

---

### 🥈 Option 2: Google Cloud Free Tier

**What's Free:**
- ✅ e2-micro instance (1 vCPU, 1 GB RAM)
- ✅ 30 GB storage
- ✅ **Always Free** in US regions
- ✅ $300 credit for 90 days (bonus)

**Setup Steps:**

1. **Sign up**: [cloud.google.com/free](https://cloud.google.com/free)
   - Requires credit card (won't charge after free credit expires)
   - Free tier continues after trial

2. **Create VM**:
   ```
   - Go to Compute Engine → VM Instances
   - Create Instance
   - Machine type: e2-micro (free tier)
   - Region: us-west1, us-central1, or us-east1
   - Boot disk: Ubuntu 22.04 LTS
   ```

3. **Connect via SSH** (built-in browser SSH)

4. **Install & Deploy** (same as Oracle steps 4-6)

**Pros**: Easy to use, built-in SSH  
**Cons**: Requires credit card

---

### 🥉 Option 3: Render.com (Easiest, No Credit Card!)

**What's Free:**
- ✅ **No credit card required**
- ✅ 750 hours/month (enough for 24/7)
- ✅ Automatic deployment from GitHub
- ✅ Super easy setup

**Setup Steps:**

1. **Push code to GitHub** (if you have an account):
   ```bash
   cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent
   git init
   git add .
   git commit -m "Initial commit"
   # Create repo on GitHub, then:
   git remote add origin https://github.com/yourusername/stock-monitor.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Sign up (no credit card needed!)
   - New → Background Worker
   - Connect GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `cd src && python main.py`

3. **Add Environment Variables**:
   - In Render dashboard, go to Environment
   - Add your API keys from `.env` file

**Pros**: No credit card, easiest setup, auto-deploy  
**Cons**: Service sleeps after 15 min inactivity (but restarts automatically)

---

### 🏅 Option 4: Railway.app (No Credit Card!)

**What's Free:**
- ✅ **No credit card required**
- ✅ $5 free credit/month
- ✅ Enough for 24/7 operation
- ✅ Easy deployment

**Setup Steps:**

1. **Sign up**: [railway.app](https://railway.app)
   - No credit card needed
   - Free $5/month credit

2. **Deploy**:
   - New Project → Deploy from GitHub
   - Or: Empty Project → Add Service
   - Upload your code
   - Set environment variables

3. **Configure**:
   - Add `FINNHUB_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
   - Start command: `cd src && python main.py`

**Pros**: No credit card, generous free tier  
**Cons**: $5 credit might run out if very active

---

### 🎯 Option 5: Fly.io (No Credit Card!)

**What's Free:**
- ✅ **No credit card required**
- ✅ 3 shared-cpu VMs
- ✅ 160GB storage
- ✅ Always free

**Setup Steps:**

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up & Deploy**:
   ```bash
   cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent
   fly auth signup
   fly launch
   # Follow prompts
   ```

3. **Set secrets**:
   ```bash
   fly secrets set FINNHUB_API_KEY=your_key
   fly secrets set TELEGRAM_BOT_TOKEN=your_token
   fly secrets set TELEGRAM_CHAT_ID=your_chat_id
   ```

**Pros**: No credit card, CLI-based deployment  
**Cons**: Requires CLI installation

---

## My Recommendation

**For you, I recommend: Render.com** 🎯

**Why:**
1. ✅ **No credit card required** - Just sign up and deploy
2. ✅ **Easiest setup** - Connect GitHub and done
3. ✅ **Free forever** - 750 hours/month (more than enough)
4. ✅ **Auto-deploy** - Push to GitHub, auto-updates

**Quick Start with Render:**

```bash
# 1. Push to GitHub (if you have account)
cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent
git init
git add .
git commit -m "Stock monitor agent"

# 2. Go to render.com and sign up
# 3. New → Background Worker → Connect GitHub
# 4. Add environment variables
# 5. Deploy!
```

---

## Comparison Table

| Service | Credit Card? | Free Tier | Ease | Best For |
|---------|-------------|-----------|------|----------|
| **Render.com** | ❌ No | 750h/month | ⭐⭐⭐⭐⭐ | Beginners |
| **Railway.app** | ❌ No | $5/month | ⭐⭐⭐⭐ | Easy setup |
| **Fly.io** | ❌ No | 3 VMs | ⭐⭐⭐ | CLI users |
| **Oracle Cloud** | ✅ Yes | 2 VMs forever | ⭐⭐⭐ | Max resources |
| **Google Cloud** | ✅ Yes | e2-micro | ⭐⭐⭐⭐ | Google users |

---

## Step-by-Step: Render.com Deployment

Since this is the easiest, here's a detailed guide:

### 1. Prepare Your Code

```bash
cd /Users/nikhil/.gemini/antigravity/scratch/stock-monitor-agent

# Make sure .env is in .gitignore (it already is!)
# Create a simple start script
echo "cd src && python main.py" > start.sh
chmod +x start.sh
```

### 2. Create GitHub Repo (Optional)

If you don't have GitHub, you can upload files directly to Render.

### 3. Deploy on Render

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with email (no credit card!)
4. Click "New +" → "Background Worker"
5. Choose "Public Git repository" or "Upload files"
6. If uploading:
   - Upload your `stock-monitor-agent` folder
7. Configure:
   - **Name**: stock-monitor-agent
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd src && python main.py`
8. Add Environment Variables:
   - Click "Environment"
   - Add: `FINNHUB_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
9. Click "Create Background Worker"

**Done!** Your agent will start running 24/7 for free! 🎉

---

## Monitoring Your Deployed Agent

### Check Logs on Render

- Go to your service dashboard
- Click "Logs" tab
- See real-time output

### Test It's Working

- Wait 15 minutes
- You should receive a Telegram notification
- Check logs for "Monitoring cycle completed"

### Stop/Restart

- Render dashboard → "Manual Deploy" → "Suspend" or "Deploy"

---

## Troubleshooting

**Problem**: Service keeps restarting

**Solution**: Check logs for errors, verify environment variables

**Problem**: No notifications

**Solution**: Check Telegram credentials in environment variables

**Problem**: Out of free hours

**Solution**: Switch to Oracle Cloud (unlimited free tier)

---

## Summary

🎯 **Best choice**: Render.com (no credit card, easiest)  
🏆 **Most generous**: Oracle Cloud (unlimited, but needs credit card)  
⚡ **Fastest setup**: Railway.app (no credit card, $5/month credit)

All options are **100% free** and will run your agent 24/7!
