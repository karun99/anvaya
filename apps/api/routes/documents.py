from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from apps.api.database import get_db
from apps.api.models import Document, DocumentChunk, Source, User
from apps.api.routes.auth import get_current_user

router = APIRouter()


class DocumentResponse(BaseModel):
    id: str
    source_id: str
    content: Optional[str]
    metadata_: dict
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document_id: str
    source_id: str
    chunks_count: int
    status: str


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    source_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Document)
        .join(Source, Document.source_id == Source.id)
        .where(Source.user_id == current_user.id)
    )
    if source_id:
        query = query.where(Document.source_id == source_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    source_type: str = "document",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()

    source = Source(
        user_id=current_user.id,
        title=file.filename,
        source_type=source_type,
    )
    db.add(source)
    await db.flush()

    document = Document(
        source_id=source.id,
        content=content.decode("utf-8", errors="ignore"),
    )
    db.add(document)
    await db.flush()

    chunk_size = 1000
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunk_content = content[i : i + chunk_size].decode("utf-8", errors="ignore")
        chunk = DocumentChunk(
            document_id=document.id,
            content=chunk_content,
            metadata_={"position": i},
        )
        chunks.append(chunk)
    db.add_all(chunks)

    await db.commit()
    await db.refresh(document)

    return DocumentUploadResponse(
        document_id=str(document.id),
        source_id=str(source.id),
        chunks_count=len(chunks),
        status="uploaded",
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .join(Source, Document.source_id == Source.id)
        .where(
            Document.id == document_id,
            Source.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .join(Source, Document.source_id == Source.id)
        .where(
            Document.id == document_id,
            Source.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks_result = await db.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    )
    chunks = chunks_result.scalars().all()
    return {"chunks": chunks, "count": len(chunks)}


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .join(Source, Document.source_id == Source.id)
        .where(
            Document.id == document_id,
            Source.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(document)
    await db.commit()
    return {"status": "deleted"}
