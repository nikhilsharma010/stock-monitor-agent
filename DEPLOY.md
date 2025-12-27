# Alpha Intelligence - Quick Deployment Guide

## 🚀 Deploy in 3 Steps

### Step 1: Deploy Backend to Railway (5 minutes)

1. **Go to Railway**: https://railway.app
2. **Sign in** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `stock-monitor-agent`
5. **Add PostgreSQL**:
   - Click "New" → "Database" → "PostgreSQL"
   - Copy the `DATABASE_URL`
6. **Configure Service**:
   - Root Directory: `api`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. **Add Environment Variables**:
   ```
   DATABASE_URL=<from PostgreSQL>
   GROQ_API_KEY=<your key>
   FINNHUB_API_KEY=<your key>
   ```
8. **Deploy** and copy the public URL

---

### Step 2: Deploy Frontend to Vercel (3 minutes)

1. **Go to Vercel**: https://vercel.com
2. **Sign in** with GitHub
3. **Import Project**: `stock-monitor-agent`
4. **Configure**:
   - Framework: Next.js
   - Root Directory: `web`
5. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=<Railway backend URL>
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<your Clerk key>
   CLERK_SECRET_KEY=<your Clerk secret>
   ```
6. **Deploy**

---

### Step 3: Update Clerk (2 minutes)

1. **Clerk Dashboard** → **Domains**
2. **Add** your Vercel URL
3. **Update redirect URLs**:
   - After sign-in: `https://your-app.vercel.app/dashboard`

---

## ✅ Done!

Your app is live! 🎉

**Test it:**
- Visit your Vercel URL
- Sign up
- Try stock search
- Create a goal

---

## 🆘 Need Help?

Check `production_deployment_guide.md` for detailed instructions.
