from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from database import get_db
from models import PageView, User, StudyLog, Word

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/track")
def track_pageview(request: Request, path: str = "/", db: Session = Depends(get_db)):
    """Track a page view"""
    pv = PageView(
        path=path,
        user_agent=(request.headers.get("user-agent", "") or "")[:500],
        ip_address=request.client.host if request.client else "",
    )
    db.add(pv)
    db.commit()
    return {"ok": True}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    """Admin dashboard: user count, daily/weekly views, active users"""
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    today_start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Total users
    total_users = db.query(User).count()

    # Users registered this week
    week_ago_dt = today_start_dt - timedelta(days=7)
    new_users_this_week = db.query(User).filter(User.created_at >= week_ago_dt).count()

    # Total page views
    total_views = db.query(PageView).count()

    # Today's views
    views_today = db.query(PageView).filter(PageView.created_at >= today_start_dt).count()

    # Yesterday's views
    yesterday_start_dt = today_start_dt - timedelta(days=1)
    views_yesterday = db.query(PageView).filter(
        PageView.created_at >= yesterday_start_dt,
        PageView.created_at < today_start_dt
    ).count()

    # Last 7 days views (per day)
    daily_views = []
    for i in range(6, -1, -1):
        day_start = today_start_dt - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.query(PageView).filter(
            PageView.created_at >= day_start,
            PageView.created_at < day_end
        ).count()
        daily_views.append({"date": day_start.strftime("%m-%d"), "views": count})  # MM-DD

    # Active users today (users who studied)
    active_today = db.query(StudyLog).filter(StudyLog.date == today).count()

    # Total words in the system
    total_words = db.query(Word).count()

    # Premium users
    premium_users = db.query(User).filter(User.is_premium == True).count()

    return {
        "total_users": total_users,
        "new_users_this_week": new_users_this_week,
        "total_views": total_views,
        "views_today": views_today,
        "views_yesterday": views_yesterday,
        "daily_views": daily_views,
        "active_users_today": active_today,
        "total_words": total_words,
        "premium_users": premium_users,
    }


@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    """List all users with their word count and review stats"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        word_count = db.query(Word).filter(Word.user_id == u.id).count()
        total_reviews = db.query(func.coalesce(func.sum(StudyLog.words_reviewed), 0)).filter(StudyLog.user_id == u.id).scalar()
        result.append({
            "id": u.id,
            "phone": u.phone[:3] + "****" + u.phone[-4:],  # mask phone
            "name": u.name,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "is_premium": u.is_premium,
            "premium_tier": u.premium_tier,
            "word_count": word_count,
            "total_reviews": total_reviews,
        })
    return result
