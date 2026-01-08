"""
Simple SQLite database for tracking reel generation history and state.
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json


class ReelDatabase:
    """Simple database for reel generation tracking."""
    
    def __init__(self, db_path: str = "reels_history.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    variant TEXT NOT NULL,
                    ai_prompt TEXT,
                    status TEXT NOT NULL,
                    thumbnail_path TEXT,
                    video_path TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    error TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generation_progress (
                    generation_id TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    progress INTEGER NOT NULL,
                    message TEXT,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (generation_id) REFERENCES generations(id)
                )
            """)
            conn.commit()
    
    def create_generation(self, generation_id: str, title: str, content: List[str], 
                         brand: str, variant: str, ai_prompt: Optional[str] = None) -> str:
        """Create a new generation record."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO generations 
                (id, title, content, brand, variant, ai_prompt, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                generation_id,
                title,
                json.dumps(content),
                brand,
                variant,
                ai_prompt,
                'generating',
                datetime.now().isoformat()
            ))
            conn.commit()
        return generation_id
    
    def update_progress(self, generation_id: str, stage: str, progress: int, message: str = None):
        """Update generation progress."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO generation_progress
                (generation_id, stage, progress, message, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (generation_id, stage, progress, message, datetime.now().isoformat()))
            conn.commit()
    
    def update_generation_status(self, generation_id: str, status: str, 
                                 thumbnail_path: str = None, video_path: str = None,
                                 error: str = None):
        """Update generation status and paths."""
        updates = ["status = ?"]
        params = [status]
        
        if thumbnail_path:
            updates.append("thumbnail_path = ?")
            params.append(thumbnail_path)
        
        if video_path:
            updates.append("video_path = ?")
            params.append(video_path)
        
        if error:
            updates.append("error = ?")
            params.append(error)
        
        if status == 'completed':
            updates.append("completed_at = ?")
            params.append(datetime.now().isoformat())
        
        params.append(generation_id)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"""
                UPDATE generations
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            conn.commit()
    
    def get_generation(self, generation_id: str) -> Optional[Dict]:
        """Get generation by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM generations WHERE id = ?
            """, (generation_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['content'] = json.loads(data['content'])
                return data
            return None
    
    def get_progress(self, generation_id: str) -> Optional[Dict]:
        """Get current progress for a generation."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM generation_progress WHERE generation_id = ?
            """, (generation_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_recent_generations(self, limit: int = 10) -> List[Dict]:
        """Get recent generations."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM generations
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                data['content'] = json.loads(data['content'])
                results.append(data)
            return results
    
    def get_active_generation(self) -> Optional[Dict]:
        """Get currently generating reel (if any)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM generations
                WHERE status = 'generating'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['content'] = json.loads(data['content'])
                return data
            return None
