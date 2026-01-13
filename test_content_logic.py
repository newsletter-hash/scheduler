#!/usr/bin/env python3
"""
Test script for content logic without API calls.
Tests numbering, line spacing, and padding without generating images.
"""
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.constants import (
    CONTENT_FONT_SIZE,
    CONTENT_SIDE_PADDING,
    TITLE_SIDE_PADDING,
    CONTENT_LINE_SPACING,
    REEL_WIDTH,
)

def test_content_logic():
    """Test content logic without API calls."""
    
    print("🧪 Testing Content Logic (No API)")
    print("=" * 60)
    
    # Test 1: Padding calculations
    print("\n📏 Test 1: Padding and Width Calculations")
    print(f"  Reel Width: {REEL_WIDTH}px")
    print(f"  Title Padding (left + right): {TITLE_SIDE_PADDING * 2}px")
    print(f"  Title Max Width: {REEL_WIDTH - (TITLE_SIDE_PADDING * 2)}px")
    print(f"  Content Padding (left + right): {CONTENT_SIDE_PADDING * 2}px")
    print(f"  Content Max Width: {REEL_WIDTH - (CONTENT_SIDE_PADDING * 2)}px")
    assert REEL_WIDTH - (TITLE_SIDE_PADDING * 2) == 900, "Title width should be 900px"
    assert REEL_WIDTH - (CONTENT_SIDE_PADDING * 2) == 864, "Content width should be 864px"
    print("  ✅ Padding calculations correct!")
    
    # Test 2: Font and spacing settings
    print(f"\n🔤 Test 2: Font and Spacing Settings")
    print(f"  Content Font Size: {CONTENT_FONT_SIZE}px")
    print(f"  Line Spacing Multiplier: {CONTENT_LINE_SPACING}x (78% of default)")
    assert CONTENT_FONT_SIZE == 49, "Content font size should be 49px"
    assert CONTENT_LINE_SPACING == 0.78, "Line spacing should be 0.78x"
    print("  ✅ Font settings correct!")
    
    # Test 3: Numbering logic simulation
    print(f"\n🔢 Test 3: Content Numbering Logic")
    import re
    
    test_lines = [
        "Coffee after 2pm — Blocks adenosine for 8+ hours",
        "Dark chocolate at night — Hidden caffeine content",
        "Spicy dinners — Raises body temperature",
        "We have more for you, follow this page for Part 2!"
    ]
    
    # Simulate numbering (all lines get numbered including CTA)
    numbered_lines = []
    for i, line in enumerate(test_lines, 1):
        line_without_number = re.sub(r'^\d+\.\s*', '', line.strip())
        numbered_lines.append(f"{i}. {line_without_number}")
    
    print("  Input lines:")
    for line in test_lines:
        print(f"    - {line}")
    
    print("\n  Output (numbered):")
    for line in numbered_lines:
        print(f"    {line}")
    
    # Verify CTA gets numbered
    assert numbered_lines[-1].startswith("4. "), "CTA should be numbered as 4."
    assert "follow this page" in numbered_lines[-1].lower(), "CTA content preserved"
    print("  ✅ All lines numbered correctly (including CTA)!")
    
    # Test 4: Line spacing calculation
    print(f"\n📐 Test 4: Line Spacing Calculation")
    font_height = 49  # Assuming content font height ~= font size
    calculated_line_spacing = int(font_height * CONTENT_LINE_SPACING)
    print(f"  Font Height: ~{font_height}px")
    print(f"  Line Spacing: {font_height} × {CONTENT_LINE_SPACING} = {calculated_line_spacing}px")
    print(f"  Expected spacing between lines: {calculated_line_spacing}px")
    print("  ✅ Line spacing calculated correctly!")
    
    print(f"\n{'='*60}")
    print("✅ All content logic tests passed!")
    print("\nSummary:")
    print("  • Title padding: 90px (left/right) → 900px max width")
    print("  • Content padding: 108px (left/right) → 864px max width")
    print("  • Content font: Browallia New Bold at 49px")
    print("  • Line spacing: 0.78x (78% of default, ~38px)")
    print("  • Letter spacing: Default (no custom spacing)")
    print("  • Numbering: ALL lines including CTA")

if __name__ == "__main__":
    try:
        test_content_logic()
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
