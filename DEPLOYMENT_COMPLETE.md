# ✅ Railway Deployment Ready! 

## What Was Done

### 1. **PostgreSQL Database Integration** 🗄️
- **Models Created** ([app/models.py](app/models.py)):
  * `ScheduledReel`: Stores scheduled posts with user attribution
  * `UserProfile`: Stores user credentials (Instagram/Facebook)
  
- **Database Connection** ([app/db_connection.py](app/db_connection.py)):
  * PostgreSQL for production (Railway)
  * SQLite fallback for local development
  * Auto-creates tables on startup
  
- **Multi-User Scheduler** ([app/services/db_scheduler.py](app/services/db_scheduler.py)):
  * Schedule posts per user
  * Each user has own Instagram/Facebook credentials
  * Auto-publishing uses correct credentials per user

### 2. **Railway Deployment Files** 📦
- **Dockerfile**: Production-ready Python 3.11 container
- **railway.json**: Railway configuration (auto-deploy)
- **docker-compose.yml**: Local PostgreSQL for testing
- **.dockerignore**: Optimized Docker builds

### 3. **Multi-User API Endpoints** 👥
```bash
# Create/Update User
POST /reels/users
{
  "user_id": "user@example.com",
  "user_name": "John Doe",
  "instagram_business_account_id": "123456",
  "meta_access_token": "token_here"
}

# Schedule Reel (with user context)
POST /reels/publish
{
  "reel_id": "abc123",
  "user_id": "user@example.com",  # NEW!
  "user_name": "John Doe",        # NEW!
  "caption": "My reel!",
  "platforms": ["instagram", "facebook"],
  "schedule_date": "2026-01-15",
  "schedule_time": "14:00"
}

# Get Scheduled Posts (filtered by user)
GET /reels/scheduled?user_id=user@example.com

# Delete Scheduled Post (with user check)
DELETE /reels/scheduled/{schedule_id}?user_id=user@example.com
```

### 4. **Auto-Publishing Worker** ⏰
- **Background Scheduler**: Checks every 60 seconds
- **User-Specific Publishing**: Uses correct credentials per user
- **Status Tracking**: Updates to "published" or "failed"
- **Error Handling**: Stores error messages in database

---

## 🚀 How to Deploy to Railway

### Step 1: Push to GitHub

```bash
cd /Users/filipepeixoto/Documents/Priv/Gym\ College/automation/reels-automation

# Initialize git (if not done)
git init
git add .
git commit -m "Multi-user reels automation with PostgreSQL"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/reels-automation.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `reels-automation` repository
5. Railway auto-detects Dockerfile and builds

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL` environment variable

### Step 4: Set Environment Variables

Click your service → "Variables" tab:

```env
# Optional: Your default Meta credentials (for backward compatibility)
META_ACCESS_TOKEN=your_default_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_default_id
FACEBOOK_PAGE_ID=your_default_page_id

# Railway auto-sets these:
# DATABASE_URL=postgresql://... (from PostgreSQL service)
# PORT=8000 (Railway default)
```

**Note**: Users will have their own credentials in the database, so default credentials are optional.

### Step 5: Get Your Public URL

1. Click "Settings" → "Generate Domain"
2. You'll get: `https://your-app.railway.app`
3. Update your `.env` locally:
   ```env
   PUBLIC_URL_BASE=https://your-app.railway.app
   ```

---

## 👥 Setting Up Users

### Create User 1 (You)

```bash
curl -X POST https://your-app.railway.app/reels/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "yourname@email.com",
    "user_name": "Your Name",
    "email": "yourname@email.com",
    "instagram_business_account_id": "YOUR_INSTAGRAM_ID",
    "facebook_page_id": "YOUR_FACEBOOK_PAGE_ID",
    "meta_access_token": "YOUR_META_TOKEN"
  }'
```

### Create User 2 (Your Friend)

```bash
curl -X POST https://your-app.railway.app/reels/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "friend@email.com",
    "user_name": "Friend Name",
    "email": "friend@email.com",
    "instagram_business_account_id": "FRIEND_INSTAGRAM_ID",
    "facebook_page_id": "FRIEND_FACEBOOK_PAGE_ID",
    "meta_access_token": "FRIEND_META_TOKEN"
  }'
```

---

## 🧪 Testing Locally (with PostgreSQL)

### Start Local PostgreSQL

```bash
docker-compose up -d
```

### Set Environment Variable

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/reels_automation"
```

### Run Server

```bash
python -m uvicorn app.main:app --reload
```

### Verify Database

```bash
# Check tables were created
docker exec -it reels_postgres psql -U postgres -d reels_automation -c "\dt"

# Should show:
# scheduled_reels
# user_profiles
```

---

## 📊 How It Works

### Scheduling Flow (Multi-User)

```
User 1 schedules post
     ↓
Web UI sends: POST /reels/publish
     {
       user_id: "user1@email.com",
       reel_id: "abc123",
       schedule_date: "2026-01-15",
       schedule_time: "14:00"
     }
     ↓
DatabaseSchedulerService.schedule_reel()
     ↓
Stores in PostgreSQL:
     {
       schedule_id: "xyz789",
       user_id: "user1@email.com",
       reel_id: "abc123",
       scheduled_time: "2026-01-15 14:00:00+00",
       status: "scheduled",
       extra_data: {platforms: ["instagram", "facebook"]}
     }
```

### Auto-Publishing Flow

```
Every 60 seconds:
     ↓
Background worker checks:
     SELECT * FROM scheduled_reels
     WHERE status = 'scheduled'
     AND scheduled_time <= NOW()
     ↓
Found post for user1@email.com
     ↓
Look up user1's credentials from user_profiles table
     ↓
Publish using user1's Instagram/Facebook tokens
     ↓
Update status to "published" or "failed"
```

---

## 💰 Cost

### Railway Free Tier
- **$5 free credit** (trial)
- **500 hours/month** execution time
- **PostgreSQL included**

### After Trial
- **$5/month** Hobby plan
- Unlimited PostgreSQL storage (up to 1GB free)
- Perfect for 2 users! 🎉

---

## 📁 File Structure

```
reels-automation/
├── Dockerfile                   # Production container
├── railway.json                 # Railway config
├── docker-compose.yml           # Local PostgreSQL
├── requirements.txt             # Updated with SQLAlchemy, psycopg2
├── README.md                    # Project overview
├── RAILWAY.md                   # Detailed deployment guide
├── DEPLOYMENT_COMPLETE.md       # This file!
│
├── app/
│   ├── models.py                # NEW: PostgreSQL models
│   ├── db_connection.py         # NEW: Database connection
│   ├── main.py                  # UPDATED: Init database on startup
│   │
│   ├── services/
│   │   ├── db_scheduler.py      # NEW: Multi-user scheduler
│   │   └── scheduler.py         # OLD: JSON-based (kept for reference)
│   │
│   └── api/
│       └── routes.py            # UPDATED: User endpoints added
```

---

## 🆘 Troubleshooting

### Database Connection Issues

**Symptoms**: `DATABASE_URL not found`  
**Solution**: Railway auto-sets this when you add PostgreSQL service. Check "Variables" tab.

### Auto-Publish Not Working

**Symptoms**: Posts stay "scheduled"  
**Solution**: Check Railway logs:
```
Project → Service → Logs

Should see:
⏰ Starting auto-publishing scheduler...
✅ Auto-publishing scheduler started (checks every 60 seconds)
```

### User Credentials Not Working

**Symptoms**: Publishing fails with 401/403  
**Solution**: Verify user credentials in database:
```bash
# Get user info (without tokens)
curl https://your-app.railway.app/reels/users/user@example.com

# Should show:
{
  "user_id": "user@example.com",
  "has_instagram": true,
  "has_facebook": true
}
```

---

## ✅ Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Environment variables set (if using defaults)
- [ ] Public domain generated
- [ ] User 1 created via API
- [ ] User 2 created via API
- [ ] Test schedule created
- [ ] Auto-publish verified in logs

---

## 🎉 You're Ready!

Your **multi-user reels automation** is ready to deploy on Railway with:

✅ PostgreSQL database (shared between users)  
✅ Individual user credentials (Instagram/Facebook)  
✅ Auto-publishing background worker (24/7)  
✅ Docker containerization (production-ready)  
✅ Free hosting (500 hrs/month)  

**Next Steps:**
1. Push to GitHub
2. Deploy on Railway
3. Add PostgreSQL
4. Create users
5. Start scheduling! 🚀

---

See [RAILWAY.md](RAILWAY.md) for detailed step-by-step deployment instructions.
