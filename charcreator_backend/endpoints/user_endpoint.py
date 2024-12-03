import logging
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Path,
    Body,
    status,
    Depends,
)
from typing import List
from ..database import TransactionManager
from ..users import UserFunctions, User, EmailTaken, UserNotFound
from ...shared_models import UserModel

router = APIRouter()
logger = logging.getLogger("cc.endpoints.user")
fastapi_tags = ["User Management"]


@router.get(
    "/users",
    tags=fastapi_tags,
    name="Get Users",
    response_model=List[UserModel],
    description="Получение списка пользователей",
)
async def get_users(
    limit: int = Query(10, description="Количество пользователей для выборки"),
    offset: int = Query(0, description="Смещение выборки"),
):
    async with TransactionManager() as transaction:
        user_funcs = UserFunctions(transaction.conn)
        rows = await transaction.conn.fetch(
            "SELECT * FROM users ORDER BY id LIMIT $1 OFFSET $2", limit, offset
        )
        users = [User.from_row(row).to_model() for row in rows]
        return users


@router.post(
    "/users/{user_id}/reset_password",
    tags=fastapi_tags,
    name="Reset Password",
    description="Сброс пароля пользователя",
)
async def reset_password(
    user_id: int = Path(..., description="ID пользователя"),
    new_password: str = Body(..., description="Новый пароль"),
):
    hashed_password = secrets.token_urlsafe(16)  # Генерация хэша пароля (замените bcrypt)
    async with TransactionManager() as transaction:
        user_funcs = UserFunctions(transaction.conn)
        try:
            updated_user = await user_funcs.set_password(user_id, hashed_password)
            logger.info(f"Password reset for user {user_id}")
            return {"status": "success", "message": "Password reset successfully"}
        except UserNotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post(
    "/users/{user_id}/block",
    tags=fastapi_tags,
    name="Block User",
    description="Блокировка пользователя",
)
async def block_user(user_id: int = Path(..., description="ID пользователя")):
    async with TransactionManager() as transaction:
        user_funcs = UserFunctions(transaction.conn)
        user = await user_funcs.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await transaction.conn.execute(
            "UPDATE users SET blocked = TRUE WHERE id = $1", user_id
        )
        return {"status": "success", "message": "User blocked successfully"}


@router.post(
    "/users/{user_id}/unblock",
    tags=fastapi_tags,
    name="Unblock User",
    description="Разблокировка пользователя",
)
async def unblock_user(user_id: int = Path(..., description="ID пользователя")):
    async with TransactionManager() as transaction:
        user_funcs = UserFunctions(transaction.conn)
        user = await user_funcs.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await transaction.conn.execute(
            "UPDATE users SET blocked = FALSE WHERE id = $1", user_id
        )
        return {"status": "success", "message": "User unblocked successfully"}


async def init_submodule(
    parent_app, submodule_path_prefix: str, module_name: str = __name__
):
    logger.info(f"Инициализация модуля {module_name}")
    parent_app.include_router(router, prefix=submodule_path_prefix)
    logger.info(f"Модуль {module_name} инициализирован")


@router.post("/block/{user_id}", response_model=UserModel)
async def block_user(user_id: int, db: Depends(get_db)):
    """
    Block a user
    """
    user_functions = UserFunctions(db)
    return await user_functions.block_user(user_id)


@router.post("/unblock/{user_id}", response_model=UserModel)
async def unblock_user(user_id: int, db: Depends(get_db)):
    """
    Unblock a user
    """
    user_functions = UserFunctions(db)
    return await user_functions.unblock_user(user_id)


@router.get("/is_blocked/{user_id}", response_model=bool)
async def is_blocked(user_id: int, db: Depends(get_db)):
    """
    Check if a user is blocked
    """
    user_functions = UserFunctions(db)
    return await user_functions.is_user_blocked(user_id)
