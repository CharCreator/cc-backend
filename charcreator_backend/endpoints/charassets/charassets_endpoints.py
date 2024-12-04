import logging
from fastapi import (
    FastAPI,
    APIRouter,
    Body,
    Path,
    Response,
    status,
)
import typing
from .models import GetCharAssetResponse, ModifyCharAssetRequest, GetAllAssetsRequest
from ...config import Config
from ...database import TransactionManager

router = APIRouter()
config = Config()

logger = logging.getLogger("cc.endpoints.character_assets")
app: FastAPI = None

fastapi_tags = ["Character Assets"]

@router.post(
    "/create",
    tags=fastapi_tags,
    name="Create Character Asset",
    description="Create a new link for a character asset",
    response_model=GetCharAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_charasset(
        request: ModifyCharAssetRequest = Body(
            ...,
            title="Request",
            description="Request body for creating a new character asset link",
        ),
):
    """
    Creates a new link for a character asset
    """
    async with TransactionManager() as transaction:
        character_asset = await transaction.functions.saved_character_assets.create_charasset(
            request.saved_character_id,
            request.used_asset_id
        )

    return GetCharAssetResponse(
        id=character_asset.id,
        saved_character_id=character_asset.saved_character_id,
        used_asset_id=character_asset.used_asset_id,
        created_at=character_asset.created_at,
    )


@router.get(
    "/{charasset_id}",
    tags=fastapi_tags,
    name="Get Character Asset",
    description="Retrieve a asset using its ID",
    response_model=GetCharAssetResponse,
)
async def get_charasset(
        charasset_id: int = Path(
            ...,
            title="Character Asset ID",
            description="The ID of the character asset to retrieve",
        ),
):
    """
    Get details of a character asset by its ID
    """
    async with TransactionManager() as transaction:
        character_asset = await transaction.functions.saved_character_assets.get_charasset(charasset_id)

    return GetCharAssetResponse(
        id=character_asset.id,
        saved_character_id=character_asset.saved_character_id,
        used_asset_id=character_asset.used_asset_id,
        created_at=character_asset.created_at.isoformat(),  # Convert to ISO 8601 format
    )


@router.get(
    "/all",
    tags=fastapi_tags,
    name="Get All Character Assets",
    description="Retrieve all character assets by the character's ID",
    response_model=typing.List[GetCharAssetResponse],
)
async def get_all_charassets(
         req: GetAllAssetsRequest = Body(...),
):
    """
    Get all character assets for a specific character ID
    """
    async with TransactionManager() as transaction:
        character_assets = await transaction.functions.saved_character_assets.get_all_charassets(req.character_id)

    return [
        GetCharAssetResponse(
            id=asset.id,
            saved_character_id=asset.saved_character_id,
            used_asset_id=asset.used_asset_id,
            created_at=asset.created_at,
        )
        for asset in character_assets
    ]

@router.put(
    "/{id}",
    tags=fastapi_tags,
    name="Update  Charsset",
    description="Update the properties of a char asset",
    response_model=GetCharAssetResponse,
)
async def update_charasset(
        id: int,
        request: ModifyCharAssetRequest = Body(...),
):
    """
    Update a used asset's properties
    """
    async with TransactionManager() as transaction:
        updated_asset = await transaction.functions.saved_character_assets.update(
            id, request.used_asset_id
        )

    return GetCharAssetResponse(
            id=updated_asset.id,
            saved_character_id=updated_asset.saved_character_id,
            used_asset_id=updated_asset.used_asset_id,
            created_at=updated_asset.created_at,
        )

@router.delete(
    "/{charasset_id}",
    tags=fastapi_tags,
    name="Delete Character Asset",
    description="Remove a сharacter asset using its ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_charasset(
        charasset_id: int = Path(
            ...,
            title="Character Asset ID",
            description="The ID of the character asset to delete",
        ),
):
    """
    Delete a character asset by its ID
    """
    async with TransactionManager() as transaction:
        await transaction.functions.saved_character_assets.delete(charasset_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def init_submodule(
        parent_app: FastAPI,
        submodule_path_prefix: str,
        module_name: str = __name__,
):
    global app
    app = parent_app
    logger.info(f"Initializing module {module_name}")
    app.include_router(router, prefix=submodule_path_prefix)
    logger.info(f"Module {module_name} has been initialized")
