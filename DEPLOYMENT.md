# Free 24/7 Deployment Guide

Since scheduled posts need the server running 24/7 to auto-publish, here are **FREE** cloud hosting options (no need to keep your PC on).

---

## 🚀 Option 1: Railway.app (RECOMMENDED)

**Free tier:** 500 hours/month ($5 credit) + $5/month after trial  
**Pros:** Easiest setup, auto-deploys from GitHub, free PostgreSQL  
**Cons:** Requires credit card after free trial

### Steps:

1. **Create account**: https://railway.app/
2. **Create new project** → "Deploy from GitHub repo"
3. **Connect your GitHub repo** (or push code to GitHub first)
4. **Add environment variables**:
   ```
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_id
   FACEBOOK_PAGE_ID=your_id
   META_ACCESS_TOKEN=your_token
   PUBLIC_URL_BASE=https://your-app.railway.app
   ```
5. **Deploy** - Railway auto-detects Python and runs `uvicorn`
6. **Get public URL**: Railway provides a free `.railway.app` domain

**Custom domain (optional):**
- Railway supports custom domains for free
- Add your domain in project settings

---

## 🌐 Option 2: Render.com

**Free tier:** Unlimited (but sleeps after 15min inactivity)  
**Pros:** No credit card required, easy setup  
**Cons:** Cold starts (15-30 sec delay when sleeping)

### Steps:

1. **Create account**: https://render.com/
2. **New Web Service** → Connect GitHub repo
3. **Configure build**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. **Add environment variables** (same as above)
5. **Deploy** - Free instance spins up

**Keep alive hack** (prevent sleeping):
```bash
# Add to cron job or use UptimeRobot.com to ping every 5 minutes
curl https://your-app.onrender.com/reels/health
```

---

## ☁️ Option 3: Fly.io

**Free tier:** 3 shared VMs, 160GB transfer/month  
**Pros:** Fully free, no sleep  
**Cons:** Requires Dockerfile, more technical

### Steps:

1. **Install flyctl**: https://fly.io/docs/hands-on/install-flyctl/
   ```bash
   brew install flyctl  # macOS
   ```

2. **Login and launch**:
   ```bash
   fly auth login
   fly launch
   ```

3. **Create Dockerfile** (in project root):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8080
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

5. **Set secrets**:
   ```bash
   fly secrets set INSTAGRAM_BUSINESS_ACCOUNT_ID=your_id
   fly secrets set FACEBOOK_PAGE_ID=your_id
   fly secrets set META_ACCESS_TOKEN=your_token
   fly secrets set PUBLIC_URL_BASE=https://your-app.fly.dev
   ```

---

## 💰 Low-Cost Alternatives ($5/month)

If free tiers don't work:

### DigitalOcean App Platform
- **Cost:** $5/month  
- **Setup:** Connect GitHub, deploy  
- **URL:** https://www.digitalocean.com/products/app-platform

### Linode
- **Cost:** $5/month (Nanode 1GB)  
- **Setup:** Deploy from marketplace  
- **URL:** https://www.linode.com/

---

## 🔧 What You Need to Change

### 1. Update `PUBLIC_URL_BASE` in `.env`

Currently you have:
```env
PUBLIC_URL_BASE=https://cool-paths-nail.loca.lt
```

Change to your cloud URL:
```env
PUBLIC_URL_BASE=https://your-app.railway.app
# or
PUBLIC_URL_BASE=https://your-app.onrender.com
# or
PUBLIC_URL_BASE=https://your-app.fly.dev
```

### 2. Update Meta Webhook URLs

If using webhooks, update callback URLs in Meta Developer Console:
- Old: `https://cool-paths-nail.loca.lt/webhook`
- New: `https://your-app.railway.app/webhook`

### 3. Test Auto-Publishing

After deployment:

1. **Schedule a test post** (2 minutes from now):
   ```bash
   # From main UI, schedule a reel for current time + 2 minutes
   ```

2. **Check logs**:
   - Railway: Project → "Logs" tab
   - Render: Dashboard → "Logs"
   - Fly.io: `fly logs`

3. **Verify auto-publish**:
   ```
   ⏰ Starting auto-publishing scheduler...
   ✅ Auto-publishing scheduler started (checks every 60 seconds)
   📅 Found 1 post(s) ready to publish at 2026-01-08 14:02:15
   📤 Publishing abc123 to instagram, facebook...
   ✅ Successfully published abc123
   ```

---

## 📊 Monitoring Scheduled Posts

### CLI Check (works remotely):
```bash
# If deployed, replace localhost with your cloud URL
curl https://your-app.railway.app/reels/scheduled | jq
```

### Web Dashboard:
```
https://your-app.railway.app/scheduled
```

### CLI Tool (local only):
```bash
python check_scheduled.py
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Use cloud environment variables
2. **Use HTTPS** - All cloud providers give free SSL
3. **Restrict CORS** in `app/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],  # Not "*"
       allow_credentials=True,
       allow_methods=["GET", "POST", "DELETE"],
       allow_headers=["*"],
   )
   ```

4. **Add API key authentication** (optional):
   ```python
   from fastapi import Header, HTTPException
   
   async def verify_api_key(x_api_key: str = Header(...)):
       if x_api_key != os.getenv("API_KEY"):
           raise HTTPException(401, "Invalid API key")
   
   @router.post("/reels/publish", dependencies=[Depends(verify_api_key)])
   ```

---

## 🆘 Troubleshooting

### Posts not auto-publishing?
```bash
# Check scheduler logs
# Should see: "Found X post(s) ready to publish"
# If not, check:
# 1. Server time is correct (UTC vs local)
# 2. scheduled.json has pending posts
# 3. APScheduler is running
```

### Cold starts on Render?
```bash
# Use UptimeRobot to ping every 5 minutes:
# https://uptimerobot.com/ (free)
# Add monitor: https://your-app.onrender.com/reels/health
```

### Out of Railway credits?
```bash
# Check usage: https://railway.app/account/usage
# Upgrade to $5/month or switch to Render
```

---

## 📝 Deployment Checklist

- [ ] Push code to GitHub
- [ ] Sign up for cloud platform (Railway/Render/Fly.io)
- [ ] Deploy from GitHub repo
- [ ] Add environment variables (META tokens, IDs)
- [ ] Update `PUBLIC_URL_BASE` to cloud URL
- [ ] Test health endpoint: `https://your-app.railway.app/reels/health`
- [ ] Schedule test post (2 minutes from now)
- [ ] Monitor logs for auto-publish confirmation
- [ ] Update Meta webhook URLs (if applicable)
- [ ] Set up monitoring (optional: UptimeRobot)

---

## ✅ You're All Set!

Your server is now running 24/7 in the cloud, checking every minute for scheduled posts and auto-publishing them. No need to keep your PC on! 🎉

**Next steps:**
- Schedule posts from web UI: `https://your-app.railway.app`
- Monitor schedules: `https://your-app.railway.app/scheduled`
- Delete schedules: Click "🗑️ Delete Schedule" button in dashboard
