"""
Meta API service for scheduling Instagram Reels.
"""
import os
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.logger import get_logger

logger = get_logger(__name__)


class MetaAPIError(Exception):
    """Exception raised for Meta API errors."""
    pass


class MetaAPIService:
    """Service for interacting with Meta (Facebook) Graph API for Instagram."""
    
    BASE_URL = "https://graph.facebook.com/v21.0"
    
    def __init__(self):
        """Initialize the Meta API service."""
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.instagram_account_id = os.getenv("META_INSTAGRAM_ACCOUNT_ID")
        
        if not self.access_token:
            logger.warning("META_ACCESS_TOKEN not configured")
        if not self.instagram_account_id:
            logger.warning("META_INSTAGRAM_ACCOUNT_ID not configured")
    
    def _check_configuration(self) -> None:
        """
        Check if the service is properly configured.
        
        Raises:
            MetaAPIError: If credentials are not configured
        """
        if not self.access_token or not self.instagram_account_id:
            raise MetaAPIError(
                "Meta API credentials not configured. "
                "Please set META_ACCESS_TOKEN and META_INSTAGRAM_ACCOUNT_ID in .env file"
            )
    
    def upload_video(self, video_path: Path, caption: str) -> str:
        """
        Upload a video to create a container for Instagram Reels.
        
        Args:
            video_path: Path to the video file
            caption: Caption for the reel
            
        Returns:
            Container ID for the uploaded video
            
        Raises:
            MetaAPIError: If upload fails
        """
        self._check_configuration()
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Step 1: Create media container
        url = f"{self.BASE_URL}/{self.instagram_account_id}/media"
        
        # Get video URL (needs to be publicly accessible)
        # For local development, you'll need to expose the video via ngrok or similar
        # For production, use a CDN or cloud storage
        video_url = self._get_public_video_url(video_path)
        
        params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": True,
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "id" not in data:
                raise MetaAPIError(f"Failed to create media container: {data}")
            
            container_id = data["id"]
            logger.info(f"Created media container: {container_id}")
            return container_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload video: {e}")
            raise MetaAPIError(f"Failed to upload video: {str(e)}")
    
    def publish_container(self, container_id: str) -> str:
        """
        Publish a media container immediately.
        
        Args:
            container_id: The media container ID
            
        Returns:
            The published media ID
            
        Raises:
            MetaAPIError: If publishing fails
        """
        self._check_configuration()
        
        url = f"{self.BASE_URL}/{self.instagram_account_id}/media_publish"
        
        params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "id" not in data:
                raise MetaAPIError(f"Failed to publish media: {data}")
            
            media_id = data["id"]
            logger.info(f"Published media: {media_id}")
            return media_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to publish media: {e}")
            raise MetaAPIError(f"Failed to publish media: {str(e)}")
    
    def schedule_reel(
        self,
        video_path: Path,
        caption: str,
        scheduled_time: datetime
    ) -> Dict[str, Any]:
        """
        Schedule an Instagram Reel for future publishing.
        
        Note: Instagram API currently doesn't support scheduled publishing directly.
        This method creates the container and returns the ID for later publishing.
        You'll need to implement a scheduler (like Celery) to publish at the scheduled time.
        
        Args:
            video_path: Path to the video file
            caption: Caption for the reel
            scheduled_time: When to publish the reel
            
        Returns:
            Dictionary with container_id and scheduled_time
            
        Raises:
            MetaAPIError: If scheduling fails
        """
        self._check_configuration()
        
        # Upload video and create container
        container_id = self.upload_video(video_path, caption)
        
        logger.info(
            f"Reel scheduled for {scheduled_time.isoformat()}. "
            f"Container ID: {container_id}"
        )
        
        return {
            "container_id": container_id,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "scheduled",
            "message": "Reel will be published at the scheduled time"
        }
    
    def _get_public_video_url(self, video_path: Path) -> str:
        """
        Get a publicly accessible URL for the video.
        
        For local development, this needs to be implemented using:
        - ngrok for local tunneling
        - Cloud storage (AWS S3, Google Cloud Storage, etc.)
        - CDN
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Publicly accessible URL
            
        Raises:
            MetaAPIError: If URL cannot be generated
        """
        # For production, upload to cloud storage and return the URL
        # For now, raise an error with instructions
        raise MetaAPIError(
            "Video must be hosted on a publicly accessible URL. "
            "Please upload the video to cloud storage (S3, GCS, etc.) "
            "or use ngrok to expose your local server."
        )
    
    def get_container_status(self, container_id: str) -> Dict[str, Any]:
        """
        Check the status of a media container.
        
        Args:
            container_id: The media container ID
            
        Returns:
            Container status information
            
        Raises:
            MetaAPIError: If status check fails
        """
        self._check_configuration()
        
        url = f"{self.BASE_URL}/{container_id}"
        
        params = {
            "fields": "id,status,status_code",
            "access_token": self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get container status: {e}")
            raise MetaAPIError(f"Failed to get container status: {str(e)}")
