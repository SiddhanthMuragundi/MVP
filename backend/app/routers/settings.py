from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.crypto import decrypt_key, encrypt_key, mask_key
from ..core.security import require_admin
from ..database import get_db
from ..enums import LLMProvider
from ..models import LLMSetting, User
from ..schemas.settings import LLMSettingOut, LLMSettingUpdate, ModelListOut
from ..services import llm
from ..services.activity import log

router = APIRouter(prefix="/settings", tags=["settings"])


def _to_out(row: LLMSetting | None) -> LLMSettingOut:
    if row is None or not row.provider:
        return LLMSettingOut(provider=None, model=None, configured=False, masked_key=None, updated_at=None)
    masked = mask_key(decrypt_key(row.api_key_encrypted)) if row.api_key_encrypted else None
    configured = bool(row.provider and row.api_key_encrypted and row.model)
    return LLMSettingOut(
        provider=row.provider,
        model=row.model,
        configured=configured,
        masked_key=masked,
        updated_at=row.updated_at,
    )


@router.get("/llm", response_model=LLMSettingOut)
def get_llm_settings(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return _to_out(db.get(LLMSetting, 1))


@router.put("/llm", response_model=LLMSettingOut)
def update_llm_settings(payload: LLMSettingUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    row = db.get(LLMSetting, 1)

    if payload.api_key:
        key_plain = payload.api_key
    elif row is not None and row.api_key_encrypted:
        key_plain = decrypt_key(row.api_key_encrypted)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "API key is required")

    try:
        available = llm.list_models(payload.provider, key_plain)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Could not validate provider/key")

    model = payload.model or (available[0] if available else None)
    if model is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No model available for this provider")
    if available and model not in available:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Selected model is not available for this provider")

    if row is None:
        row = LLMSetting(id=1)
        db.add(row)
    row.provider = payload.provider
    row.api_key_encrypted = encrypt_key(key_plain)
    row.model = model
    row.updated_by = admin.id
    row.updated_at = datetime.now(timezone.utc)
    log(db, admin, "settings_updated", f"{admin.display_name} updated AI settings ({payload.provider.value})")
    db.commit()
    return _to_out(row)


@router.delete("/llm", response_model=LLMSettingOut)
def remove_llm_settings(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Clear the stored provider/key/model. The app falls back to built-in templates."""
    row = db.get(LLMSetting, 1)
    if row is not None:
        db.delete(row)
        log(db, admin, "settings_updated", f"{admin.display_name} removed the AI configuration")
        db.commit()
    return _to_out(None)


@router.get("/llm/models", response_model=ModelListOut)
def list_llm_models(
    provider: LLMProvider = Query(...),
    api_key: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    key = api_key
    if not key:
        row = db.get(LLMSetting, 1)
        if row and row.provider == provider and row.api_key_encrypted:
            key = decrypt_key(row.api_key_encrypted)
    if not key:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Provide an API key")

    try:
        return ModelListOut(models=llm.list_models(provider, key))
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Could not load models for this provider/key")
