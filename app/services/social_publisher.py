"""
Social media publisher for Instagram and Facebook Reels.
"""
import os
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.config import BrandConfig


class SocialPublisher:
    """Service for publishing Reels to Instagram and Facebook."""
    
    def __init__(self, brand_config: Optional[BrandConfig] = None):
        """
        Initialize the social publisher with Meta credentials.
        
        Args:
            brand_config: Optional brand configuration with specific credentials.
                         If not provided, uses default environment variables.
        """
        # Use brand-specific credentials if provided, otherwise fall back to defaults
        if brand_config:
            self.ig_business_account_id = brand_config.instagram_business_account_id
            self.fb_page_id = brand_config.facebook_page_id
            self.ig_access_token = brand_config.meta_access_token
            self.fb_access_token = brand_config.meta_access_token
        else:
            # Fallback to default environment variables
            self.ig_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
            self.ig_business_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
            self.fb_access_token = os.getenv("FACEBOOK_ACCESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
            self.fb_page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        self.api_version = "v19.0"
        
        if not self.ig_access_token:
            print("⚠️  Warning: Meta access token not found")
        if not self.ig_business_account_id:
            print("⚠️  Warning: INSTAGRAM_BUSINESS_ACCOUNT_ID not found")
    
    def publish_instagram_reel(
        self,
        video_url: str,
        caption: str = "CHANGE ME",
        thumbnail_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a Reel to Instagram using the two-step process.
        
        Args:
            video_url: Public URL to the video file (must be accessible)
            caption: Caption text for the reel
            thumbnail_url: Optional thumbnail URL
            
        Returns:
            Dict with publish status and Instagram post ID
        """
        if not self.ig_access_token or not self.ig_business_account_id:
            return {
                "success": False,
                "error": "Instagram credentials not configured",
                "platform": "instagram"
            }
        
        try:
            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/{self.api_version}/{self.ig_business_account_id}/media"
            
            container_payload = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": self.ig_access_token
            }
            
            # Add thumbnail if provided
            if thumbnail_url:
                container_payload["thumb_offset"] = 0  # Use first frame, or provide custom offset
            
            print(f"📸 Creating Instagram Reel container...")
            container_response = requests.post(container_url, data=container_payload, timeout=30)
            container_data = container_response.json()
            
            if "error" in container_data:
                return {
                    "success": False,
                    "error": container_data["error"].get("message", "Unknown error"),
                    "platform": "instagram",
                    "step": "create_container"
                }
            
            creation_id = container_data.get("id")
            if not creation_id:
                return {
                    "success": False,
                    "error": "No creation ID returned",
                    "platform": "instagram"
                }
            
            print(f"✅ Container created: {creation_id}")
            
            # Step 2: Publish the container
            publish_url = f"https://graph.facebook.com/{self.api_version}/{self.ig_business_account_id}/media_publish"
            
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.ig_access_token
            }
            
            print(f"🚀 Publishing Instagram Reel...")
            publish_response = requests.post(publish_url, data=publish_payload, timeout=30)
            publish_data = publish_response.json()
            
            if "error" in publish_data:
                return {
                    "success": False,
                    "error": publish_data["error"].get("message", "Unknown error"),
                    "platform": "instagram",
                    "step": "publish",
                    "creation_id": creation_id
                }
            
            instagram_post_id = publish_data.get("id")
            
            print(f"🎉 Instagram Reel published! Post ID: {instagram_post_id}")
            
            return {
                "success": True,
                "platform": "instagram",
                "post_id": instagram_post_id,
                "creation_id": creation_id
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out",
                "platform": "instagram"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }
    
    def publish_facebook_reel(
        self,
        video_url: str,
        caption: str = "CHANGE ME",
        thumbnail_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a video to Facebook Page (will surface as Reel if vertical).
        
        Args:
            video_url: Public URL to the video file
            caption: Caption text
            thumbnail_url: Optional thumbnail URL
            
        Returns:
            Dict with publish status and Facebook post ID
        """
        if not self.fb_access_token or not self.fb_page_id:
            return {
                "success": False,
                "error": "Facebook credentials not configured",
                "platform": "facebook"
            }
        
        try:
            # Publish video to Facebook Page
            publish_url = f"https://graph.facebook.com/{self.api_version}/{self.fb_page_id}/videos"
            
            payload = {
                "file_url": video_url,
                "description": caption,
                "access_token": self.fb_access_token
            }
            
            # Add thumbnail if provided
            if thumbnail_url:
                payload["thumb"] = thumbnail_url
            
            print(f"🚀 Publishing Facebook video...")
            response = requests.post(publish_url, data=payload, timeout=60)
            data = response.json()
            
            if "error" in data:
                return {
                    "success": False,
                    "error": data["error"].get("message", "Unknown error"),
                    "platform": "facebook"
                }
            
            fb_post_id = data.get("id")
            
            print(f"🎉 Facebook video published! Post ID: {fb_post_id}")
            print(f"ℹ️  If video is 9:16 vertical, Facebook will surface it as a Reel")
            
            return {
                "success": True,
                "platform": "facebook",
                "post_id": fb_post_id
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out",
                "platform": "facebook"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "facebook"
            }
    
    def publish_to_both(
        self,
        video_url: str,
        caption: str = "CHANGE ME",
        thumbnail_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish to both Instagram and Facebook.
        
        Args:
            video_url: Public URL to the video file
            caption: Caption text
            thumbnail_url: Optional thumbnail URL
            
        Returns:
            Dict with results from both platforms
        """
        instagram_result = self.publish_instagram_reel(video_url, caption, thumbnail_url)
        facebook_result = self.publish_facebook_reel(video_url, caption, thumbnail_url)
        
        return {
            "instagram": instagram_result,
            "facebook": facebook_result,
            "overall_success": instagram_result.get("success") and facebook_result.get("success")
        }
