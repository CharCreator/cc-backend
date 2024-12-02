import datetime
import logging
from fastapi import APIRouter, Body, Path, Response, status, FastAPI
from typing import List
from .models import ModifyCharacterRequest, GetCharacterResponse, GetAllCharactersRequest
from ...config import Config
from ...database import TransactionManager

router = APIRouter()
config = Config()
logger = logging.getLogger("cc.endpoints.characters")

fastapi_tags = ["Characters"]
app: FastAPI = None

@router.post(
    "/create",
    tags=fastapi_tags,
    name="Create Character",
    description="Create a new character for the user",
    response_model=GetCharacterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_character(
        saved_character: ModifyCharacterRequest = Body(...),
):
    """
    This endpoint allows creating a new character for the user.
    """
    async with TransactionManager() as transaction:
        character = await transaction.functions.saved_characters.create_character(
            saved_character.user_id, saved_character.name
        )

    return GetCharacterResponse(
        id=character.id,
        user_id=character.user_id,
        name=character.name,
        created_at=character.created_at
    )


@router.get(
    "/all",
    tags=fastapi_tags,
    name="List of All Characters",
    description="Retrieve a list of all characters for a user",
    response_model=List[GetCharacterResponse],
)
async def get_all_characters(
    req: GetAllCharactersRequest = Body(...),
):
    """
    Fetch all saved characters associated with the provided user ID.
    """
    async with TransactionManager() as transaction:
        characters_list = await transaction.functions.saved_characters.get_all_characters(req.user_id)
    return characters_list


@router.get(
    "/{character_id}",
    tags=fastapi_tags,
    name="Get Specific Character",
    description="Get detailed information about a character by ID",
    response_model=GetCharacterResponse,
)
async def get_character(character_id: int = Path(..., description="ID of the character to fetch")):
    """
    Retrieve information of a specific saved character by providing its ID.
    """
    async with TransactionManager() as transaction:
        character = await transaction.functions.saved_characters.get_character(character_id)
    return character


@router.put(
    "/{character_id}",
    tags=fastapi_tags,
    name="Update Existing Character",
    description="Update details of an existing character",
    response_model=GetCharacterResponse,
)
async def update_character(
        character_id: int = Path(..., description="ID of the character to update"),
        saved_character: ModifyCharacterRequest = Body(...),
):
    """
    Modify the properties of a specific character by ID.
    """
    async with TransactionManager() as transaction:
        updated_character = await transaction.functions.saved_characters.update_character(
            character_id, saved_character.name
        )
    return updated_character


@router.delete(
    "/{character_id}",
    tags=fastapi_tags,
    name="Delete Character",
    description="Delete a character permanently",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_character(character_id: int = Path(..., description="ID of the character to delete")):
    """
    Permanently remove a character from the database.
    """
    async with TransactionManager() as transaction:
        await transaction.functions.saved_characters.delete_character(character_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def init_characters_submodule(
        parent_app: FastAPI,
        submodule_path_prefix: str,
        module_name: str = __name__,
):
    """
    Initialize and include the characters router in the FastAPI app.
    """
    global app
    app = parent_app
    logger.info(f"Initializing module {module_name}")
    app.include_router(router, prefix=submodule_path_prefix)
    logger.info(f"Module {module_name} has been initialized")
