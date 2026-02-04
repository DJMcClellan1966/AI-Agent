from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List
import zipfile
import io

from app.db.database import get_db
from app.models.user import User
from app.models.project import Project
from app.core.security import get_current_active_user
from app.schemas.build import (
    BuildGenerateRequest,
    ProjectResponse,
    ProjectListItem,
)
from app.services.builder_service import (
    conversation_to_spec,
    spec_to_code,
    build_conversation_summary,
)

router = APIRouter()


@router.post("/generate", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def generate_project(
    body: BuildGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Generate an app from conversation history.
    Uses LLM to derive a spec and generate HTML/CSS/JS, then saves the project.
    """
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one message is required",
        )

    spec = conversation_to_spec(messages)
    if body.project_name:
        spec["name"] = body.project_name

    files = spec_to_code(spec)
    summary = build_conversation_summary(messages)

    project = Project(
        user_id=current_user.id,
        name=spec.get("name", "MyApp"),
        spec=spec,
        files=files,
        conversation_summary=summary,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=List[ProjectListItem])
def list_projects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List the current user's generated projects."""
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
  project_id: int,
  current_user: User = Depends(get_current_active_user),
  db: Session = Depends(get_db),
):
    """Get a single project by id."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("/projects/{project_id}/download")
def download_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Download project as a zip of generated files."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in (project.files or {}).items():
            zf.writestr(filename, content)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{project.name}_project.zip"',
        },
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    db.delete(project)
    db.commit()
    return None
