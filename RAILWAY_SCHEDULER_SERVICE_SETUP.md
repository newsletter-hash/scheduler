# Railway Scheduler Service Setup Guide

## Problem Identified
Your environment variables are currently on the **Postgres database service**, but your FastAPI web app needs its own **Scheduler service** to run.

## Solution: Create Railway Scheduler Service

### Step 1: Create New Service in Railway
1. Go to Railway dashboard: https://railway.app/project/e7cab23c-c06d-4ffd-9b5f-23168118b692
2. Click **"+ New"** button in the top right
3. Select **"GitHub Repo"**
4. Choose your repository (or use "Empty Service" if you want to configure later)
5. Name it: **"Scheduler"**

### Step 2: Configure the Service
1. In the Scheduler service settings:
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Build Command**: (leave empty or use `pip install -r requirements.txt`)
   - **Root Directory**: (leave as `/`)

2. Add a **Public Domain**:
   - Settings > Networking > Generate Domain
   - Should create: `scheduler-production-cd0b.up.railway.app` (or similar)

### Step 3: Add Environment Variables
You have two options:

#### Option A: Manual (Recommended - avoids rate limits)
Go to Scheduler service > Variables tab, and add these one by one:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# App Settings
APP_ENV=development
API_HOST=127.0.0.1
API_PORT=8000

# Meta App (shared)
INSTAGRAM_APP_ID=1533600021273075
INSTAGRAM_APP_SECRET=25d65d1962784567128e037600c8314b

# Gym College
GYMCOLLEGE_INSTAGRAM_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB
GYMCOLLEGE_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841468847801005
GYMCOLLEGE_FACEBOOK_PAGE_ID=421725951022067
GYMCOLLEGE_FACEBOOK_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB
GYMCOLLEGE_META_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB

# Healthy College
HEALTHYCOLLEGE_INSTAGRAM_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB
HEALTHYCOLLEGE_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841479849607158
HEALTHYCOLLEGE_FACEBOOK_PAGE_ID=944977965368075
HEALTHYCOLLEGE_FACEBOOK_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB
HEALTHYCOLLEGE_META_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB

# Legacy/Fallback
INSTAGRAM_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841468847801005
META_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB
FACEBOOK_PAGE_ID=421725951022067
FACEBOOK_ACCESS_TOKEN=EAANSOCguXOABQZAmZAZC7ocFK2xzzpsBTRBpcU24KHcH1s9iowJRcVtQTgGBLZB2PqUr9Rev1pBlLInzDGKT3r7GDVXbZAL6UZC0u9gb8ZCXlorTnJBCNAlgb16EZBNO9vT8UsLZBE0P0WAbAw4eDjGQY1fgKZCSZBszWL0X8aQWbOqPKNUmB6H3ZCDz3gVavZCvGr6GYEsChlVHdfgcZAy65JDlH280fao2Pvm3rcnUvYWUVZB

# Database Connection (reference to Postgres service)
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**Note**: The `DATABASE_URL` uses Railway's service referencing syntax to connect to your Postgres database.

#### Option B: CLI (after waiting for rate limit cooldown)
After Railway rate limit resets (usually 5-10 minutes), run:
```bash
./railway_sync_scheduler.sh
```
And make sure to select **"Scheduler"** service (not Postgres).

### Step 4: Deploy
Once variables are set, Railway will automatically deploy your app. Check:
- Logs tab for any errors
- Deployments tab to see build/deploy status
- Public URL (e.g., `scheduler-production-cd0b.up.railway.app`)

### Step 5: Test Publishing
1. Visit: https://scheduler-production-cd0b.up.railway.app/scheduled
2. Click "Retry" on your failed post
3. Should successfully publish to both Instagram and Facebook!

## Quick Check
After setup, verify:
```bash
railway service  # Should show "Scheduler"
railway variables  # Should show all your tokens
railway logs  # Should show FastAPI startup logs
```

## Troubleshooting
If publish still fails:
1. Check Railway logs: `railway logs`
2. Look for "Instagram credentials loaded" messages
3. Verify public domain is accessible: `curl https://scheduler-production-cd0b.up.railway.app`
