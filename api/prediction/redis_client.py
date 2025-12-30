import redis
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class RedisHistoryManager:
    """Manage prediction history in Redis container"""
    
    def __init__(self):
        # Use Redis container connection
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        
        try:
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
            
        self.ttl = 7 * 24 * 60 * 60  # 7 days
        self.max_per_session = 100
    
    def add_history(self, session_id: str, data: Dict) -> str:
        """Add prediction to history"""
        history_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        record = {
            'id': history_id,
            'timestamp': timestamp,
            **data
        }
        
        # Save individual record
        key = f"history:{session_id}:{history_id}"
        self.client.setex(key, self.ttl, json.dumps(record))
        
        # Add to session list
        list_key = f"history:{session_id}:list"
        self.client.lpush(list_key, history_id)
        self.client.expire(list_key, self.ttl)
        
        # Trim to max size
        self.client.ltrim(list_key, 0, self.max_per_session - 1)
        
        logger.info(f"Added history {history_id} for session {session_id}")
        return history_id
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get history for session"""
        list_key = f"history:{session_id}:list"
        history_ids = self.client.lrange(list_key, 0, limit - 1)
        
        records = []
        for history_id in history_ids:
            key = f"history:{session_id}:{history_id}"
            data = self.client.get(key)
            if data:
                records.append(json.loads(data))
        
        return records
    
    def delete_history(self, session_id: str, history_id: str) -> bool:
        """Delete specific history item"""
        key = f"history:{session_id}:{history_id}"
        list_key = f"history:{session_id}:list"
        
        # Remove from list
        self.client.lrem(list_key, 0, history_id)
        # Delete record
        result = self.client.delete(key)
        
        return result > 0
    
    def clear_history(self, session_id: str) -> int:
        """Clear all history for session"""
        list_key = f"history:{session_id}:list"
        history_ids = self.client.lrange(list_key, 0, -1)
        
        count = 0
        for history_id in history_ids:
            key = f"history:{session_id}:{history_id}"
            count += self.client.delete(key)
        
        self.client.delete(list_key)
        logger.info(f"Cleared {count} history items for session {session_id}")
        return count
    
    def health_check(self) -> bool:
        """Check Redis connection"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
