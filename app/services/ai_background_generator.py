"""
AI background generation service using OpenAI's DALL-E API.
"""
import os
import uuid
import time
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image
from openai import OpenAI
from app.core.constants import REEL_WIDTH, REEL_HEIGHT


class AIBackgroundGenerator:
    """Service for generating AI backgrounds for dark mode."""
    
    def __init__(self):
        """Initialize the AI background generator with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)
    
    def generate_background(self, brand_name: str, user_prompt: str = None, progress_callback=None) -> Image.Image:
        """
        Generate an AI background image based on brand.
        
        Args:
            brand_name: Brand name ("gymcollege" or "healthycollege")
            user_prompt: Custom prompt from user (optional)
            progress_callback: Callback function for progress updates (optional)
            
        Returns:
            PIL Image object with AI-generated background
        """
        start_time = time.time()
        
        if progress_callback:
            progress_callback("Preparing AI prompt...", 10)
        
        # If user provides custom prompt, adapt it with brand color tones
        if user_prompt:
            color_adaptations = {
                "gymcollege": " Overall color palette MUST be dominated by dark blue tones specifically #00435c (dark teal-blue), absolutely NO green tones, use only deep navy blues, dark teal-blues, and rich sapphire hues with moody atmospheric lighting. Think ocean depths and icy blue environments.",
                "healthycollege": " Overall color palette dominated by dark green tones, green healthy and nature environment with deep emerald greens, and rich forest green hues with moody atmospheric lighting.",
                "vitalitycollege": " Overall color palette MUST be dominated by rose, pink, and mauve tones specifically rose #b85578, soft pinks, dusty rose, and warm mauve hues with elegant atmospheric lighting. Think blooming gardens, sunset skies, and feminine vitality energy. Absolutely NO blues or greens."
            }
            prompt = user_prompt + color_adaptations.get(brand_name, color_adaptations["gymcollege"])
        else:
            # Default prompts
            prompts = {
                "gymcollege": "A high-detail, cinematic health concept scene filling the entire frame with no empty space, featuring an oversized anatomical muscle fiber or human heart as the central focal subject, surrounded by molecular structures, protein chains, and energy particles in carefully arranged layers creating depth. Sharp, tactile microscopic cellular structures in the foreground with dark teal-blue (#00435c) and deep navy blue gradients, NO green tones whatsoever, glowing blue particles, and liquid effects in the background. Vivid saturated colors dominated by dark blue #00435c, deep navy, and dark teal-blue with contrasting warm yellow and orange accents for ATP energy and muscle activation. Studio-quality cinematic lighting with soft global illumination, subtle translucent glow on biological structures, and crisp highlights making everything pristine and idealized. Scientific, revealing mood visualizing hidden performance processes inside the athletic body, instantly readable at thumbnail size. Overall color palette strictly dark blue #00435c, deep ocean blues, and icy teal-blues with moody atmospheric lighting, absolutely NO green.",
                "healthycollege": "A high-detail, cinematic health concept scene filling the entire frame with no empty space, featuring an oversized cluster of vibrant superfoods, fresh produce, or anatomical digestive system as the central focal subject, surrounded by vitamin molecules, antioxidant particles, and nutrient symbols in carefully arranged layers creating depth. Sharp, tactile food textures and cellular structures in the foreground with softly lit green and teal gradients, glowing wellness particles, and liquid nutrient effects in the background. Vivid saturated colors dominated by clean emerald greens and teals with contrasting warm yellow, red, and orange accents from fruits and vital energy. Studio-quality cinematic lighting with soft global illumination, subtle translucent glow on organic elements, and crisp highlights making everything pristine and premium. Scientific, revealing mood visualizing hidden wellness processes inside the healthy body, instantly readable at thumbnail size. Overall color palette dominated by dark green tones, deep emerald greens, and rich forest green hues with moody atmospheric lighting.",
                "vitalitycollege": "A high-detail, cinematic vitality and wellness concept scene filling the entire frame with no empty space, featuring an oversized feminine anatomical element like ovaries, hormone molecules, or cellular rejuvenation processes as the central focal subject, surrounded by flower petals, energy spirals, and vitality particles in carefully arranged layers creating depth. Sharp, tactile organic structures in the foreground with rose (#b85578), dusty pink, and soft mauve gradients, glowing rose-toned particles, and flowing energy effects in the background. Vivid saturated colors dominated by rose pink #b85578, dusty rose, and warm mauve with contrasting golden and peachy accents for vitality energy and feminine strength. Studio-quality cinematic lighting with soft global illumination, subtle translucent glow on organic structures, and crisp highlights making everything pristine and elegant. Empowering, revealing mood visualizing hidden vitality processes inside the feminine body, instantly readable at thumbnail size. Overall color palette strictly rose #b85578, soft pinks, dusty rose, and warm mauve hues with elegant atmospheric lighting, absolutely NO blues or greens."
            }
            prompt = prompts.get(brand_name, prompts["gymcollege"])
        
        # Add unique identifier to ensure different images each time
        unique_id = str(uuid.uuid4())[:8]
        prompt = f"{prompt} [ID: {unique_id}]"
        
        print(f"🎨 Generating AI background for brand: {brand_name}")
        print(f"📝 Prompt length: {len(prompt)} chars")
        print(f"🆔 Unique ID: {unique_id}")
        
        if progress_callback:
            progress_callback(f"Calling DALL-E 3 API for {brand_name}...", 30)
        
        try:
            # Generate image using DALL-E 3
            api_start = time.time()
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # Closest to our 1080x1920 ratio
                quality="standard",
                n=1,
            )
            api_duration = time.time() - api_start
            
            if progress_callback:
                progress_callback(f"API responded in {api_duration:.1f}s, downloading image...", 60)
            
            # Download the generated image
            download_start = time.time()
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            download_duration = time.time() - download_start
            
            if progress_callback:
                progress_callback(f"Downloaded in {download_duration:.1f}s, resizing...", 80)
            
            # Resize to exact dimensions
            image = image.resize((REEL_WIDTH, REEL_HEIGHT), Image.Resampling.LANCZOS)
            
            total_duration = time.time() - start_time
            
            if progress_callback:
                progress_callback(f"Background generated in {total_duration:.1f}s total", 100)
            
            print(f"✅ Successfully generated {REEL_WIDTH}x{REEL_HEIGHT} background for {brand_name}")
            print(f"⏱️  Total time: {total_duration:.1f}s (API: {api_duration:.1f}s, Download: {download_duration:.1f}s)")
            
            return image
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate AI background: {str(e)}")
