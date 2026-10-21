"""FastAPI routes for Service CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.deps import get_current_admin
from models.admin_user import AdminUser
from models.service import Service, ServiceCRUD

router = APIRouter()
_bearer = HTTPBearer(auto_error=False)


@router.post(
    "/",
    response_model=Service,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    payload: Service,
    _: AdminUser = Depends(get_current_admin),
) -> Service:
    return await ServiceCRUD.create(payload)


@router.get("/", response_model=list[Service])
async def list_services(
    active_only: bool = False,
    limit: int = 200,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        _bearer,
    ),
) -> list[Service]:
    if not active_only:
        await get_current_admin(credentials)
    return await ServiceCRUD.list_all(
        active_only=active_only,
        limit=limit,
    )


@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: int,
    _: AdminUser = Depends(get_current_admin),
) -> Service:
    item = await ServiceCRUD.get_by_id(service_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена",
        )
    return item


@router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: int,
    payload: Service,
    _: AdminUser = Depends(get_current_admin),
) -> Service:
    item = await ServiceCRUD.update(service_id, payload)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена",
        )
    return item


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(
    service_id: int,
    _: AdminUser = Depends(get_current_admin),
) -> Response:
    deleted = await ServiceCRUD.delete(service_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
