from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from _database import get_db
from _models import Word, StudyLog, User
from _auth import get_current_user

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def get_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    total_words = db.query(Word).filter(Word.user_id == user.id).count()
    mastered = db.query(Word).filter(Word.user_id == user.id, Word.srs_level >= 3).count()

    # Today's reviews
    today_log = db.query(StudyLog).filter(
        StudyLog.user_id == user.id, StudyLog.date == today
    ).first()
    words_today = today_log.words_reviewed if today_log else 0

    # Last 7 days
    recent_logs = (
        db.query(StudyLog)
        .filter(StudyLog.user_id == user.id, StudyLog.date >= week_ago)
        .order_by(StudyLog.date.desc())
        .all()
    )
    words_this_week = sum(log.words_reviewed for log in recent_logs)
    total_reviews = sum(log.words_reviewed for log in db.query(StudyLog).filter(StudyLog.user_id == user.id).all())

    # Streak
    streak = 0
    logs = db.query(StudyLog).filter(StudyLog.user_id == user.id).order_by(StudyLog.date.desc()).all()
    for log in logs:
        if log.words_reviewed > 0:
            streak += 1
        else:
            break

    # Daily stats for chart
    daily_stats = [
        {"date": log.date, "reviewed": log.words_reviewed, "remembered": log.words_remembered}
        for log in recent_logs
    ]

    return {
        "total_words": total_words,
        "words_today": words_today,
        "words_this_week": words_this_week,
        "total_reviews": total_reviews,
        "mastered_count": mastered,
        "streak_days": streak,
        "daily_stats": daily_stats,
    }


@router.post("/log")
def log_study(data: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Record a study session."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log = db.query(StudyLog).filter(StudyLog.user_id == user.id, StudyLog.date == today).first()
    if log:
        log.words_reviewed += data.get("words_reviewed", 0)
        log.words_remembered += data.get("words_remembered", 0)
        log.words_forgot += data.get("words_forgot", 0)
    else:
        log = StudyLog(
            user_id=user.id,
            date=today,
            words_reviewed=data.get("words_reviewed", 0),
            words_remembered=data.get("words_remembered", 0),
            words_forgot=data.get("words_forgot", 0),
            streak_current=data.get("streak_current", 0),
        )
        db.add(log)
    db.commit()
    return {"message": "ok"}
