from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from _database import get_db
from _models import Word, User
from _schemas import WordCreate, WordUpdate, WordResponse, BatchWordsCreate
from _auth import get_current_user

router = APIRouter(prefix="/api/words", tags=["words"])


@router.get("", response_model=List[WordResponse])
def list_words(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    starred_only: bool = Query(False),
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    limit: int = Query(500, le=2000),
):
    q = db.query(Word).filter(Word.user_id == user.id)
    if starred_only:
        q = q.filter(Word.starred == True)
    if search:
        like = f"%{search}%"
        q = q.filter((Word.word.ilike(like)) | (Word.definition.ilike(like)))
    if tag:
        q = q.filter(Word.tags.contains(tag))
    return q.order_by(Word.created_at.desc()).limit(limit).all()


@router.post("", response_model=WordResponse, status_code=201)
def create_word(
    data: WordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existing = db.query(Word).filter(Word.user_id == user.id, Word.word == data.word).first()
    if existing:
        raise HTTPException(409, "该单词已存在")
    word = Word(user_id=user.id, **data.model_dump())
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


@router.post("/batch", status_code=201)
def batch_create(
    data: BatchWordsCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    added, skipped = 0, 0
    for w in data.words:
        if db.query(Word).filter(Word.user_id == user.id, Word.word == w.word).first():
            skipped += 1
            continue
        word = Word(user_id=user.id, **w.model_dump())
        db.add(word)
        added += 1
    db.commit()
    return {"added": added, "skipped": skipped}


@router.put("/{word_id}", response_model=WordResponse)
def update_word(
    word_id: int,
    data: WordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    word = db.query(Word).filter(Word.id == word_id, Word.user_id == user.id).first()
    if not word:
        raise HTTPException(404, "单词不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(word, key, val)
    db.commit()
    db.refresh(word)
    return word


@router.delete("/{word_id}")
def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    word = db.query(Word).filter(Word.id == word_id, Word.user_id == user.id).first()
    if not word:
        raise HTTPException(404, "单词不存在")
    db.delete(word)
    db.commit()
    return {"message": "已删除"}


@router.post("/sync", response_model=List[WordResponse])
def sync_words(
    local_words: List[WordCreate],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Sync: upload all local words, get back the merged cloud version."""
    existing = {w.word: w for w in db.query(Word).filter(Word.user_id == user.id).all()}
    for lw in local_words:
        if lw.word not in existing:
            word = Word(user_id=user.id, **lw.model_dump())
            db.add(word)
            existing[lw.word] = word
    db.commit()
    return [WordResponse.model_validate(w) for w in existing.values()]
