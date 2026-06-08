from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..database import get_db
from ..models import Note, User
from ..schemas.note import NoteCreate, NoteOut
from ..services.activity import client_label, log
from ._helpers import load_client

router = APIRouter(prefix="/customers", tags=["notes"])


@router.post("/{customer_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def add_note(customer_id: int, payload: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = load_client(db, user, customer_id)
    note = Note(customer_id=client.id, body=payload.body, author_id=user.id)
    db.add(note)
    # Log the action only, never the note content.
    log(db, user, "note_added", f"{user.display_name} added a note to {client_label(client)}", customer_id=client.id)
    db.commit()
    db.refresh(note)
    return NoteOut(id=note.id, body=note.body, author_name=user.display_name, created_at=note.created_at)
