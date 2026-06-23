from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import require_roles
from app.db.session import get_db
from app.models.dam import Dam, DamDocument, User, UserRole
from app.schemas.dam import DamDocumentOut
from app.services import log_audit


router = APIRouter()


@router.post("/{dam_id}/documents", response_model=DamDocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    dam_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer, UserRole.inspector))],
    document_type: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
) -> DamDocument:
    if not db.get(Dam, dam_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dam not found")

    upload_dir = Path(settings.upload_dir) / dam_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4()}-{Path(file.filename or 'document.bin').name}"
    file_path = upload_dir / safe_name
    file_path.write_bytes(await file.read())

    document = DamDocument(
        dam_id=dam_id,
        document_type=document_type,
        title=title,
        file_url=f"/uploads/{dam_id}/{safe_name}",
        file_name=file.filename,
        mime_type=file.content_type,
        uploaded_by=current_user.user_id,
    )
    db.add(document)
    log_audit(db, request, current_user, "upload_document", "dam_document", dam_id, dam_id, after_state={"title": title, "file_name": file.filename})
    db.commit()
    db.refresh(document)
    return document

