"""
AI background generation service using deAPI.
"""
import os
import uuid
import time
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image
from app.core.constants import REEL_WIDTH, REEL_HEIGHT


class AIBackgroundGenerator:
    """Service for generating AI backgrounds for dark mode using deAPI."""
    
    def __init__(self):
        """Initialize the AI background generator with deAPI client."""
        api_key = os.getenv("DEAPI_API_KEY")
        if not api_key:
            raise ValueError("DEAPI_API_KEY not found in environment variables")
        self.api_key = api_key
        self.base_url = "https://api.deapi.ai/api/v1/client"
    
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
                "gymcollege": " Overall color palette MUST be dominated by dark navy blue tones specifically #00435c (dark navy blue), absolutely NO green tones, use only deep midnight blues, dark navy blues, and steel blue hues with moody dark atmospheric lighting. Think deep ocean depths and midnight environments.",
                "healthycollege": " Overall color palette dominated by dark green tones specifically #004f00, deep forest greens, and rich emerald green hues with moody atmospheric lighting. Think dense forest and natural wellness environments.",
                "vitalitycollege": " Overall color palette MUST be dominated by vivid turquoise tones specifically #028f7a, bright teals, cyan, and aqua hues with vibrant atmospheric lighting. Think energetic tropical waters and dynamic vitality energy. Absolutely NO pinks or roses.",
                "longevitycollege": " Overall color palette MUST be dominated by light blue and cyan tones specifically #00c9ff (light blue), sky blues, bright cyan tones, and luminous blue hues with clear atmospheric lighting. Think clear skies, pristine waters, and cellular clarity. Absolutely NO warm tones like amber, gold, or yellows."
            }
            prompt = user_prompt + color_adaptations.get(brand_name, color_adaptations["gymcollege"])
        else:
            # Default prompts - FULL FRAME UTILIZATION, NO CENTERED SUBJECTS, NO DARK BACKGROUNDS
            prompts = {
                "gymcollege": "An ultra-detailed, edge-to-edge composition completely filling the vertical 9:16 frame with NO empty space or dark backgrounds. The scene shows an extreme close-up macro view of anatomical muscle fibers, protein chains, and molecular structures arranged in diagonal, asymmetric layers from corner to corner. NO centered subject - elements flow dynamically across the entire frame creating natural depth and movement. Foreground features sharp, tactile cellular details with dark navy blue (#00435c) and deep midnight blue tones, middle ground shows glowing energy particles and ATP molecules, background has layered molecular structures creating depth. Rich, saturated color palette dominated by dark navy #00435c with vivid warm orange and yellow energy accents for contrast. Professional studio lighting with soft global illumination ensuring every corner is visible and detailed. Scientific, powerful mood showing the athletic body's hidden processes. Absolutely NO green tones, NO centered compositions, NO dark empty backgrounds - every pixel utilized with intentional visual information.",
                
                "healthycollege": "An ultra-detailed, edge-to-edge composition completely filling the vertical 9:16 frame with NO empty space or dark backgrounds. The scene shows an extreme close-up macro view of vibrant superfood textures, fresh produce cross-sections, and digestive cellular structures arranged in diagonal, asymmetric layers from corner to corner. NO centered subject - elements flow dynamically across the entire frame creating natural depth and movement. Foreground features sharp, tactile organic textures with dark green (#004f00) and deep forest green tones, middle ground shows glowing nutrient molecules and antioxidant particles, background has layered vitamin structures creating depth. Rich, saturated color palette dominated by dark green #004f00 with vivid warm red, orange, and yellow produce accents for contrast. Professional studio lighting with soft global illumination ensuring every corner is visible and detailed. Scientific, natural mood showing the body's wellness processes. NO centered compositions, NO dark empty backgrounds - every pixel utilized with intentional visual information.",
                
                "vitalitycollege": "An ultra-detailed, edge-to-edge composition completely filling the vertical 9:16 frame with NO empty space or dark backgrounds. The scene shows an extreme close-up macro view of cellular rejuvenation structures, energy spirals, and vitality streams arranged in diagonal, asymmetric layers from corner to corner. NO centered subject - elements flow dynamically across the entire frame creating natural depth and movement. Foreground features sharp, tactile organic structures with vivid turquoise (#028f7a), bright teal, and cyan tones, middle ground shows glowing energy particles and dynamic vitality elements, background has layered cellular patterns creating depth. Rich, saturated color palette dominated by vivid turquoise #028f7a with warm golden and coral energy accents for contrast. Professional studio lighting with soft global illumination ensuring every corner is visible and detailed. Dynamic, invigorating mood showing vitality and life force. Absolutely NO pink or rose tones, NO centered compositions, NO dark empty backgrounds - every pixel utilized with intentional visual information.",
                
                "longevitycollege": "An ultra-detailed, edge-to-edge composition completely filling the vertical 9:16 frame with NO empty space or dark backgrounds. The scene shows an extreme close-up macro view of mitochondria, DNA helixes, and telomere structures arranged in diagonal, asymmetric layers from corner to corner. NO centered subject - elements flow dynamically across the entire frame creating natural depth and movement. Foreground features sharp, tactile cellular details with light blue (#00c9ff), sky blue, and bright cyan tones, middle ground shows glowing ATP molecules and cellular energy particles, background has layered molecular structures creating depth. Rich, saturated color palette dominated by light blue #00c9ff with subtle silver and white accents for clarity. Professional studio lighting with soft global illumination ensuring every corner is visible and detailed. Scientific, calm mood showing longevity and cellular optimization. Absolutely NO warm tones, NO centered compositions, NO dark empty backgrounds - every pixel utilized with intentional visual information."
            }
            prompt = prompts.get(brand_name, prompts["gymcollege"])
        
        # Add unique identifier to ensure different images each time
        unique_id = str(uuid.uuid4())[:8]
        prompt = f"{prompt} [ID: {unique_id}]"
        
        print(f"\n{'='*80}")
        print(f"🎨 AI BACKGROUND GENERATION STARTED")
        print(f"{'='*80}")
        print(f"🏷️  Brand: {brand_name}")
        print(f"📝 Prompt length: {len(prompt)} chars")
        print(f"🆔 Unique ID: {unique_id}")
        print(f"📄 Full prompt: {prompt[:200]}...")  # Show first 200 chars
        print(f"{'='*80}\n")
        
        if progress_callback:
            progress_callback(f"Calling deAPI (FLUX.1-schnell) for {brand_name}...", 30)
        
        try:
            # Generate image using deAPI with FLUX.1-schnell (cheapest model)
            api_start = time.time()
            
            # Calculate dimensions (FLUX.1-schnell requires multiples of 128)
            # Our target is 1080x1920, round to nearest valid dimensions
            width = ((REEL_WIDTH + 127) // 128) * 128  # Round up to nearest 128
            height = ((REEL_HEIGHT + 127) // 128) * 128  # Round up to nearest 128
            
            print(f"📐 Target dimensions: {REEL_WIDTH}x{REEL_HEIGHT}")
            print(f"📐 Rounded dimensions: {width}x{height} (multiples of 128 required)")
            
            # Submit generation request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "model": "Flux1schnell",  # Cheapest model at $0.00136 for 512x512, 4 steps
                "width": width,
                "height": height,
                "steps": 4,  # Max steps for Flux1schnell is 10, using 4 for speed/cost
                "guidance": 0,  # Flux1schnell does not support guidance (must be 0)
                "seed": int(unique_id, 16) % (2**31),  # Convert unique_id to seed
                "loras": []
            }
            
            print(f"📊 API Request Parameters:")
            print(f"   Model: {payload['model']}")
            print(f"   Dimensions: {width}x{height}")
            print(f"   Steps: {payload['steps']}")
            print(f"   Seed: {payload['seed']}")
            print(f"🌐 Sending POST request to {self.base_url}/txt2img...")
            
            response = requests.post(
                f"{self.base_url}/txt2img",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            print(f"📡 Response status code: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            # Extract request_id from response (can be at root or nested in 'data')
            request_id = result.get("request_id") or result.get("data", {}).get("request_id")
            if not request_id:
                print(f"❌ ERROR: No request_id in response!")
                print(f"📄 Response: {result}")
                raise RuntimeError(f"No request_id in response: {result}")
            
            print(f"✅ Generation queued successfully!")
            print(f"📝 Request ID: {request_id}")
            print(f"⏳ Polling for results...")
            
            if progress_callback:
                progress_callback(f"Waiting for generation (ID: {request_id})...", 50)
            
            # Poll for results
            max_attempts = 90  # 90 attempts x 2 seconds = 3 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(2)  # Wait 2 seconds between polls
                attempt += 1
                
                status_response = requests.get(
                    f"{self.base_url}/request-status/{request_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30
                )
                status_response.raise_for_status()
                status_result = status_response.json()
                
                # Extract data from response (deAPI nests everything in 'data')
                data = status_result.get("data", {})
                status = data.get("status")
                progress = data.get("progress", 0)
                
                if status == "done":
                    # Get result_url from the response
                    result_url = data.get("result_url")
                    if not result_url:
                        raise RuntimeError(f"No result_url in completed result: {status_result}")
                    
                    api_duration = time.time() - api_start
                    
                    if progress_callback:
                        progress_callback(f"Generation completed in {api_duration:.1f}s, downloading...", 70)
                    
                    # Download the generated image
                    download_start = time.time()
                    image_response = requests.get(result_url, timeout=60)
                    image_response.raise_for_status()
                    image = Image.open(BytesIO(image_response.content))
                    download_duration = time.time() - download_start
                    
                    if progress_callback:
                        progress_callback(f"Downloaded in {download_duration:.1f}s, resizing...", 85)
                    
                    # Resize to exact dimensions if needed
                    if image.size != (REEL_WIDTH, REEL_HEIGHT):
                        image = image.resize((REEL_WIDTH, REEL_HEIGHT), Image.Resampling.LANCZOS)
                    
                    # Darken the image by 5%
                    from PIL import ImageEnhance
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(0.95)  # 95% brightness = 5% darker
                    
                    total_duration = time.time() - start_time
                    
                    if progress_callback:
                        progress_callback(f"Background generated in {total_duration:.1f}s total", 100)
                    
                    print(f"✅ Successfully generated {REEL_WIDTH}x{REEL_HEIGHT} background for {brand_name}")
                    print(f"⏱️  Total time: {total_duration:.1f}s (API: {api_duration:.1f}s, Download: {download_duration:.1f}s)")
                    
                    return image
                
                elif status == "failed":
                    error_msg = status_result.get("error", "Unknown error")
                    raise RuntimeError(f"Generation failed: {error_msg}")
                
                elif status in ["pending", "processing"]:
                    if progress_callback:
                        progress_callback(f"Generating... (attempt {attempt}/{max_attempts})", 30 + (attempt * 20 // max_attempts))
                    continue
                
                else:
                    raise RuntimeError(f"Unknown status: {status}")
            
            raise RuntimeError(f"Generation timed out after {max_attempts} attempts (~{max_attempts * 2}s). The deAPI server may be overloaded. Try again or use a shorter prompt.")
            
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"Network timeout connecting to deAPI: {str(e)}. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error with deAPI: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate AI background: {str(e)}")
