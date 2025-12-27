# Alpha Intelligence - Monorepo

AI-Powered Financial Intelligence Platform with Telegram Bot and Web App.

## 🏗️ Project Structure

```
stock-monitor-agent/
├── telegram-bot/     # Telegram bot
├── web/              # Next.js web app
├── api/              # FastAPI backend
├── shared/           # Shared Python code (analyzer, social intelligence)
├── migrations/       # Database migrations
└── config/           # Configuration files
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL (or Supabase account)
- Redis (or Upstash account)

### Development

**1. Telegram Bot:**
```bash
cd telegram-bot
python main.py
```

**2. FastAPI Backend:**
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

**3. Next.js Web App:**
```bash
cd web
npm install
npm run dev
```

Visit http://localhost:3000

## 🌐 Deployment

- **Frontend**: Vercel (auto-deploy from `main` branch)
- **Backend**: Railway (auto-deploy from `main` branch)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Upstash (Redis)

## 📚 Documentation

- [Web App Master Plan](./brain/webapp_master_plan.md)
- [Build Guide](./brain/webapp_build_guide.md)
- [Monorepo Plan](./brain/monorepo_build_plan.md)

## 🔑 Environment Variables

See `.env.example` files in each directory.

## 📝 License

MIT
