"""
PostgreSQL-based scheduler service with multi-user support.
"""
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import and_
from app.models import ScheduledReel, UserProfile
from app.db_connection import get_db_session
from app.services.social_publisher import SocialPublisher


class DatabaseSchedulerService:
    """Scheduler service using PostgreSQL for multi-user support."""
    
    def __init__(self):
        """Initialize the database scheduler service."""
        self.publisher = SocialPublisher()
    
    def schedule_reel(
        self,
        user_id: str,
        reel_id: str,
        scheduled_time: datetime,
        caption: str = "CHANGE ME",
        platforms: list[str] = ["instagram"],
        video_path: Optional[Path] = None,
        thumbnail_path: Optional[Path] = None,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a reel for future publishing.
        
        Args:
            user_id: User identifier (e.g., email or username)
            reel_id: Unique identifier for the reel
            scheduled_time: When to publish (datetime object)
            caption: Caption for the post
            platforms: List of platforms ("instagram", "facebook")
            video_path: Path to video file
            thumbnail_path: Path to thumbnail
            user_name: Display name for the user
            
        Returns:
            Schedule details with schedule_id
        """
        import uuid
        
        with get_db_session() as db:
            # Generate schedule ID
            schedule_id = str(uuid.uuid4())[:8]
            
            # Prepare metadata
            metadata = {
                "platforms": platforms,
                "video_path": str(video_path) if video_path else None,
                "thumbnail_path": str(thumbnail_path) if thumbnail_path else None
            }
            
            # Create scheduled reel
            scheduled_reel = ScheduledReel(
                schedule_id=schedule_id,
                user_id=user_id,
                user_name=user_name or user_id,
                reel_id=reel_id,
                caption=caption,
                scheduled_time=scheduled_time,
                status="scheduled",
                extra_data=metadata  # Store in extra_data column
            )
            
            db.add(scheduled_reel)
            db.commit()
            
            return scheduled_reel.to_dict()
    
    def get_pending_publications(self) -> list[Dict[str, Any]]:
        """
        Get all scheduled reels that are due for publishing.
        
        Returns:
            List of schedules ready to publish
        """
        with get_db_session() as db:
            now = datetime.now(timezone.utc)
            
            pending = db.query(ScheduledReel).filter(
                and_(
                    ScheduledReel.status == "scheduled",
                    ScheduledReel.scheduled_time <= now
                )
            ).all()
            
            return [reel.to_dict() for reel in pending]
    
    def get_all_scheduled(self, user_id: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        Get all scheduled reels, optionally filtered by user.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List of all schedules
        """
        with get_db_session() as db:
            query = db.query(ScheduledReel)
            
            if user_id:
                query = query.filter(ScheduledReel.user_id == user_id)
            
            schedules = query.order_by(ScheduledReel.scheduled_time.desc()).all()
            return [reel.to_dict() for reel in schedules]
    
    def delete_scheduled(self, schedule_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete a scheduled post.
        
        Args:
            schedule_id: ID of the schedule to delete
            user_id: Optional user filter for security
            
        Returns:
            True if deleted, False if not found
        """
        with get_db_session() as db:
            query = db.query(ScheduledReel).filter(
                ScheduledReel.schedule_id == schedule_id
            )
            
            if user_id:
                query = query.filter(ScheduledReel.user_id == user_id)
            
            scheduled_reel = query.first()
            
            if not scheduled_reel:
                return False
            
            db.delete(scheduled_reel)
            db.commit()
            return True
    
    def mark_as_published(self, schedule_id: str) -> None:
        """Mark a schedule as successfully published."""
        with get_db_session() as db:
            scheduled_reel = db.query(ScheduledReel).filter(
                ScheduledReel.schedule_id == schedule_id
            ).first()
            
            if scheduled_reel:
                scheduled_reel.status = "published"
                scheduled_reel.published_at = datetime.now(timezone.utc)
                db.commit()
    
    def mark_as_failed(self, schedule_id: str, error: str) -> None:
        """Mark a schedule as failed with error message."""
        with get_db_session() as db:
            scheduled_reel = db.query(ScheduledReel).filter(
                ScheduledReel.schedule_id == schedule_id
            ).first()
            
            if scheduled_reel:
                scheduled_reel.status = "failed"
                scheduled_reel.publish_error = error
                db.commit()
    
    def publish_now(
        self,
        video_path: Path,
        thumbnail_path: Path,
        caption: str = "CHANGE ME",
        platforms: list[str] = ["instagram"],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a reel immediately using user's credentials.
        
        Args:
            video_path: Path to video file
            thumbnail_path: Path to thumbnail
            caption: Caption for the post
            platforms: List of platforms
            user_id: User ID to use credentials from
            
        Returns:
            Publishing results
        """
        # Get user credentials if user_id provided
        if user_id:
            with get_db_session() as db:
                user = db.query(UserProfile).filter(
                    UserProfile.user_id == user_id
                ).first()
                
                if user:
                    # Use user's specific credentials
                    publisher = SocialPublisher(
                        instagram_account_id=user.instagram_business_account_id,
                        facebook_page_id=user.facebook_page_id,
                        meta_access_token=user.meta_access_token or user.instagram_access_token
                    )
                else:
                    publisher = self.publisher
        else:
            publisher = self.publisher
        
        # Get public URL
        public_url_base = os.getenv("PUBLIC_URL_BASE", "http://localhost:8000")
        video_url = f"{public_url_base}/output/videos/{video_path.name}"
        thumbnail_url = f"{public_url_base}/output/thumbnails/{thumbnail_path.name}"
        
        results = {}
        
        if "instagram" in platforms:
            print("📸 Publishing to Instagram...")
            results["instagram"] = publisher.publish_instagram_reel(
                video_url=video_url,
                caption=caption,
                thumbnail_url=thumbnail_url
            )
        
        if "facebook" in platforms:
            print("📘 Publishing to Facebook...")
            results["facebook"] = publisher.publish_facebook_reel(
                video_url=video_url,
                caption=caption,
                thumbnail_url=thumbnail_url
            )
        
        return results
    
    def get_or_create_user(
        self,
        user_id: str,
        user_name: str,
        email: Optional[str] = None,
        instagram_account_id: Optional[str] = None,
        facebook_page_id: Optional[str] = None,
        meta_access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get existing user or create new one.
        
        Args:
            user_id: User identifier
            user_name: Display name
            email: Email address
            instagram_account_id: Instagram Business Account ID
            facebook_page_id: Facebook Page ID
            meta_access_token: Meta API access token
            
        Returns:
            User profile data
        """
        with get_db_session() as db:
            user = db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not user:
                user = UserProfile(
                    user_id=user_id,
                    user_name=user_name,
                    email=email,
                    instagram_business_account_id=instagram_account_id,
                    facebook_page_id=facebook_page_id,
                    meta_access_token=meta_access_token
                )
                db.add(user)
                db.commit()
            
            return user.to_dict()
