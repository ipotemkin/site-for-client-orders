"""FastAPI routes for AdminSettings CRUD."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from models.admin import AdminSettings, AdminSettingsCRUD

router = APIRouter()


@router.post(
    "/",
    response_model=AdminSettings,
    status_code=status.HTTP_201_CREATED,
)
async def create_settings(
    payload: AdminSettings,
) -> AdminSettings:
    return await AdminSettingsCRUD.create(payload)


@router.get("/", response_model=list[AdminSettings])
async def list_settings(
    limit: int = 50,
) -> list[AdminSettings]:
    return await AdminSettingsCRUD.list_all(limit=limit)


@router.get("/latest", response_model=AdminSettings)
async def get_latest_settings() -> AdminSettings:
    item = await AdminSettingsCRUD.get_latest()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin settings not found",
        )
    return item


@router.get("/{settings_id}", response_model=AdminSettings)
async def get_settings(settings_id: int) -> AdminSettings:
    item = await AdminSettingsCRUD.get_by_id(settings_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin settings not found",
        )
    return item


@router.put("/{settings_id}", response_model=AdminSettings)
async def update_settings(
    settings_id: int,
    payload: AdminSettings,
) -> AdminSettings:
    item = await AdminSettingsCRUD.update(
        settings_id,
        payload,
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin settings not found",
        )
    return item


@router.delete(
    "/{settings_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_settings(settings_id: int) -> Response:
    deleted = await AdminSettingsCRUD.delete(settings_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin settings not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
