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
        user_name: Optional[str] = None,
        brand: Optional[str] = None,
        variant: Optional[str] = None
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
            brand: Brand name ("gymcollege" or "healthycollege")
            variant: Variant type ("light" or "dark")
            
        Returns:
            Schedule details with schedule_id
        """
        import uuid
        
        print("\n🔵 DatabaseSchedulerService.schedule_reel() called")
        print(f"   User ID: {user_id}")
        print(f"   Reel ID: {reel_id}")
        print(f"   Scheduled time: {scheduled_time}")
        print(f"   Platforms: {platforms}")
        print(f"   Brand: {brand}, Variant: {variant}")
        
        try:
            with get_db_session() as db:
                print("   ✅ Database session created")
                
                # Generate schedule ID
                schedule_id = str(uuid.uuid4())[:8]
                print(f"   ✅ Generated schedule_id: {schedule_id}")
                
                # Prepare metadata
                metadata = {
                    "platforms": platforms,
                    "video_path": str(video_path) if video_path else None,
                    "thumbnail_path": str(thumbnail_path) if thumbnail_path else None,
                    "brand": brand,
                    "variant": variant or "light"
                }
                print(f"   ✅ Metadata prepared: {metadata}")
                
                # Create scheduled reel
                print("   🔄 Creating ScheduledReel object...")
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
                print("   ✅ ScheduledReel object created")
                
                print("   🔄 Adding to database session...")
                db.add(scheduled_reel)
                print("   ✅ Added to session")
                
                print("   🔄 Committing to database...")
                db.commit()
                print("   ✅ COMMITTED TO DATABASE!")
                
                result = scheduled_reel.to_dict()
                print(f"   ✅ Converted to dict: {result}")
                
                return result
                
        except Exception as e:
            print(f"\n❌ ERROR in DatabaseSchedulerService.schedule_reel()")
            print(f"   Exception type: {type(e).__name__}")
            print(f"   Details: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_pending_publications(self) -> list[Dict[str, Any]]:
        """
        Get all scheduled reels that are due for publishing.
        Uses atomic locking to prevent duplicate publishing.
        
        Returns:
            List of schedules ready to publish (already marked as 'publishing')
        """
        with get_db_session() as db:
            now = datetime.now(timezone.utc)
            
            # Use FOR UPDATE to lock rows and prevent race conditions
            # This ensures only one scheduler instance can pick up each post
            pending = db.query(ScheduledReel).filter(
                and_(
                    ScheduledReel.status == "scheduled",
                    ScheduledReel.scheduled_time <= now
                )
            ).with_for_update(skip_locked=True).all()
            
            # IMMEDIATELY mark all as "publishing" to prevent duplicate picks
            result = []
            for reel in pending:
                reel.status = "publishing"
                result.append(reel.to_dict())
            
            # Commit the status change before returning
            db.commit()
            
            return result
    
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
    
    def mark_as_published(self, schedule_id: str, post_ids: Dict[str, str] = None) -> None:
        """Mark a schedule as successfully published.
        
        Args:
            schedule_id: The schedule ID
            post_ids: Dict of platform -> post_id for storing results
        """
        with get_db_session() as db:
            scheduled_reel = db.query(ScheduledReel).filter(
                ScheduledReel.schedule_id == schedule_id
            ).first()
            
            if scheduled_reel:
                scheduled_reel.status = "published"
                scheduled_reel.published_at = datetime.now(timezone.utc)
                
                # Store post IDs in metadata if provided
                if post_ids:
                    metadata = scheduled_reel.extra_data or {}
                    metadata['post_ids'] = post_ids
                    scheduled_reel.extra_data = metadata
                
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
    
    def reset_stuck_publishing(self, max_age_minutes: int = 10) -> int:
        """
        Reset any posts stuck in 'publishing' status for too long.
        This handles cases where the server crashed during publishing.
        
        Args:
            max_age_minutes: Max minutes a post can be in 'publishing' before reset
            
        Returns:
            Number of posts reset
        """
        from datetime import timedelta
        
        with get_db_session() as db:
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
            
            # Find posts stuck in 'publishing' for too long
            stuck = db.query(ScheduledReel).filter(
                and_(
                    ScheduledReel.status == "publishing",
                    ScheduledReel.scheduled_time <= cutoff
                )
            ).all()
            
            count = 0
            for reel in stuck:
                reel.status = "scheduled"  # Reset to allow retry
                reel.publish_error = f"Reset after being stuck in publishing for >{max_age_minutes} minutes"
                count += 1
            
            if count > 0:
                db.commit()
                print(f"⚠️ Reset {count} stuck publishing post(s)")
            
            return count
    
    def publish_now(
        self,
        video_path: Path,
        thumbnail_path: Path,
        caption: str = "CHANGE ME",
        platforms: list[str] = ["instagram"],
        user_id: Optional[str] = None,
        brand_config: Optional['BrandConfig'] = None
    ) -> Dict[str, Any]:
        """
        Publish a reel immediately using user's credentials or brand credentials.
        
        Args:
            video_path: Path to video file
            thumbnail_path: Path to thumbnail
            caption: Caption for the post
            platforms: List of platforms
            user_id: User ID to use credentials from
            brand_config: Brand configuration with specific credentials
            
        Returns:
            Publishing results
        """
        from app.services.social_publisher import SocialPublisher
        
        # Priority: brand_config > user_id > default
        publisher = None
        
        if brand_config:
            # Use brand-specific credentials
            publisher = SocialPublisher(brand_config=brand_config)
        elif user_id:
            # Get user credentials if user_id provided
            with get_db_session() as db:
                user = db.query(UserProfile).filter(
                    UserProfile.user_id == user_id
                ).first()
                
                if user:
                    # Create temporary brand config from user credentials
                    from app.core.config import BrandConfig
                    user_config = BrandConfig(
                        name="user_custom",
                        display_name="User Custom",
                        primary_color=(0, 0, 0),
                        secondary_color=(0, 0, 0),
                        text_color=(0, 0, 0),
                        highlight_color=(0, 0, 0, 0),
                        logo_filename="",
                        thumbnail_bg_color=(0, 0, 0),
                        thumbnail_text_color=(0, 0, 0),
                        content_title_color=(0, 0, 0),
                        content_highlight_color=(0, 0, 0, 0),
                        instagram_business_account_id=user.instagram_business_account_id,
                        facebook_page_id=user.facebook_page_id,
                        meta_access_token=user.meta_access_token
                    )
                    publisher = SocialPublisher(brand_config=user_config)
        
        if not publisher:
            # Use default credentials
            publisher = SocialPublisher()
        
        # Get public URL - auto-detect Railway or use configured value
        # Railway sets RAILWAY_PUBLIC_DOMAIN automatically
        railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_domain:
            public_url_base = f"https://{railway_domain}"
            print(f"🌐 Using Railway domain: {railway_domain}")
        else:
            public_url_base = os.getenv("PUBLIC_URL_BASE", "http://localhost:8000")
            print(f"🌐 Using PUBLIC_URL_BASE: {public_url_base}")
        
        video_url = f"{public_url_base}/output/videos/{video_path.name}"
        thumbnail_url = f"{public_url_base}/output/thumbnails/{thumbnail_path.name}"
        
        print(f"🎬 Video URL: {video_url}")
        print(f"🖼️  Thumbnail URL: {thumbnail_url}")
        
        # Verify video file exists
        if not video_path.exists():
            print(f"❌ ERROR: Video file not found at {video_path}")
        else:
            print(f"✅ Video file exists: {video_path} ({video_path.stat().st_size} bytes)")
        
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

    def get_next_available_slot(
        self,
        brand: str,
        variant: str,
        reference_date: Optional[datetime] = None
    ) -> datetime:
        """
        Get the next available scheduling slot for a brand+variant combo.
        
        Slot Rules:
        - Light mode: 12 AM, 8 AM, 4 PM (every 8 hours starting at midnight)
        - Dark mode: 4 AM, 12 PM, 8 PM (every 8 hours starting at 4 AM)
        
        Starting from January 16, 2026, or today if after that date.
        Each brand has its own independent schedule.
        
        Args:
            brand: Brand name ("gymcollege" or "healthycollege")
            variant: "light" or "dark"
            reference_date: Optional reference date (defaults to now)
            
        Returns:
            Next available datetime for scheduling
        """
        from datetime import timedelta
        
        # Define slot hours
        LIGHT_SLOTS = [0, 8, 16]   # 12 AM, 8 AM, 4 PM
        DARK_SLOTS = [4, 12, 20]   # 4 AM, 12 PM, 8 PM
        
        slots = LIGHT_SLOTS if variant == "light" else DARK_SLOTS
        
        # Starting reference point
        start_date = datetime(2026, 1, 16, tzinfo=timezone.utc)
        now = reference_date or datetime.now(timezone.utc)
        
        # Use the later of start_date or now
        base_date = max(start_date, now)
        
        # Get all scheduled posts for this brand+variant
        with get_db_session() as db:
            # Get schedules for this brand that are scheduled or publishing
            # Filter by variant in metadata
            schedules = db.query(ScheduledReel).filter(
                and_(
                    ScheduledReel.status.in_(["scheduled", "publishing"]),
                    ScheduledReel.scheduled_time >= start_date
                )
            ).all()
            
            # Filter by brand and variant
            occupied_slots = set()
            for schedule in schedules:
                metadata = schedule.extra_data or {}
                schedule_brand = metadata.get("brand", "").lower()
                schedule_variant = metadata.get("variant", "light")
                
                # Match by brand name (normalize gymcollege and healthycollege)
                brand_match = (
                    (brand.lower() == "gymcollege" and schedule_brand in ["gymcollege", "the_gym_college", ""]) or
                    (brand.lower() == "healthycollege" and schedule_brand in ["healthycollege", "wellness_life"])
                )
                
                if brand_match and schedule_variant == variant:
                    # Store as timestamp for easy comparison
                    occupied_slots.add(schedule.scheduled_time.replace(tzinfo=timezone.utc).timestamp())
        
        # Find next available slot starting from base_date
        current = base_date.replace(minute=0, second=0, microsecond=0)
        
        # Find the next valid slot hour on or after current time
        max_iterations = 365 * 3  # Don't search more than 3*365 slot checks (~1 year)
        
        for _ in range(max_iterations):
            for hour in slots:
                candidate = current.replace(hour=hour)
                
                # Skip if in the past
                if candidate <= now:
                    continue
                
                # Check if slot is available
                if candidate.timestamp() not in occupied_slots:
                    return candidate
            
            # Move to next day
            current = current + timedelta(days=1)
            current = current.replace(hour=0)
        
        # Fallback: just return tomorrow at first slot
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=slots[0], minute=0, second=0, microsecond=0)

    def get_scheduled_slots_for_brand(
        self,
        brand: str,
        variant: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[datetime]:
        """
        Get all scheduled/occupied slots for a brand+variant combo.
        
        Args:
            brand: Brand name
            variant: "light" or "dark"
            start_date: Optional start filter
            end_date: Optional end filter
            
        Returns:
            List of occupied datetime slots
        """
        with get_db_session() as db:
            query = db.query(ScheduledReel).filter(
                ScheduledReel.status.in_(["scheduled", "publishing"])
            )
            
            if start_date:
                query = query.filter(ScheduledReel.scheduled_time >= start_date)
            if end_date:
                query = query.filter(ScheduledReel.scheduled_time <= end_date)
            
            schedules = query.all()
            
            occupied = []
            for schedule in schedules:
                metadata = schedule.extra_data or {}
                schedule_brand = metadata.get("brand", "").lower()
                schedule_variant = metadata.get("variant", "light")
                
                brand_match = (
                    (brand.lower() == "gymcollege" and schedule_brand in ["gymcollege", "the_gym_college", ""]) or
                    (brand.lower() == "healthycollege" and schedule_brand in ["healthycollege", "wellness_life"])
                )
                
                if brand_match and schedule_variant == variant:
                    occupied.append(schedule.scheduled_time)
            
            return sorted(occupied)
