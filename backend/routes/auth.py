"""Auth routes: bootstrap register, login, me."""

from __future__ import annotations

from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status

from core.deps import get_current_admin
from core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from models.admin_user import (
    AdminUser,
    AdminUserCreate,
    AdminUserCRUD,
)

router = APIRouter()


class BootstrapStatus(BaseModel):
    registration_open: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.get(
    "/bootstrap-status",
    response_model=BootstrapStatus,
)
async def bootstrap_status() -> BootstrapStatus:
    count = await AdminUserCRUD.count()
    return BootstrapStatus(registration_open=count == 0)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: AdminUserCreate) -> TokenResponse:
    if await AdminUserCRUD.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Регистрация закрыта",
        )
    login = payload.login.strip()
    if not login:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Укажите логин",
        )
    existing = await AdminUserCRUD.get_by_login(login)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такой логин уже занят",
        )
    admin = await AdminUserCRUD.create(
        login,
        hash_password(payload.password),
    )
    assert admin.id is not None
    token = create_access_token(
        subject=admin.login,
        admin_id=admin.id,
    )
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: AdminUserCreate) -> TokenResponse:
    login_value = payload.login.strip()
    found = await AdminUserCRUD.get_by_login(login_value)
    if found is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    admin, password_hash = found
    if not verify_password(payload.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    assert admin.id is not None
    token = create_access_token(
        subject=admin.login,
        admin_id=admin.id,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminUser)
async def me(
    admin: AdminUser = Depends(get_current_admin),
) -> AdminUser:
    return admin
