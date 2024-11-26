import datetime
import json
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
from . import models as used_assets_models
from ...config import Config
from ...database import TransactionManager
from ...database.functions import used_assets

router = APIRouter()
config = Config()

logger = logging.getLogger("cc.endpoints.used_assets")
app: FastAPI = None

fastapi_tags = ["Used Assets"]


@router.post(
    "/used_asset",
    tags=fastapi_tags,
    name="Create Used Asset",
    description="Create a new used asset",
    response_model=used_assets_models.UsedAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_used_asset(
        request: used_assets_models.UsedAssetRequest = Body(
            ...,
            title="Request",
            description="Request body for creating or updating a used asset",
        ),
):
    """
    Create a new used asset
    """
    async with TransactionManager() as transaction:
        used_asset = await transaction.functions.used_assets.create_used_asset(
            request.user_id, request.asset_id, request.properties
        )

    return used_assets_models.UsedAssetResponse(
        id=used_asset.id,
        user_id=used_asset.user_id,
        asset_id=used_asset.asset_id,
        properties=json.loads(used_asset.properties),
        created_at=used_asset.created_at,
    )


@router.get(
    "/used_asset/{id}",
    tags=fastapi_tags,
    name="Get Used Asset by ID",
    description="Get a used asset by its ID",
    response_model=used_assets_models.UsedAssetResponse,
)
async def get_used_asset_by_id(
        id: int = Path(
            ...,
            title="ID",
            description="ID of the used asset to retrieve",
        ),
):
    """
    Retrieve a used asset by ID
    """
    async with TransactionManager() as transaction:
        used_asset = await transaction.functions.used_assets.get_by_id(id)

    return used_assets_models.UsedAssetResponse(
        id=used_asset.id,
        user_id=used_asset.user_id,
        asset_id=used_asset.asset_id,
        properties=used_asset.properties,
        created_at=used_asset.created_at,
    )


@router.put(
    "/used_asset/{id}",
    tags=fastapi_tags,
    name="Update Used Asset",
    description="Update the properties of a used asset",
    response_model=used_assets_models.UsedAssetResponse,
)
async def update_used_asset(
        id: int,
        request: used_assets_models.UsedAssetRequest = Body(...),
):
    """
    Update a used asset's properties
    """
    async with TransactionManager() as transaction:
        updated_asset = await transaction.functions.used_assets.update_properties(
            id, request.properties
        )

    return used_assets_models.UsedAssetResponse(
        id=updated_asset.id,
        user_id=updated_asset.user_id,
        asset_id=updated_asset.asset_id,
        properties=updated_asset.properties,
        created_at=updated_asset.created_at,
    )


@router.delete(
    "/used_asset/{id}",
    tags=fastapi_tags,
    name="Delete Used Asset",
    description="Delete a used asset by its ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_used_asset(
        id: int = Path(
            ...,
            title="ID",
            description="ID of the used asset to delete",
        ),
):
    """
    Delete a used asset by ID
    """
    async with TransactionManager() as transaction:
        await transaction.functions.used_assets.delete(id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def init_submodule(
        parent_app: FastAPI,
        submodule_path_prefix: str,
        module_name: str = __name__,
):
    global app
    app = parent_app
    logger.info(f"Initializing submodule {module_name}")
    app.include_router(router, prefix=submodule_path_prefix)
    logger.info(f"Submodule {module_name} initialized")
