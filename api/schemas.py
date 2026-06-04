from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ---- User ----
class UserRegister(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    password: str = Field(..., min_length=6)
    name: Optional[str] = ""

class UserLogin(BaseModel):
    phone: str
    password: str

class UserResetPassword(BaseModel):
    phone: str
    new_password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    phone: str
    name: str
    is_premium: bool
    premium_tier: str
    premium_expires: Optional[datetime] = None
    created_at: datetime

    class Config: from_attributes = True


# ---- Word ----
class WordCreate(BaseModel):
    word: str
    definition: Optional[str] = ""
    context_sentence: Optional[str] = ""
    tags: Optional[str] = "[]"
    starred: Optional[bool] = False
    source_image: Optional[str] = None
    source_filename: Optional[str] = None

class WordUpdate(BaseModel):
    definition: Optional[str] = None
    context_sentence: Optional[str] = None
    tags: Optional[str] = None
    starred: Optional[bool] = None
    review_count: Optional[int] = None
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    ease_factor: Optional[float] = None
    interval: Optional[int] = None
    srs_level: Optional[int] = None

class WordResponse(BaseModel):
    id: int
    word: str
    definition: str
    context_sentence: Optional[str] = ""
    tags: str
    starred: bool
    review_count: int
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    ease_factor: float
    interval: int
    srs_level: int
    created_at: datetime
    source_image: Optional[str] = None

    class Config: from_attributes = True

class BatchWordsCreate(BaseModel):
    words: List[WordCreate]


# ---- Study Log ----
class StudyLogCreate(BaseModel):
    date: str
    words_reviewed: int = 0
    words_remembered: int = 0
    words_forgot: int = 0
    streak_current: int = 0

class StudyLogResponse(BaseModel):
    id: int
    date: str
    words_reviewed: int
    words_remembered: int
    words_forgot: int
    streak_current: int

    class Config: from_attributes = True

class StatsResponse(BaseModel):
    total_words: int
    words_today: int
    words_this_week: int
    total_reviews: int
    mastered_count: int
    streak_days: int
    daily_stats: List[dict]
