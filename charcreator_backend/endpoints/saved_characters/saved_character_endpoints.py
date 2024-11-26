import datetime
import logging
import random
from fastapi import APIRouter, Body, Path, Response, status, FastAPI
from typing import List
from .models import SavedCharacterRequest, SavedCharacterResponse
from ...config import Config
from ...database import TransactionManager
from ...database.functions import saved_characters

router = APIRouter()
config = Config()
logger = logging.getLogger("cc.endpoints.saved_characters")

fastapi_tags = ["Saved Characters"]
app: FastAPI = None

@router.post(
    "/saved_characters",
    tags=fastapi_tags,
    name="Create saved character",
    description="Create a new saved character for the user",
    response_model=SavedCharacterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_saved_character(
        saved_character: SavedCharacterRequest = Body(...),
):
    """
    Create a new saved character.
    """
    async with TransactionManager() as transaction:
        new_character = await transaction.functions.saved_characters.create_saved_character(
            saved_character.user_id, saved_character.name
        )

    return SavedCharacterResponse(
        id=new_character.id,
        user_id=new_character.user_id,
        name=new_character.name,
        created_at=new_character.created_at
    )


@router.get(
    "/saved_characters",
    tags=fastapi_tags,
    name="List saved characters",
    description="Get a list of saved characters",
    response_model=List[SavedCharacterResponse],
)
async def list_saved_characters():
    """
    Retrieve a list of saved characters.
    """
    async with TransactionManager() as transaction:
        characters = await transaction.functions.saved_characters.get_all_by_user(
            1)  # Replace with actual user_id logic
    return characters


@router.get(
    "/saved_characters/{character_id}",
    tags=fastapi_tags,
    name="Get saved character",
    description="Get details of a saved character",
    response_model=SavedCharacterResponse,
)
async def get_saved_character(character_id: int = Path(..., description="ID of the saved character")):
    """
    Retrieve a specific saved character by ID.
    """
    async with TransactionManager() as transaction:
        character = await transaction.functions.saved_characters.get_by_id(character_id)
    return character


@router.put(
    "/saved_characters/{character_id}",
    tags=fastapi_tags,
    name="Update saved character",
    description="Update an existing saved character",
    response_model=SavedCharacterResponse,
)
async def update_saved_character(
        character_id: int = Path(..., description="ID of the saved character"),
        saved_character: SavedCharacterRequest = Body(...),
):
    """
    Update details of a specific saved character.
    """
    async with TransactionManager() as transaction:
        updated_character = await transaction.functions.saved_characters.update_name(
            character_id, saved_character.name
        )
    return updated_character


@router.delete(
    "/saved_characters/{character_id}",
    tags=fastapi_tags,
    name="Delete saved character",
    description="Delete a saved character",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_saved_character(character_id: int = Path(..., description="ID of the saved character")):
    """
    Delete a specific saved character.
    """
    async with TransactionManager() as transaction:
        await transaction.functions.saved_characters.delete(character_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def init_saved_characters_module(
        parent_app: FastAPI,
        submodule_path_prefix: str,
        module_name: str = __name__,
):
    global app
    app = parent_app
    logger.info(f"Инициализация модуля {module_name}")
    app.include_router(router, prefix=submodule_path_prefix)
    logger.info(f"Модуль {module_name} инициализирован")
