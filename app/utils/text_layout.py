"""
Text layout and wrapping utilities for image generation.
"""
from typing import List, Tuple
from PIL import ImageFont, ImageDraw, Image


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """
    Wrap text to fit within a specified width.
    
    Args:
        text: The text to wrap
        font: Font to use for measuring
        max_width: Maximum width in pixels
        
    Returns:
        List of wrapped text lines
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Try adding the word to the current line
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            # Current line is full, start a new line
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                # Single word is too long, add it anyway
                lines.append(word)
    
    # Add the last line
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines if lines else [""]


def get_text_dimensions(text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """
    Get the width and height of text when rendered.
    
    Args:
        text: The text to measure
        font: Font to use for measuring
        
    Returns:
        Tuple of (width, height) in pixels
    """
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def get_multiline_text_dimensions(
    lines: List[str],
    font: ImageFont.FreeTypeFont,
    line_spacing: int = 0
) -> Tuple[int, int]:
    """
    Get the total dimensions of multiline text.
    
    Args:
        lines: List of text lines
        font: Font to use for measuring
        line_spacing: Additional spacing between lines in pixels
        
    Returns:
        Tuple of (width, height) in pixels
    """
    if not lines:
        return 0, 0
    
    max_width = 0
    total_height = 0
    
    for i, line in enumerate(lines):
        width, height = get_text_dimensions(line, font)
        max_width = max(max_width, width)
        total_height += height
        
        # Add line spacing except for the last line
        if i < len(lines) - 1:
            total_height += line_spacing
    
    return max_width, total_height


def draw_text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y_position: int,
    font: ImageFont.FreeTypeFont,
    color: Tuple[int, int, int],
    image_width: int
) -> int:
    """
    Draw text centered horizontally at a given y position.
    
    Args:
        draw: ImageDraw object
        text: Text to draw
        y_position: Y coordinate for the top of the text
        font: Font to use
        color: RGB color tuple
        image_width: Width of the image for centering
        
    Returns:
        The y position after drawing (bottom of the text)
    """
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x_position = (image_width - text_width) // 2
    draw.text((x_position, y_position), text, font=font, fill=color)
    
    return y_position + text_height


def draw_multiline_text_centered(
    draw: ImageDraw.ImageDraw,
    lines: List[str],
    y_position: int,
    font: ImageFont.FreeTypeFont,
    color: Tuple[int, int, int],
    image_width: int,
    line_spacing: int = 0
) -> int:
    """
    Draw multiple lines of text, each centered horizontally.
    
    Args:
        draw: ImageDraw object
        lines: List of text lines
        y_position: Y coordinate for the top of the first line
        font: Font to use
        color: RGB color tuple
        image_width: Width of the image for centering
        line_spacing: Additional spacing between lines
        
    Returns:
        The y position after drawing all lines
    """
    current_y = y_position
    
    for line in lines:
        current_y = draw_text_centered(
            draw, line, current_y, font, color, image_width
        )
        current_y += line_spacing
    
    return current_y


def draw_text_with_background(
    image: Image.Image,
    text: str,
    y_position: int,
    font: ImageFont.FreeTypeFont,
    text_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int, int],
    padding: int = 20,
    spread: int = 0,
    roundness: int = 0
) -> int:
    """
    Draw text with a colored background bar.
    
    Args:
        image: PIL Image object
        text: Text to draw
        y_position: Y coordinate for the center of the background bar
        font: Font to use
        text_color: RGB color for text
        bg_color: RGBA color for background
        padding: Vertical padding around text
        spread: Additional horizontal spread beyond text width (total, split on both sides)
        roundness: Corner radius for rounded rectangle (0 = sharp corners)
        
    Returns:
        The y position after drawing (bottom of the background)
    """
    draw = ImageDraw.Draw(image, 'RGBA')
    
    # Get text dimensions
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate background bar dimensions
    bar_height = text_height + (padding * 2)
    bar_top = y_position - bar_height // 2
    
    # Calculate horizontal position with spread
    bar_left = 0  # Full width bar
    bar_right = image.width
    
    # If spread is specified, create a narrower bar centered on text
    if spread > 0:
        bar_left = (image.width - text_width) // 2 - spread // 2
        bar_right = bar_left + text_width + spread
    
    # Draw background rectangle (with optional rounded corners)
    if roundness > 0:
        draw.rounded_rectangle(
            [(bar_left, bar_top), (bar_right, bar_top + bar_height)],
            radius=roundness,
            fill=bg_color
        )
    else:
        draw.rectangle(
            [(bar_left, bar_top), (bar_right, bar_top + bar_height)],
            fill=bg_color
        )
    
    # Draw text centered on the background
    text_x = (image.width - text_width) // 2
    text_y = bar_top + padding
    
    draw = ImageDraw.Draw(image)  # Switch back to RGB mode for text
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    return bar_top + bar_height


def calculate_total_content_height(
    lines: List[str],
    font: ImageFont.FreeTypeFont,
    line_spacing: int,
    numbered: bool = True
) -> int:
    """
    Calculate the total height needed for content lines.
    
    Args:
        lines: List of content lines
        font: Font to use
        line_spacing: Spacing between lines
        numbered: Whether lines will be numbered
        
    Returns:
        Total height in pixels
    """
    total_height = 0
    
    for i, line in enumerate(lines):
        # Format line with number if needed
        display_line = f"{i+1}. {line}" if numbered else line
        
        # Wrap the line and calculate height
        wrapped = wrap_text(display_line, font, 920)  # Max width with margins
        _, height = get_multiline_text_dimensions(wrapped, font, line_spacing)
        
        total_height += height
        if i < len(lines) - 1:
            total_height += line_spacing
    
    return total_height
