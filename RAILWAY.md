# Railway Deployment Guide for Multi-User Reels Automation

## 🚀 Quick Deploy to Railway.app

### Step 1: Create Railway Account
1. Go to https://railway.app/
2. Sign up with GitHub
3. Connect your GitHub account

### Step 2: Deploy from GitHub Repository

#### Option A: Deploy via Railway Dashboard

1. **Push your code to GitHub** (if not already):
   ```bash
   cd /Users/filipepeixoto/Documents/Priv/Gym\ College/automation/reels-automation
   git init
   git add .
   git commit -m "Initial commit - Multi-user reels automation"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/reels-automation.git
   git push -u origin main
   ```

2. **In Railway Dashboard**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `reels-automation` repository
   - Railway will auto-detect the Dockerfile

3. **Add PostgreSQL Database**:
   - In your project, click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway automatically sets `DATABASE_URL` environment variable

### Step 3: Configure Environment Variables

Click on your service → "Variables" tab:

```env
# Required: Your Meta/Instagram credentials
META_ACCESS_TOKEN=your_meta_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id
FACEBOOK_PAGE_ID=your_facebook_page_id

# Railway provides this automatically, but you can override:
# PUBLIC_URL_BASE=https://your-app.railway.app

# Optional: Port (Railway sets this automatically)
# PORT=8000
```

**Important**: Railway automatically connects your PostgreSQL database via `DATABASE_URL`.

### Step 4: Deploy and Get URL

1. Railway starts building your Docker image
2. After ~2-3 minutes, you'll get a public URL
3. Click "Settings" → "Generate Domain" to get: `https://your-app.railway.app`

### Step 5: Initialize Users

Access your deployment at `https://your-app.railway.app` and create users via API:

```bash
# User 1 (You)
curl -X POST https://your-app.railway.app/reels/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1@example.com",
    "user_name": "Your Name",
    "email": "user1@example.com",
    "instagram_business_account_id": "your_instagram_id",
    "facebook_page_id": "your_facebook_id",
    "meta_access_token": "your_token"
  }'

# User 2 (Your Friend)
curl -X POST https://your-app.railway.app/reels/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "friend@example.com",
    "user_name": "Friend Name",
    "email": "friend@example.com",
    "instagram_business_account_id": "friend_instagram_id",
    "facebook_page_id": "friend_facebook_id",
    "meta_access_token": "friend_token"
  }'
```

---

## 📊 Database Schema

PostgreSQL database includes two tables:

### `scheduled_reels`
- **schedule_id**: Unique schedule identifier
- **user_id**: User who scheduled the post
- **reel_id**: Generated reel identifier
- **scheduled_time**: When to publish (UTC)
- **status**: "scheduled", "published", or "failed"
- **metadata**: JSON with platforms, file paths

### `user_profiles`
- **user_id**: Unique user identifier (email)
- **user_name**: Display name
- **instagram_business_account_id**: Instagram credentials
- **facebook_page_id**: Facebook credentials
- **meta_access_token**: Meta API token

---

## 🧑‍🤝‍🧑 Multi-User Usage

### Scheduling Posts (with user context)

When scheduling, include `user_id`:

```bash
curl -X POST https://your-app.railway.app/reels/publish \
  -H "Content-Type: application/json" \
  -d '{
    "reel_id": "abc123",
    "user_id": "user1@example.com",
    "caption": "My awesome reel!",
    "platforms": ["instagram", "facebook"],
    "schedule_date": "2026-01-15",
    "schedule_time": "14:00"
  }'
```

### View Your Scheduled Posts

```bash
# All posts for specific user
curl https://your-app.railway.app/reels/scheduled?user_id=user1@example.com

# All posts (admin view)
curl https://your-app.railway.app/reels/scheduled
```

### Delete Your Posts

```bash
curl -X DELETE https://your-app.railway.app/reels/scheduled/{schedule_id}?user_id=user1@example.com
```

---

## 🔐 Security Considerations

### Current Setup (2 trusted users)
- No authentication required
- Users identified by `user_id` parameter
- Suitable for 2 friends sharing the system

### Future: Add Authentication (if scaling)

If you add more users, implement API key auth:

```python
# In routes.py
from fastapi import Header, HTTPException

async def verify_user(x_user_id: str = Header(...)):
    # Verify user exists in database
    with get_db_session() as db:
        user = db.query(UserProfile).filter(
            UserProfile.user_id == x_user_id
        ).first()
        if not user:
            raise HTTPException(401, "Invalid user")
    return x_user_id

# Then in routes:
@router.post("/publish")
async def publish(
    request: PublishRequest,
    user_id: str = Depends(verify_user)
):
    # Use verified user_id
```

---

## 🔧 Local Development with PostgreSQL

### Use Docker Compose locally:

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: reels_automation
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run locally:
```bash
docker-compose up -d
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/reels_automation"
python -m uvicorn app.main:app --reload
```

---

## 📈 Monitoring

### Railway Metrics
- Go to your project → "Metrics"
- View CPU, Memory, Network usage
- See deployment logs in real-time

### Database Size
```bash
# Check database size
curl https://your-app.railway.app/reels/health

# Shows:
# - Total scheduled posts
# - Active users
# - Database connection status
```

---

## 💰 Costs

### Railway Free Tier
- **$5 free credit** (trial)
- **500 hours/month** execution time
- **8GB RAM** max
- **100GB bandwidth**

### After Trial
- **$5/month** for Hobby plan
- Includes PostgreSQL database
- Unlimited projects

**For 2 users with moderate usage**: Free tier should cover you! 🎉

---

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Check Railway logs
# In project → Select service → "Logs"

# Should see:
✅ Connected to PostgreSQL database
✅ Database tables created/verified
```

### Migration Issues
```bash
# If database schema changes, Railway auto-rebuilds
# Tables are created on startup via init_db()

# Manual table recreation (if needed):
# Access Railway PostgreSQL shell:
# Project → PostgreSQL → "Data" → "Query"
DROP TABLE IF EXISTS scheduled_reels;
DROP TABLE IF EXISTS user_profiles;
# Then redeploy
```

### Auto-Publish Not Working
```bash
# Check scheduler logs:
⏰ Starting auto-publishing scheduler...
✅ Auto-publishing scheduler started (checks every 60 seconds)

# If missing, restart deployment:
# Railway dashboard → Service → "Deploy" → "Redeploy"
```

---

## ✅ Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Railway project from GitHub repo
- [ ] Add PostgreSQL database to project
- [ ] Set environment variables (META_ACCESS_TOKEN, etc.)
- [ ] Generate public domain
- [ ] Create user profiles via API
- [ ] Test scheduling a post
- [ ] Verify auto-publish in logs
- [ ] Share URL with your friend

---

## 🎉 You're Live!

Your multi-user reels automation is now running 24/7 on Railway with PostgreSQL!

- **Web UI**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`
- **Scheduled Posts**: `https://your-app.railway.app/scheduled`

Both you and your friend can schedule posts independently using your own Instagram/Facebook credentials! 🚀
