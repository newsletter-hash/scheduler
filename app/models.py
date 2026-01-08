"""
Database models for PostgreSQL storage.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ScheduledReel(Base):
    """Model for scheduled reels with user support."""
    __tablename__ = "scheduled_reels"
    
    # Primary key
    schedule_id = Column(String(36), primary_key=True)
    
    # User identification
    user_id = Column(String(100), nullable=False, index=True)
    user_name = Column(String(255))
    
    # Reel information
    reel_id = Column(String(36), nullable=False, index=True)
    caption = Column(Text)
    
    # Scheduling
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Publishing status
    status = Column(String(20), default="scheduled", nullable=False, index=True)
    # Status values: "scheduled", "published", "failed"
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    publish_error = Column(Text, nullable=True)
    
    # Extra data (platforms, video_path, thumbnail_path, etc.)
    extra_data = Column(JSON, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "schedule_id": self.schedule_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "reel_id": self.reel_id,
            "caption": self.caption,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "status": self.status,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "publish_error": self.publish_error,
            "metadata": self.extra_data or {}  # Return as "metadata" for API compatibility
        }


class UserProfile(Base):
    """Model for user profiles with Instagram/Facebook credentials."""
    __tablename__ = "user_profiles"
    
    # Primary key
    user_id = Column(String(100), primary_key=True)
    
    # User information
    user_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, unique=True, index=True)
    
    # Instagram credentials
    instagram_business_account_id = Column(String(255), nullable=True)
    instagram_access_token = Column(Text, nullable=True)
    
    # Facebook credentials
    facebook_page_id = Column(String(255), nullable=True)
    facebook_access_token = Column(Text, nullable=True)
    
    # Meta app credentials
    meta_access_token = Column(Text, nullable=True)
    
    # Settings
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self, include_tokens=False):
        """Convert to dictionary for API responses."""
        data = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "email": self.email,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "has_instagram": bool(self.instagram_business_account_id),
            "has_facebook": bool(self.facebook_page_id),
        }
        
        if include_tokens:
            data.update({
                "instagram_business_account_id": self.instagram_business_account_id,
                "instagram_access_token": self.instagram_access_token,
                "facebook_page_id": self.facebook_page_id,
                "facebook_access_token": self.facebook_access_token,
                "meta_access_token": self.meta_access_token,
            })
        
        return data
