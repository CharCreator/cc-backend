from fastapi import APIRouter, Depends, HTTPException, status
from ...database import TransactionManager
from ...dependencies import must_be_logged_in
from .models import UsedAssetRequest, UsedAssetResponse
from typing import List
import logging

from fastapi import (
    FastAPI,
    APIRouter,
    Body,
    Path,
    Response,
    status,
)
router = APIRouter()
logger = logging.getLogger("cc.endpoints.used_assets")
fastapi_tags = ["UsedAssetsModule"]
@router.post(
    "/used_assets",
    tags=["Used Assets"],
    response_model=UsedAssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать использованный ассет",
    description="Добавляет запись об использованном ассете для текущего пользователя.",
)
async def create_used_asset(
    request: UsedAssetRequest,
    session_data=Depends(must_be_logged_in),
):
    """
    Эндпоинт для создания записи об использованном ассете.
    """
    async with TransactionManager() as transaction:
        try:
            used_asset = await transaction.functions.used_assets.create_used_asset(
                session_data.user.id,
                request.asset_id,
                request.properties or {}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка при создании использованного ассета: {str(e)}"
            )
        return UsedAssetResponse(
            id=used_asset.id,
            user_id=used_asset.user_id,
            asset_id=used_asset.asset_id,
            properties=used_asset.properties,
            created_at=used_asset.created_at.isoformat(),
        )

@router.get(
    "/used_assets",
    tags=["Used Assets"],
    response_model=List[UsedAssetResponse],
    summary="Получить список использованных ассетов",
    description="Возвращает все использованные ассеты текущего пользователя.",
)
async def list_used_assets(
    session_data=Depends(must_be_logged_in),
):
    """
    Эндпоинт для получения всех использованных ассетов текущего пользователя.
    """
    async with TransactionManager() as transaction:
        try:
            used_assets = await transaction.functions.used_assets.get_used_assets_by_user(
                session_data.user.id
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении списка использованных ассетов: {str(e)}"
            )
        return [
            UsedAssetResponse(
                id=asset.id,
                user_id=asset.user_id,
                asset_id=asset.asset_id,
                properties=asset.properties,
                created_at=asset.created_at.isoformat(),
            )
            for asset in used_assets
        ]

@router.delete(
    "/used_assets/{asset_id}",
    tags=["Used Assets"],
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Удалить использованный ассет",
    description="Удаляет запись об использованном ассете по его ID.",
)
async def delete_used_asset(
    asset_id: int,
    session_data=Depends(must_be_logged_in),
):
    """
    Эндпоинт для удаления записи об использованном ассете.
    """
    async with TransactionManager() as transaction:
        try:
            await transaction.functions.used_assets.delete_used_asset(asset_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ошибка при удалении использованного ассета: {str(e)}"
            )
        return {"status": "deleted"}

async def init_submodule(
        parent_app: FastAPI,
        submodule_path_prefix: str,
        module_name: str = __name__,
):
    global app
    app = parent_app
    logger.info(f"Инициализация модуля {module_name}")
    app.include_router(router, prefix=submodule_path_prefix)
    logger.info(f"Модуль {module_name} инициализирован")
