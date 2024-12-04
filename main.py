import logging
import os
import base64
import secrets
import tracemalloc

import fastapi
from fastapi import status
import fastapi.exceptions
from uuid import UUID
from enum import Enum
import fastapi.responses
from sqlalchemy.dialects.postgresql import JSONB
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware

import charcreator_backend

tracemalloc.start()

NO_COLOR_MODE = os.getenv("NO_COLOR", "").lower() in ("true", "1", "yes")
# logging level for 3rd party libraries
GLOBAL_LOGGING_LEVEL = logging.WARNING
# logging level for the bot
LOCAL_LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = "%(asctime)-15s.%(msecs)03d [%(levelname)-8s] %(name)-22s > %(filename)-18s:%(lineno)-5d - %(message)s"
LOGGING_DT_FORMAT = "%b %d %H:%M:%S"

if not NO_COLOR_MODE:
    import colorlog

    # color handler+formatter
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s" + LOGGING_FORMAT,
        datefmt=LOGGING_DT_FORMAT,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        )
    handler.setFormatter(formatter)

    # global logging
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(GLOBAL_LOGGING_LEVEL)

    logging.basicConfig(
        format=LOGGING_FORMAT,
        datefmt=LOGGING_DT_FORMAT,
        level=root_logger.level,
    )

    # local logging
    parent_logger = logging.getLogger("cc")
    parent_logger.setLevel(LOCAL_LOGGING_LEVEL)
    parent_logger.propagate = False
    parent_logger.addHandler(handler)
else:
    logging.basicConfig(
        format=LOGGING_FORMAT,
        datefmt=LOGGING_DT_FORMAT,
        level=GLOBAL_LOGGING_LEVEL,
    )
    parent_logger = logging.getLogger("cc")
    parent_logger.setLevel(LOCAL_LOGGING_LEVEL)

logger = logging.getLogger("cc").getChild("main")

app = fastapi.FastAPI(
    openapi_tags=[
        {
            "name": "Example module",
            "description": "Модуль-пример",
        },
        {
            "name": "Used Assets",
            "description": "Модуль использованных ассетов",
        },
        {
            "name": "Characters",
            "description": "Модуль сохраненные персонажей",
        },
        {
            "name": "Character Assets",
            "description": "Модуль Saved Character Assets",
        },
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


async def init_modules():
    import charcreator_backend.endpoints
    import charcreator_backend.admin_panels

    await charcreator_backend.endpoints.example.init_submodule(
        app, "/example", "example"
    )

    await charcreator_backend.admin_panels.init(app)    

    await charcreator_backend.endpoints.used_assets.asset_init_submodule(
        app, "/used_assets", "used_assets"
    )

    await charcreator_backend.endpoints.characters.init_characters_submodule(
        app, "/characters", "saved_characters"
    )

    await charcreator_backend.endpoints.charassets.charassets_init_submodule(
        app, "/charassets", "character_assets"
    )


security = HTTPBasic()


def check_auth(auth_header: str):
    prefix = "Basic "
    if not auth_header.startswith(prefix):
        return fastapi.Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
            content="Unauthorized",
        )

    auth_decoded = base64.b64decode(auth_header[len(prefix) :]).decode("utf-8")
    username, _, password = auth_decoded.partition(":")

    # этот пароль не особо важен, так что просто хранится в коде
    correct_username = secrets.compare_digest(username, "docs_read")
    correct_password = secrets.compare_digest(
        password, "H6AmdL296HeMX094J7AqRQN2OC8TBvtP"
    )

    if not (correct_username and correct_password):
        return fastapi.Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
            content="Unauthorized",
        )


@app.exception_handler(fastapi.exceptions.RequestValidationError)
async def validation_exception_handler(
        request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError
):
    error_messages = []
    for error in exc.errors():
        error_messages.append(
            {"field": error["loc"][0], "error": error["msg"], "type": error["type"]}
        )

    logger.info(
        f"Returning validation error in {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "errors": error_messages,
        },
    )
    e = charcreator_backend.shared_models.ErrorModel(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Некорректные данные в запросе",
        fields={"errors": error_messages},
    )
    return fastapi.responses.JSONResponse(content=e.model_dump(), status_code=e.code)


@app.middleware("http")
async def docs_auth_handler(request: fastapi.Request, call_next):
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        client_host = request.headers.get("X-Real-IP") or request.client[0]
        if client_host not in ["127.0.0.1", "localhost"]:
            auth = request.headers.get("Authorization")
            if not auth:
                return fastapi.Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Basic"},
                    content="Unauthorized",
                )

            try:
                check_auth(auth)
            except Exception:
                return fastapi.Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Basic"},
                    content="Unauthorized",
                )

    response = await call_next(request)
    return response


@app.middleware("http")
async def custom_exception_handler(request: fastapi.Request, call_next):
    try:
        response = await call_next(request)
        return response
    except fastapi.HTTPException as e:
        logger.info(
            f"An error was returned in {request.url.path}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": e.status_code,
                "exception": str(e),
            },
        )
        if hasattr(e, "custom_data"):
            custom_data: charcreator_backend.shared_models.ErrorModel = getattr(
                e, "custom_data"
            )
            resp = fastapi.responses.JSONResponse(
                content=custom_data.model_dump(), status_code=custom_data.code
            )
            cookies_to_remove = getattr(e, "remove_cookies", None)
            if cookies_to_remove:
                for cookie in cookies_to_remove:
                    resp.delete_cookie(cookie)
            return resp
        elif e.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            return fastapi.responses.JSONResponse(
                content=charcreator_backend.shared_models.ErrorModel(
                    code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    message="Некорректные данные в запросе",
                    fields=e.detail,
                ).model_dump(),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        else:
            return e
    except Exception as e:
        logger.error(f"An internal error occurred in {request.url.path}")
        logger.exception(e)
        custom_error = charcreator_backend.shared_models.ExceptionModel(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An internal error occurred",
            fields={
                "path": request.url.path,
                "method": request.method,
            },
            exception={
                "type": type(e).__name__,
                "message": str(e),
            },
        )
        return fastapi.responses.JSONResponse(
            content=custom_error.model_dump(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.on_event("startup")
async def startup_event():
    await init_modules()
    logger.info("Modules initialized")
    from charcreator_backend.database import TransactionManager

    async with TransactionManager() as conn:
        pass
    logger.info("Database connection established")


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2612)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)