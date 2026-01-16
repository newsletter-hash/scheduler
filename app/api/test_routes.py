"""
Test routes for brand connection testing.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.services.content_generator import ContentGenerator
from app.services.db_scheduler import DatabaseSchedulerService

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
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    schedule_id: Optional[str] = None


@router.post("/brand", response_model=TestBrandResponse)
async def test_brand_connection(request: TestBrandRequest):
    """
    Test a brand connection by generating a single reel.
    
    This endpoint:
    1. Generates a test reel for the specified brand and variant
    2. Schedules it for immediate publication (now + 1 minute)
    3. Returns the job details and schedule info
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
    
    # Validate variant
    if request.variant not in ['light', 'dark']:
        print(f"❌ Invalid variant: {request.variant}")
        raise HTTPException(status_code=400, detail="Invalid variant. Must be 'light' or 'dark'")
    
    try:
        # Test content lines
        test_content = [
            "Test Connection",
            "This is an automated test",
            "Verifying brand configuration",
            "All systems operational"
        ]
        
        print(f"📝 Test content prepared: {len(test_content)} lines")
        print(f"   {test_content}")
        
        # Initialize content generator
        print(f"\n🔧 Initializing ContentGenerator...")
        generator = ContentGenerator()
        
        # Generate the test reel
        print(f"🎬 Starting reel generation...")
        print(f"   Brand: {request.brand}")
        print(f"   Variant: {request.variant}")
        print(f"   Content lines: {test_content}")
        
        result = generator.generate_single_reel(
            content_lines=test_content,
            brand=request.brand,
            variant=request.variant,
            cta_type="follow"
        )
        
        print(f"\n✅ Generation completed!")
        print(f"📊 Result status: {result.get('status')}")
        print(f"🎬 Video path: {result.get('video_path')}")
        print(f"🖼️  Thumbnail path: {result.get('thumbnail_path')}")
        print(f"🆔 Reel ID: {result.get('reel_id')}")
        
        if result['status'] != 'completed':
            error_msg = result.get('error', 'Unknown error during generation')
            print(f"❌ Generation failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Generation failed: {error_msg}")
        
        # Schedule for immediate publication (1 minute from now)
        scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=1)
        
        print(f"\n📅 Scheduling test reel for immediate publication...")
        print(f"   Scheduled time: {scheduled_time.isoformat()}")
        
        scheduler = DatabaseSchedulerService()
        schedule_result = scheduler.schedule_reel(
            user_id="test@system",
            reel_id=result['reel_id'],
            scheduled_time=scheduled_time,
            caption=result.get('caption', 'Test reel'),
            platforms=["instagram", "facebook"],
            video_path=result.get('video_path'),
            thumbnail_path=result.get('thumbnail_path'),
            user_name="Test User",
            brand=request.brand,
            variant=request.variant
        )
        
        print(f"✅ Scheduled successfully!")
        print(f"📋 Schedule ID: {schedule_result.get('schedule_id')}")
        print(f"⏰ Will publish at: {schedule_result.get('scheduled_time')}")
        
        print(f"\n{'='*100}")
        print(f"🎉 TEST COMPLETED SUCCESSFULLY")
        print(f"{'='*100}\n")
        
        return TestBrandResponse(
            success=True,
            job_id=result['reel_id'],
            brand=request.brand,
            variant=request.variant,
            message=f"Test reel generated and scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            video_path=result.get('video_path'),
            thumbnail_path=result.get('thumbnail_path'),
            schedule_id=schedule_result.get('schedule_id')
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
