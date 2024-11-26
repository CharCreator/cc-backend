import datetime
import logging
import random
from fastapi import (
    FastAPI,
    APIRouter,
    Body,
    Path,
    Response,
    status,
)
import typing
from . import models as saved_character_assets_models
from ...config import Config
from ...database import TransactionManager
from ...database.functions import  saved_character_assets as saved_character_assets_functions

router = APIRouter()
config = Config()

logger = logging.getLogger("cc.endpoints.saved_character_assets")
app: FastAPI = None

fastapi_tags = ["Saved Character Assets"]


@router.post(
    "/create",
    tags=fastapi_tags,
    name="Create Saved Character Asset",
    description="Create a new saved character asset link",
    response_model=saved_character_assets_models.SavedCharacterAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_saved_character_asset(
        request: saved_character_assets_models.SavedCharacterAssetRequest = Body(
            ...,
            title="Request",
            description="Request body for creating a saved character asset link",
        ),
):
    """
    Create a new saved character asset link
    """
    async with TransactionManager() as transaction:
        saved_character_asset = await transaction.functions.saved_character_assets.create_saved_character_asset(
            request.saved_character_id,
            request.used_asset_id
        )

    return saved_character_assets_models.SavedCharacterAssetResponse(
        id=saved_character_asset.id,
        saved_character_id=saved_character_asset.saved_character_id,
        used_asset_id=saved_character_asset.used_asset_id,
        created_at=saved_character_asset.created_at,
    )


@router.get(
    "/{saved_character_asset_id}",
    tags=fastapi_tags,
    name="Get Saved Character Asset",
    description="Get a saved character asset by ID",
    response_model=saved_character_assets_models.SavedCharacterAssetResponse,
)
async def get_saved_character_asset(
        saved_character_asset_id: int = Path(
            ...,
            title="Saved Character Asset ID",
            description="ID of the saved character asset",
        ),
):
    """
    Retrieve a saved character asset by ID
    """
    async with TransactionManager() as transaction:
        saved_character_asset = await transaction.functions.saved_character_assets.get_by_id(saved_character_asset_id)

    return saved_character_assets_models.SavedCharacterAssetResponse(
        id=saved_character_asset.id,
        saved_character_id=saved_character_asset.saved_character_id,
        used_asset_id=saved_character_asset.used_asset_id,
        created_at=saved_character_asset.created_at.isoformat(),  # Преобразуем в ISO 8601
    )


@router.get(
    "/all/{saved_character_id}",
    tags=fastapi_tags,
    name="Get All Saved Character Assets",
    description="Get all saved character assets by saved character ID",
    response_model=typing.List[saved_character_assets_models.SavedCharacterAssetResponse],
)
async def get_all_saved_character_assets(
        saved_character_id: int = Path(
            ...,
            title="Saved Character ID",
            description="ID of the saved character",
        ),
):
    """
    Retrieve all saved character assets by saved character ID
    """
    async with TransactionManager() as transaction:
        saved_character_assets = await transaction.functions.saved_character_assets.get_all_by_saved_character(saved_character_id)

    return [
        saved_character_assets_models.SavedCharacterAssetResponse(
            id=asset.id,
            saved_character_id=asset.saved_character_id,
            used_asset_id=asset.used_asset_id,
            created_at=asset.created_at,
        )
        for asset in saved_character_assets
    ]


@router.delete(
    "/delete/{saved_character_asset_id}",
    tags=fastapi_tags,
    name="Delete Saved Character Asset",
    description="Delete a saved character asset by ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_saved_character_asset(
        saved_character_asset_id: int = Path(
            ...,
            title="Saved Character Asset ID",
            description="ID of the saved character asset to delete",
        ),
):
    """
    Delete a saved character asset by ID
    """
    async with TransactionManager() as transaction:
        await transaction.functions.saved_character_assets.delete(saved_character_asset_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
