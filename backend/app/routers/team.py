from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.security import require_admin
from ..database import get_db
from ..models import User
from ..schemas.profile import MatchmakerOut
from ._helpers import list_matchmakers_with_counts

router = APIRouter(tags=["team"])


@router.get("/matchmakers", response_model=list[MatchmakerOut])
def list_matchmakers(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return [
        MatchmakerOut(id=m.id, display_name=m.display_name, client_count=count)
        for m, count in list_matchmakers_with_counts(db)
    ]
