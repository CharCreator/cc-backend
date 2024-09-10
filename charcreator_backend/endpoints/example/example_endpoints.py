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

from . import models as example_module_models
from ...config import Config
from ...database import TransactionManager

router = APIRouter()
config = Config()

logger = logging.getLogger("cc.endpoints.example")
app: FastAPI = None

fastapi_tags = ["Example module"]


@router.post(
    "/submit",
    tags=fastapi_tags,
    name="Example submit",
    description="An example of a POST request",
    response_model=example_module_models.ExampleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_example(
        request: example_module_models.ExampleRequest = Body(
            ...,
            title="Request",
            description="Request body",
        ),
):
    """
    An example of a POST request
    """
    async with TransactionManager() as transaction:
        # you'd put database calls here
        ...

    return example_module_models.ExampleResponse(
        **request.model_dump(),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )


@router.delete(
    "/delete/{id}",
    tags=fastapi_tags,
    name="Example delete",
    description="An example of a DELETE request",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_example(
        id: int = Path(
            ...,
            title="ID",
            description="ID of the object to delete",
        ),
):
    """
    An example of a DELETE request
    """
    async with TransactionManager() as transaction:
        # you'd put database calls here
        ...

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/random_number",
    tags=fastapi_tags,
    name="Random number",
    description="Get a random number",
    response_model=int,
)
async def random_number():
    """
    Get a random number
    """
    return random.randint(0, 100)


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
