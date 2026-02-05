"""
Workspace API for the IDE: list directory and read file.
Uses the same path rules as the agent (workspace_root, allowlist).
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User
from app.core.security import get_current_active_user
from app.core.config import settings

router = APIRouter()


def _safe_path(root: str, path: str) -> Optional[str]:
    """Resolve path under workspace_root; return None if outside."""
    if not root or not os.path.isabs(root):
        return None
    full = os.path.normpath(os.path.join(root, path.lstrip("/").replace("\\", "/")))
    root_abs = os.path.abspath(root)
    if not full.startswith(root_abs):
        return None
    return full


def _validate_workspace_allowed(workspace_root: str) -> bool:
    allowed = getattr(settings, "WORKSPACE_ALLOWED_ROOTS", None) or []
    if not allowed:
        return True
    root_abs = os.path.abspath(workspace_root)
    for allowed_dir in allowed:
        if not allowed_dir:
            continue
        if root_abs.startswith(os.path.abspath(allowed_dir)):
            return True
    return False


@router.get("/list")
def workspace_list(
    root: str,
    path: str = ".",
    current_user: User = Depends(get_current_active_user),
):
    """List directory entries. root = workspace_root (absolute path), path = relative path."""
    if not _validate_workspace_allowed(root):
        raise HTTPException(status_code=400, detail="Workspace not allowed")
    full = _safe_path(root, path)
    if not full:
        raise HTTPException(status_code=400, detail="Path outside workspace")
    if not os.path.isdir(full):
        raise HTTPException(status_code=400, detail="Not a directory")
    try:
        entries = os.listdir(full)
        return {"path": path, "entries": entries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/read")
def workspace_read(
    root: str,
    path: str,
    current_user: User = Depends(get_current_active_user),
):
    """Read file content. root = workspace_root, path = relative path to file."""
    if not _validate_workspace_allowed(root):
        raise HTTPException(status_code=400, detail="Workspace not allowed")
    full = _safe_path(root, path)
    if not full:
        raise HTTPException(status_code=400, detail="Path outside workspace")
    if not os.path.isfile(full):
        raise HTTPException(status_code=400, detail="Not a file")
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            return {"path": path, "content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
