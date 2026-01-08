"""
Call-to-Action (CTA) system with enum-based mappings.
"""
from enum import Enum
from typing import Dict


class CTAType(str, Enum):
    """Enumeration of available CTA types."""
    FOLLOW_PART_2 = "FOLLOW_PART_2"
    FOLLOW_WELLNESS = "FOLLOW_WELLNESS"
    COMMENT_LEAN = "COMMENT_LEAN"
    SAVE_FOR_LATER = "SAVE_FOR_LATER"
    SHARE_WITH_FRIEND = "SHARE_WITH_FRIEND"


# CTA text mapping
CTA_MAP: Dict[CTAType, str] = {
    CTAType.FOLLOW_PART_2: "Follow this page for Part 2.",
    CTAType.FOLLOW_WELLNESS: "If you want to improve your health and wellness, follow this page.",
    CTAType.COMMENT_LEAN: 'Comment "LEAN" and we will send you our most recommended supplement for fat loss!',
    CTAType.SAVE_FOR_LATER: "Save this post for later and share with someone who needs to see this.",
    CTAType.SHARE_WITH_FRIEND: "Share this with a friend who needs motivation!",
}


def get_cta_text(cta_type: CTAType) -> str:
    """
    Get the CTA text for a given CTA type.
    
    Args:
        cta_type: The CTA type enum
        
    Returns:
        The corresponding CTA text
        
    Raises:
        ValueError: If CTA type is not in the mapping
    """
    if cta_type not in CTA_MAP:
        raise ValueError(f"Invalid CTA type: {cta_type}")
    return CTA_MAP[cta_type]
