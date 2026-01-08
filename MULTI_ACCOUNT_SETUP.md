# Multi-Account Publishing Setup Guide

This system supports publishing Instagram Reels and Facebook videos to multiple accounts simultaneously.

## 📋 Table of Contents

1. [Account Configuration](#account-configuration)
2. [Environment Variables](#environment-variables)
3. [Publishing Options](#publishing-options)
4. [API Usage](#api-usage)
5. [Adding New Accounts](#adding-new-accounts)

---

## Account Configuration

### Currently Configured Accounts

The system is pre-configured for two accounts:

1. **Gym College** (`gymcollege`)
   - Instagram Business Account: `17841468847801005`
   - Facebook Page: `421725951022067`
   
2. **Healthy College** (`healthycollege`)
   - Instagram Business Account: `17841479849607158`
   - Facebook Page: `944977965368075`

---

## Environment Variables

### Required Variables Per Account

Each account needs the following credentials in your `.env` file:

```bash
# Account Name: GYMCOLLEGE
GYMCOLLEGE_INSTAGRAM_ACCESS_TOKEN=your_token_here
GYMCOLLEGE_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841468847801005
GYMCOLLEGE_FACEBOOK_PAGE_ID=421725951022067
GYMCOLLEGE_FACEBOOK_ACCESS_TOKEN=your_token_here
GYMCOLLEGE_META_ACCESS_TOKEN=your_token_here

# Account Name: HEALTHYCOLLEGE
HEALTHYCOLLEGE_INSTAGRAM_ACCESS_TOKEN=your_token_here
HEALTHYCOLLEGE_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841479849607158
HEALTHYCOLLEGE_FACEBOOK_PAGE_ID=944977965368075
HEALTHYCOLLEGE_FACEBOOK_ACCESS_TOKEN=your_token_here
HEALTHYCOLLEGE_META_ACCESS_TOKEN=your_token_here
```

### Shared Configuration

These are shared across all accounts:

```bash
# Meta App Settings (shared)
INSTAGRAM_APP_ID=1533600021273075
INSTAGRAM_APP_SECRET=your_app_secret_here

# Public URL for serving media files
PUBLIC_URL_BASE=https://your-public-url.com
```

---

## Publishing Options

### 1. Publish to Single Account

Publish to just one account (e.g., Gym College):

```python
from app.services.multi_account_publisher import MultiAccountPublisher

publisher = MultiAccountPublisher()

result = publisher.publish_to_account(
    account_key="gymcollege",
    video_url="https://your-domain.com/videos/reel.mp4",
    caption="Check out this workout! 💪",
    thumbnail_url="https://your-domain.com/thumbnails/reel.png",
    publish_to_instagram=True,
    publish_to_facebook=True
)
```

### 2. Publish to All Accounts

Publish the same content to all configured accounts:

```python
result = publisher.publish_to_all_accounts(
    video_url="https://your-domain.com/videos/reel.mp4",
    caption="Check out this workout! 💪",
    thumbnail_url="https://your-domain.com/thumbnails/reel.png",
    publish_to_instagram=True,
    publish_to_facebook=True
)
```

### 3. Publish to Specific Accounts Only

Publish to a subset of accounts:

```python
result = publisher.publish_to_all_accounts(
    video_url="https://your-domain.com/videos/reel.mp4",
    caption="Check out this workout! 💪",
    account_filter=["gymcollege", "healthycollege"],  # Only these accounts
    publish_to_instagram=True,
    publish_to_facebook=True
)
```

### 4. Instagram Only or Facebook Only

```python
# Instagram only (all accounts)
result = publisher.publish_to_all_accounts(
    video_url="https://your-domain.com/videos/reel.mp4",
    caption="Instagram exclusive! 📸",
    publish_to_instagram=True,
    publish_to_facebook=False
)

# Facebook only (all accounts)
result = publisher.publish_to_all_accounts(
    video_url="https://your-domain.com/videos/reel.mp4",
    caption="Facebook exclusive! 📘",
    publish_to_instagram=False,
    publish_to_facebook=True
)
```

---

## API Usage

### Check Available Accounts

```bash
curl http://localhost:8000/accounts
```

Response:
```json
{
  "accounts": ["gymcollege", "healthycollege"],
  "total": 2
}
```

### Publish to Single Account (API Endpoint)

```bash
curl -X POST http://localhost:8000/reels/publish \
  -H "Content-Type: application/json" \
  -d '{
    "account_key": "gymcollege",
    "video_url": "https://your-domain.com/videos/reel.mp4",
    "caption": "Check this out!",
    "publish_to_instagram": true,
    "publish_to_facebook": true
  }'
```

### Publish to All Accounts (API Endpoint)

```bash
curl -X POST http://localhost:8000/reels/publish/all \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://your-domain.com/videos/reel.mp4",
    "caption": "Check this out!",
    "publish_to_instagram": true,
    "publish_to_facebook": true
  }'
```

---

## Adding New Accounts

### Step 1: Get Meta Credentials

1. Go to [Meta Developer Dashboard](https://developers.facebook.com/)
2. Select your app (App ID: `1533600021273075`)
3. Navigate to **Tools** → **Access Token Tool**
4. Select the new Instagram account or Facebook page
5. Generate an access token with the required permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_manage_posts`

### Step 2: Add to `.env`

Add credentials for the new account using a unique prefix:

```bash
# Example: Adding a third account "FITNESS_PRO"
FITNESSPRO_INSTAGRAM_ACCESS_TOKEN=your_new_token_here
FITNESSPRO_INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_account_id
FITNESSPRO_FACEBOOK_PAGE_ID=your_fb_page_id
FITNESSPRO_FACEBOOK_ACCESS_TOKEN=your_new_token_here
FITNESSPRO_META_ACCESS_TOKEN=your_new_token_here
```

### Step 3: Update `multi_account_publisher.py`

Add loading logic for the new account in the `_load_accounts()` method:

```python
# Load Fitness Pro account
fitnesspro_ig_token = os.getenv("FITNESSPRO_INSTAGRAM_ACCESS_TOKEN")
fitnesspro_ig_account = os.getenv("FITNESSPRO_INSTAGRAM_BUSINESS_ACCOUNT_ID")
fitnesspro_fb_token = os.getenv("FITNESSPRO_FACEBOOK_ACCESS_TOKEN")
fitnesspro_fb_page = os.getenv("FITNESSPRO_FACEBOOK_PAGE_ID")
fitnesspro_meta_token = os.getenv("FITNESSPRO_META_ACCESS_TOKEN")

if all([fitnesspro_ig_token, fitnesspro_ig_account, fitnesspro_fb_token, fitnesspro_fb_page]):
    self.accounts["fitnesspro"] = AccountCredentials(
        account_name="Fitness Pro",
        instagram_access_token=fitnesspro_ig_token,
        instagram_business_account_id=fitnesspro_ig_account,
        facebook_access_token=fitnesspro_fb_token,
        facebook_page_id=fitnesspro_fb_page,
        meta_access_token=fitnesspro_meta_token or fitnesspro_ig_token
    )
    print(f"✅ Loaded Fitness Pro account (IG: {fitnesspro_ig_account}, FB: {fitnesspro_fb_page})")
```

### Step 4: Restart Server

```bash
./run_local.sh
```

You should see:
```
✅ Loaded Gym College account (IG: 17841468847801005, FB: 421725951022067)
✅ Loaded Healthy College account (IG: 17841479849607158, FB: 944977965368075)
✅ Loaded Fitness Pro account (IG: your_new_id, FB: your_new_page_id)
📊 Total accounts configured: 3
```

---

## Response Format

### Single Account Response

```json
{
  "success": true,
  "account": "gymcollege",
  "account_name": "Gym College",
  "results": {
    "instagram": {
      "success": true,
      "platform": "instagram",
      "post_id": "17841468847801005_123456"
    },
    "facebook": {
      "success": true,
      "platform": "facebook",
      "post_id": "421725951022067_789012"
    }
  }
}
```

### All Accounts Response

```json
{
  "success": true,
  "total_accounts": 2,
  "success_count": 2,
  "failure_count": 0,
  "results": {
    "gymcollege": {
      "success": true,
      "account": "gymcollege",
      "account_name": "Gym College",
      "results": {
        "instagram": { "success": true, "post_id": "..." },
        "facebook": { "success": true, "post_id": "..." }
      }
    },
    "healthycollege": {
      "success": true,
      "account": "healthycollege",
      "account_name": "Healthy College",
      "results": {
        "instagram": { "success": true, "post_id": "..." },
        "facebook": { "success": true, "post_id": "..." }
      }
    }
  }
}
```

---

## Troubleshooting

### Account Not Loading

Check server logs on startup:
```
✅ Loaded Gym College account (IG: 17841468847801005, FB: 421725951022067)
⚠️  Warning: Healthy College account credentials incomplete
```

If you see a warning, check that ALL required environment variables are set for that account.

### Publishing Fails for One Account

The system is designed to continue even if one account fails. Check the response:

```json
{
  "success": true,  // At least one account succeeded
  "success_count": 1,
  "failure_count": 1,
  "results": {
    "gymcollege": {
      "success": true,
      "results": { "instagram": { "success": true } }
    },
    "healthycollege": {
      "success": false,
      "results": { 
        "instagram": { 
          "success": false, 
          "error": "Token expired" 
        } 
      }
    }
  }
}
```

### Token Expiration

Instagram/Facebook tokens expire after 60-90 days. To refresh:

1. Go to [Meta Access Token Tool](https://developers.facebook.com/tools/accesstoken/)
2. Generate a new token for the affected account
3. Update the `.env` file with the new token
4. Restart the server

---

## Best Practices

1. **Always configure both Instagram AND Facebook** - Even if you only use one platform, having both configured ensures future flexibility

2. **Use descriptive account keys** - Use lowercase, no spaces (e.g., `gymcollege`, `healthycollege`, `fitnesspro`)

3. **Test individually first** - When adding a new account, test it individually before including it in "publish to all"

4. **Monitor token expiration** - Set reminders to refresh tokens every 60 days

5. **Keep `.env` secure** - Never commit `.env` to git. Use Railway/Vercel environment variables for production

6. **Use account filters for specific campaigns** - If a campaign is only relevant to certain accounts, use `account_filter`

---

## Future Scaling to 10+ Accounts

The current system is designed to scale. To support 10 accounts:

1. Add credentials to `.env` with unique prefixes
2. Add loading logic in `_load_accounts()`
3. Server automatically detects all configured accounts
4. Use `publish_to_all_accounts()` to publish to all at once

**Alternatively**, consider creating a JSON configuration file:

```json
{
  "accounts": [
    {
      "key": "gymcollege",
      "name": "Gym College",
      "instagram_token": "...",
      "instagram_account_id": "...",
      "facebook_token": "...",
      "facebook_page_id": "..."
    },
    // ... 9 more accounts
  ]
}
```

And load from JSON instead of environment variables for easier management.
