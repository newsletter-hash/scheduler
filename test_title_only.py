#!/usr/bin/env python3
"""
Quick test script for title rendering without AI background generation.
Tests the new title padding in dark mode.
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.config import BrandType
from app.core.brand_colors import get_brand_colors
from app.core.constants import (
    REEL_WIDTH, REEL_HEIGHT, H_PADDING, BAR_HEIGHT, BAR_GAP, 
    VERTICAL_CORRECTION, FONT_BOLD
)
from app.utils.fonts import load_font
from app.utils.text_layout import wrap_text, get_text_dimensions

def test_title_rendering(variant="dark"):
    """Test title rendering with new padding changes."""
    
    # Test parameters
    title = "FOODS THAT DESTROY YOUR SLEEP QUALITY"
    brand_name = "gymcollege"
    
    print(f"🧪 Testing title: {title}")
    print(f"🎨 Brand: {brand_name}, Variant: {variant}")
    
    # Create background based on variant
    if variant == "light":
        # Light background
        image = Image.new('RGB', (REEL_WIDTH, REEL_HEIGHT), (240, 240, 240))  # Light gray background
    else:
        # Dark background (no AI generation)
        image = Image.new('RGB', (REEL_WIDTH, REEL_HEIGHT), (20, 30, 40))  # Dark blue background
    
    # Get brand colors
    brand_colors = get_brand_colors(brand_name, variant)
    
    # Title processing
    title_upper = title.upper()
    title_start_y = 280
    content_side_margin = 109
    max_content_width = REEL_WIDTH - (content_side_margin * 2)
    
    # Find optimal title font size (start at 56, reduce until fits in 2 lines)
    title_font_size = 56
    title_font = None
    title_wrapped = []
    
    while title_font_size >= 20:
        title_font = load_font(FONT_BOLD, title_font_size)
        title_wrapped = wrap_text(title_upper, title_font, max_content_width)
        
        if len(title_wrapped) <= 2:
            break
        title_font_size -= 1
    
    print(f"📏 Final font size: {title_font_size}px")
    print(f"📝 Title lines: {len(title_wrapped)}")
    for i, line in enumerate(title_wrapped, 1):
        print(f"   Line {i}: '{line}'")
    
    # Title styling colors
    title_bg_color = brand_colors.content_title_bg_color
    title_text_color = brand_colors.content_title_text_color
    
    # Calculate metrics for all lines
    metrics = []
    for line in title_wrapped:
        bbox = title_font.getbbox(line)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        metrics.append((line, w, h, bbox))
        print(f"   '{line}' → {w}px wide")
    
    # Find max text width for stepped effect
    max_text_width = max(w for _, w, _, _ in metrics)
    
    # NEW: Test both old and new padding
    current_padding = H_PADDING  # Now 20px globally
    
    print(f"\n🔄 Testing with current padding:")
    print(f"   Max text width: {max_text_width}px")
    print(f"   Current padding (H_PADDING): {current_padding}px → Total bar width: {max_text_width + current_padding * 2}px")
    
    # Use current padding
    max_bar_width = max_text_width + H_PADDING * 2
    center_x = REEL_WIDTH // 2
    
    # Draw title bars
    draw = ImageDraw.Draw(image, 'RGBA')
    y = title_start_y
    
    print(f"\n🎨 Drawing title bars:")
    
    for i, (line, text_w, _, bbox) in enumerate(metrics):
        # Calculate inset for stepped effect
        inset = (max_text_width - text_w) / 2
        
        # Draw background bar
        bar_left = int(center_x - max_bar_width / 2 + inset)
        bar_right = int(center_x + max_bar_width / 2 - inset)
        bar_top = y
        bar_bottom = y + BAR_HEIGHT
        
        print(f"   Line {i+1}: Bar {bar_right - bar_left}px wide (text: {text_w}px)")
        
        draw.rectangle(
            [(bar_left, bar_top), (bar_right, bar_bottom)],
            fill=title_bg_color
        )
        
        # Calculate precise text position
        glyph_top = bbox[1]
        glyph_height = bbox[3] - bbox[1]
        
        text_x = int(center_x - text_w / 2)
        text_y = int(
            bar_top
            + (BAR_HEIGHT - glyph_height) / 2
            - glyph_top
            + VERTICAL_CORRECTION
            + 1.5  # Move text down 1.5px
        )
        
        draw.text((text_x, text_y), line, font=title_font, fill=title_text_color)
        
        # Move to next line
        y += BAR_HEIGHT + BAR_GAP
    
    # Save test image
    output_path = Path(__file__).parent / "output" / f"test_title_{variant}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, 'PNG', quality=95)
    
    print(f"\n✅ Test image saved: {output_path}")
    print(f"🔍 Open the image to see the title in {variant} mode!")
    
    return output_path

if __name__ == "__main__":
    try:
        # Test both variants
        print("=" * 60)
        test_title_rendering("dark")
        print("\n" + "=" * 60)
        test_title_rendering("light")
        print("\n" + "=" * 60)
        print("✅ Both dark and light mode tests completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)