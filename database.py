import json
import os
from typing import List
from datetime import datetime

from .models import Complaint, Stats

class ComplaintDatabase:
    """Simple file-based database for complaints"""
    
    def __init__(self, db_file: str = "complaints.json"):
        self.db_file = db_file
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump([], f)
    
    async def save_complaint(self, complaint: Complaint):
        """Save a complaint to the database"""
        complaints = await self.get_complaints()
        
        # Convert complaint to dict for JSON serialization
        complaint_dict = {
            "id": complaint.id,
            "text": complaint.text,
            "category": complaint.category,
            "subcategory": complaint.subcategory,
            "nature_of_issue": complaint.nature_of_issue,
            "confidence": complaint.confidence,
            "timestamp": complaint.timestamp.isoformat(),
            "status": complaint.status
        }
        
        complaints.append(complaint_dict)
        
        with open(self.db_file, 'w') as f:
            json.dump(complaints, f, indent=2)
    
    async def get_complaints(self) -> List[dict]:
        """Get all complaints from the database"""
        try:
            with open(self.db_file, 'r') as f:
                complaints = json.load(f)
            
            # Sort by timestamp (newest first)
            complaints.sort(key=lambda x: x['timestamp'], reverse=True)
            return complaints
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    async def get_stats(self) -> Stats:
        """Get complaint statistics"""
        complaints = await self.get_complaints()
        
        total = len(complaints)
        pending = sum(1 for c in complaints if c['status'] == 'pending')
        classified = sum(1 for c in complaints if c['status'] == 'classified')
        reviewed = sum(1 for c in complaints if c['status'] == 'reviewed')
        
        return Stats(
            total=total,
            pending=pending,
            classified=classified,
            reviewed=reviewed
        )