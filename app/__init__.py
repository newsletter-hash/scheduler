"""Reels automation application package."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)  # override=True ensures .env values take precedence
    print(f"✅ Loaded environment from: {env_path}")
else:
    print(f"⚠️  No .env file found at: {env_path}")
