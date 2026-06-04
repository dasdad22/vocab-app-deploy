from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(50), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_premium = Column(Boolean, default=False)
    premium_expires = Column(DateTime, nullable=True)
    premium_tier = Column(String(20), default="free")

    words = relationship("Word", back_populates="user", cascade="all, delete-orphan")
    study_logs = relationship("StudyLog", back_populates="user", cascade="all, delete-orphan")


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word = Column(String(100), nullable=False)
    definition = Column(Text, default="")
    context_sentence = Column(Text, default="")
    tags = Column(Text, default="[]")          # JSON array string
    starred = Column(Boolean, default=False)
    review_count = Column(Integer, default=0)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)
    srs_level = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source_image = Column(Text, nullable=True)   # base64 or URL
    source_filename = Column(String(200), nullable=True)

    user = relationship("User", back_populates="words")


class StudyLog(Base):
    __tablename__ = "study_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(String(10), nullable=False)      # YYYY-MM-DD
    words_reviewed = Column(Integer, default=0)
    words_remembered = Column(Integer, default=0)
    words_forgot = Column(Integer, default=0)
    streak_current = Column(Integer, default=0)

    user = relationship("User", back_populates="study_logs")


class PageView(Base):
    __tablename__ = "page_views"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(200), default="/")
    user_agent = Column(String(500), default="")
    ip_address = Column(String(50), default="")
    session_id = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
