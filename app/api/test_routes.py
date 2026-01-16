"""
Test routes for brand connection testing.
"""
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.services.image_generator import ImageGenerator
from app.services.video_generator import VideoGenerator
from app.services.caption_builder import CaptionBuilder
from app.services.content_generator import ContentGenerator
from app.services.db_scheduler import DatabaseSchedulerService
from app.core.config import BrandType

router = APIRouter(prefix="/api/test", tags=["test"])


class TestBrandRequest(BaseModel):
    brand: str
    variant: str  # "light" or "dark"


class TestBrandResponse(BaseModel):
    success: bool
    job_id: str
    brand: str
    variant: str
    message: str
    title: str
    content_lines: list[str]
    caption: str
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None


@router.post("/brand", response_model=TestBrandResponse)
async def test_brand_connection(request: TestBrandRequest):
    """
    Test a brand connection by generating a single reel with AI content.
    
    This endpoint:
    1. Generates viral content using AI (same as Auto-Generate)
    2. Creates thumbnail, reel image, and video
    3. Returns all details for user review - NO AUTOMATIC SCHEDULING
    """
    print(f"\n{'='*100}")
    print(f"🧪 TEST BRAND CONNECTION ENDPOINT CALLED")
    print(f"{'='*100}")
    print(f"🏷️  Brand: {request.brand}")
    print(f"🎨 Variant: {request.variant}")
    print(f"⏰ Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*100}\n")
    
    # Validate brand
    valid_brands = ['gymcollege', 'healthycollege', 'vitalitycollege', 'longevitycollege']
    if request.brand not in valid_brands:
        print(f"❌ Invalid brand: {request.brand}")
        raise HTTPException(status_code=400, detail=f"Invalid brand. Must be one of: {valid_brands}")
    
    # Map brand string to BrandType enum
    brand_mapping = {
        "gymcollege": BrandType.THE_GYM_COLLEGE,
        "healthycollege": BrandType.HEALTHY_COLLEGE,
        "vitalitycollege": BrandType.VITALITY_COLLEGE,
        "longevitycollege": BrandType.LONGEVITY_COLLEGE,
    }
    brand_type = brand_mapping[request.brand]
    print(f"🔄 Mapped '{request.brand}' to BrandType: {brand_type}")
    
    # Validate variant
    if request.variant not in ['light', 'dark']:
        print(f"❌ Invalid variant: {request.variant}")
        raise HTTPException(status_code=400, detail="Invalid variant. Must be 'light' or 'dark'")
    
    try:
        # Generate unique reel ID
        reel_id = f"TEST-{uuid.uuid4().hex[:8]}_{request.brand}"
        print(f"🆔 Generated reel ID: {reel_id}")
        
        # Step 0: Generate viral content using AI (same as Auto-Generate)
        print(f"\n🤖 Step 0: Generating AI viral content...")
        content_gen = ContentGenerator()
        viral_content = content_gen.generate_viral_content(topic_hint=None)
        
        if not viral_content.get('success'):
            print(f"   ❌ AI generation failed, using fallback")
        
        title = viral_content.get('title', '🧪 Connection Test')
        lines = viral_content.get('content_lines', [
            "This is an automated test",
            "Verifying brand configuration",
            "All systems operational"
        ])
        
        print(f"📝 AI Content generated:")
        print(f"   Title: {title}")
        print(f"   Lines: {lines}")
        
        # Define output paths
        base_dir = Path(__file__).resolve().parent.parent.parent
        thumbnail_path = base_dir / "output" / "thumbnails" / f"{reel_id}.png"
        reel_image_path = base_dir / "output" / "reels" / f"{reel_id}.png"
        video_path = base_dir / "output" / "videos" / f"{reel_id}.mp4"
        
        print(f"\n📁 Output paths:")
        print(f"   Thumbnail: {thumbnail_path}")
        print(f"   Reel image: {reel_image_path}")
        print(f"   Video: {video_path}")
        
        # Initialize services
        print(f"\n🔧 Initializing generators...")
        image_generator = ImageGenerator(brand_type, variant=request.variant, brand_name=request.brand)
        video_generator = VideoGenerator()
        caption_builder = CaptionBuilder()
        
        # Step 1: Generate thumbnail
        print(f"\n🖼️  Step 1: Generating thumbnail...")
        try:
            image_generator.generate_thumbnail(
                title=title,
                output_path=thumbnail_path
            )
            print(f"   ✅ Thumbnail generated: {thumbnail_path.name}")
        except Exception as e:
            print(f"   ❌ Thumbnail generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {str(e)}")
        
        # Step 2: Generate reel image
        print(f"\n🎨 Step 2: Generating reel image...")
        try:
            image_generator.generate_reel_image(
                title=title,
                lines=lines,
                output_path=reel_image_path,
                cta_type="follow"
            )
            print(f"   ✅ Reel image generated: {reel_image_path.name}")
        except Exception as e:
            print(f"   ❌ Reel image generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Reel image generation failed: {str(e)}")
        
        # Step 3: Generate video
        print(f"\n🎬 Step 3: Generating video...")
        try:
            video_generator.generate_reel_video(
                reel_image_path=reel_image_path,
                output_path=video_path,
                music_id=None  # Random music
            )
            print(f"   ✅ Video generated: {video_path.name}")
        except Exception as e:
            print(f"   ❌ Video generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
        
        # Step 4: Generate caption
        print(f"\n✍️  Step 4: Generating caption...")
        try:
            caption = caption_builder.build_caption(
                title=title,
                lines=lines
            )
            print(f"   ✅ Caption generated: {len(caption)} characters")
        except Exception as e:
            print(f"   ❌ Caption generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")
        
        print(f"\n{'='*100}")
        print(f"🎉 TEST GENERATION COMPLETED SUCCESSFULLY")
        print(f"   Reel ID: {reel_id}")
        print(f"   Video: /output/videos/{reel_id}.mp4")
        print(f"   Thumbnail: /output/thumbnails/{reel_id}.png")
        print(f"   Caption: {caption[:100]}...")
        print(f"   ⚠️  NOT SCHEDULED - User must review and confirm")
        print(f"{'='*100}\n")
        
        return TestBrandResponse(
            success=True,
            job_id=reel_id,
            brand=request.brand,
            variant=request.variant,
            message="Test reel generated successfully. Review and schedule manually.",
            title=title,
            content_lines=lines,
            caption=caption,
            video_path=f"/output/videos/{reel_id}.mp4",
            thumbnail_path=f"/output/thumbnails/{reel_id}.png"
        )
        
    except Exception as e:
        print(f"\n{'='*100}")
        print(f"❌ TEST FAILED WITH ERROR")
        print(f"{'='*100}")
        print(f"🔥 Error type: {type(e).__name__}")
        print(f"📄 Error message: {str(e)}")
        import traceback
        print(f"📜 Traceback:\n{traceback.format_exc()}")
        print(f"{'='*100}\n")
        
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reel/{reel_id}")
async def delete_test_reel(reel_id: str):
    """
    Delete a test reel (video, thumbnail, reel image files).
    """
    print(f"\n🗑️  DELETE TEST REEL: {reel_id}")
    
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent
        
        files_to_delete = [
            base_dir / "output" / "videos" / f"{reel_id}.mp4",
            base_dir / "output" / "thumbnails" / f"{reel_id}.png",
            base_dir / "output" / "reels" / f"{reel_id}.png"
        ]
        
        deleted = []
        for file_path in files_to_delete:
            if file_path.exists():
                file_path.unlink()
                deleted.append(str(file_path.name))
                print(f"   ✅ Deleted: {file_path.name}")
        
        if not deleted:
            print(f"   ⚠️  No files found for reel: {reel_id}")
            raise HTTPException(status_code=404, detail=f"No files found for reel: {reel_id}")
        
        print(f"   🎉 Successfully deleted {len(deleted)} file(s)\n")
        return {"success": True, "deleted_files": deleted, "message": f"Deleted {len(deleted)} file(s)"}
        
    except Exception as e:
        print(f"   ❌ Delete failed: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))
