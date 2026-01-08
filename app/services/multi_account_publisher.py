"""
Multi-account social media publisher for Instagram and Facebook Reels.
Supports publishing to multiple accounts simultaneously.
"""
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from app.services.social_publisher import SocialPublisher


@dataclass
class AccountCredentials:
    """Credentials for a single social media account."""
    account_name: str
    instagram_access_token: str
    instagram_business_account_id: str
    facebook_access_token: str
    facebook_page_id: str
    meta_access_token: str


class MultiAccountPublisher:
    """Service for publishing Reels to multiple Instagram and Facebook accounts."""
    
    def __init__(self):
        """Initialize the multi-account publisher with all configured accounts."""
        self.accounts: Dict[str, AccountCredentials] = {}
        self._load_accounts()
    
    def _load_accounts(self):
        """Load all account credentials from environment variables."""
        # Load Gym College account
        gymcollege_ig_token = os.getenv("GYMCOLLEGE_INSTAGRAM_ACCESS_TOKEN")
        gymcollege_ig_account = os.getenv("GYMCOLLEGE_INSTAGRAM_BUSINESS_ACCOUNT_ID")
        gymcollege_fb_token = os.getenv("GYMCOLLEGE_FACEBOOK_ACCESS_TOKEN")
        gymcollege_fb_page = os.getenv("GYMCOLLEGE_FACEBOOK_PAGE_ID")
        gymcollege_meta_token = os.getenv("GYMCOLLEGE_META_ACCESS_TOKEN")
        
        if all([gymcollege_ig_token, gymcollege_ig_account, gymcollege_fb_token, gymcollege_fb_page]):
            self.accounts["gymcollege"] = AccountCredentials(
                account_name="Gym College",
                instagram_access_token=gymcollege_ig_token,
                instagram_business_account_id=gymcollege_ig_account,
                facebook_access_token=gymcollege_fb_token,
                facebook_page_id=gymcollege_fb_page,
                meta_access_token=gymcollege_meta_token or gymcollege_ig_token
            )
            print(f"✅ Loaded Gym College account (IG: {gymcollege_ig_account}, FB: {gymcollege_fb_page})")
        else:
            print("⚠️  Warning: Gym College account credentials incomplete")
        
        # Load Healthy College account
        healthycollege_ig_token = os.getenv("HEALTHYCOLLEGE_INSTAGRAM_ACCESS_TOKEN")
        healthycollege_ig_account = os.getenv("HEALTHYCOLLEGE_INSTAGRAM_BUSINESS_ACCOUNT_ID")
        healthycollege_fb_token = os.getenv("HEALTHYCOLLEGE_FACEBOOK_ACCESS_TOKEN")
        healthycollege_fb_page = os.getenv("HEALTHYCOLLEGE_FACEBOOK_PAGE_ID")
        healthycollege_meta_token = os.getenv("HEALTHYCOLLEGE_META_ACCESS_TOKEN")
        
        if all([healthycollege_ig_token, healthycollege_ig_account, healthycollege_fb_token, healthycollege_fb_page]):
            self.accounts["healthycollege"] = AccountCredentials(
                account_name="Healthy College",
                instagram_access_token=healthycollege_ig_token,
                instagram_business_account_id=healthycollege_ig_account,
                facebook_access_token=healthycollege_fb_token,
                facebook_page_id=healthycollege_fb_page,
                meta_access_token=healthycollege_meta_token or healthycollege_ig_token
            )
            print(f"✅ Loaded Healthy College account (IG: {healthycollege_ig_account}, FB: {healthycollege_fb_page})")
        else:
            print("⚠️  Warning: Healthy College account credentials incomplete")
        
        # Load legacy fallback account (for backward compatibility)
        legacy_ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        legacy_ig_account = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        legacy_fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        legacy_fb_page = os.getenv("FACEBOOK_PAGE_ID")
        legacy_meta_token = os.getenv("META_ACCESS_TOKEN")
        
        # Only add legacy if it's not already covered by named accounts
        if all([legacy_ig_token, legacy_ig_account]) and legacy_ig_account not in [
            self.accounts.get("gymcollege", AccountCredentials("", "", "", "", "", "")).instagram_business_account_id,
            self.accounts.get("healthycollege", AccountCredentials("", "", "", "", "", "")).instagram_business_account_id
        ]:
            self.accounts["legacy"] = AccountCredentials(
                account_name="Legacy Account",
                instagram_access_token=legacy_ig_token,
                instagram_business_account_id=legacy_ig_account,
                facebook_access_token=legacy_fb_token or legacy_meta_token,
                facebook_page_id=legacy_fb_page or "",
                meta_access_token=legacy_meta_token or legacy_ig_token
            )
            print(f"✅ Loaded legacy account (IG: {legacy_ig_account})")
        
        if not self.accounts:
            print("⚠️  WARNING: No accounts configured! Publishing will fail.")
        else:
            print(f"📊 Total accounts configured: {len(self.accounts)}")
    
    def get_available_accounts(self) -> List[str]:
        """Get list of all configured account names."""
        return list(self.accounts.keys())
    
    def publish_to_account(
        self,
        account_key: str,
        video_url: str,
        caption: str = "CHANGE ME",
        thumbnail_url: Optional[str] = None,
        publish_to_instagram: bool = True,
        publish_to_facebook: bool = True
    ) -> Dict[str, Any]:
        """
        Publish to a specific account.
        
        Args:
            account_key: Account identifier (e.g., "gymcollege", "healthycollege")
            video_url: Public URL to the video file
            caption: Caption text
            thumbnail_url: Optional thumbnail URL
            publish_to_instagram: Whether to publish to Instagram
            publish_to_facebook: Whether to publish to Facebook
            
        Returns:
            Dict with publish results
        """
        if account_key not in self.accounts:
            return {
                "success": False,
                "error": f"Account '{account_key}' not found or not configured",
                "account": account_key
            }
        
        account = self.accounts[account_key]
        print(f"\n📤 Publishing to {account.account_name} ({account_key})...")
        
        # Create a temporary BrandConfig-like object
        class TempConfig:
            def __init__(self, creds: AccountCredentials):
                self.instagram_business_account_id = creds.instagram_business_account_id
                self.facebook_page_id = creds.facebook_page_id
                self.meta_access_token = creds.meta_access_token
        
        publisher = SocialPublisher(brand_config=TempConfig(account))
        
        results = {}
        
        if publish_to_instagram:
            print(f"   📸 Publishing to Instagram ({account.instagram_business_account_id})...")
            ig_result = publisher.publish_instagram_reel(video_url, caption, thumbnail_url)
            results["instagram"] = ig_result
            if ig_result.get("success"):
                print(f"   ✅ Instagram: {ig_result.get('post_id')}")
            else:
                print(f"   ❌ Instagram failed: {ig_result.get('error')}")
        
        if publish_to_facebook and account.facebook_page_id:
            print(f"   📘 Publishing to Facebook ({account.facebook_page_id})...")
            fb_result = publisher.publish_facebook_reel(video_url, caption, thumbnail_url)
            results["facebook"] = fb_result
            if fb_result.get("success"):
                print(f"   ✅ Facebook: {fb_result.get('post_id')}")
            else:
                print(f"   ❌ Facebook failed: {fb_result.get('error')}")
        
        # Determine overall success
        success = any(r.get("success", False) for r in results.values())
        
        return {
            "success": success,
            "account": account_key,
            "account_name": account.account_name,
            "results": results
        }
    
    def publish_to_all_accounts(
        self,
        video_url: str,
        caption: str = "CHANGE ME",
        thumbnail_url: Optional[str] = None,
        publish_to_instagram: bool = True,
        publish_to_facebook: bool = True,
        account_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Publish to all configured accounts (or filtered subset).
        
        Args:
            video_url: Public URL to the video file
            caption: Caption text
            thumbnail_url: Optional thumbnail URL
            publish_to_instagram: Whether to publish to Instagram
            publish_to_facebook: Whether to publish to Facebook
            account_filter: Optional list of account keys to publish to (e.g., ["gymcollege"])
            
        Returns:
            Dict with results from all accounts
        """
        print(f"\n🚀 Publishing to {len(self.accounts)} account(s)...")
        
        accounts_to_publish = account_filter if account_filter else list(self.accounts.keys())
        
        all_results = {}
        success_count = 0
        failure_count = 0
        
        for account_key in accounts_to_publish:
            if account_key not in self.accounts:
                print(f"⚠️  Skipping unknown account: {account_key}")
                continue
            
            result = self.publish_to_account(
                account_key=account_key,
                video_url=video_url,
                caption=caption,
                thumbnail_url=thumbnail_url,
                publish_to_instagram=publish_to_instagram,
                publish_to_facebook=publish_to_facebook
            )
            
            all_results[account_key] = result
            
            if result.get("success"):
                success_count += 1
            else:
                failure_count += 1
        
        overall_success = success_count > 0
        
        print(f"\n{'✅' if overall_success else '❌'} Publishing complete: {success_count} succeeded, {failure_count} failed")
        
        return {
            "success": overall_success,
            "total_accounts": len(accounts_to_publish),
            "success_count": success_count,
            "failure_count": failure_count,
            "results": all_results
        }
