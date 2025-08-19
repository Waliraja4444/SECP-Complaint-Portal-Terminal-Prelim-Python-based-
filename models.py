from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
import uuid

class ComplaintRequest(BaseModel):
    complaint_text: str

class Classification(BaseModel):
    category: str
    subcategory: str
    nature_of_issue: str
    confidence: float

class ClassificationResponse(BaseModel):
    classification: Classification
    processed_at: str

class Complaint(BaseModel):
    id: str = None
    text: str
    category: str
    subcategory: str
    nature_of_issue: str
    confidence: float = 0.0
    timestamp: datetime
    status: Literal['pending', 'classified', 'reviewed'] = 'classified'
    
    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)

class Stats(BaseModel):
    total: int
    pending: int
    classified: int
    reviewed: int