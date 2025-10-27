from typing import Annotated

import typer

from commands.coro import coro
from crud.crud_service import get_crud_service_with_session

app = typer.Typer(
    name="crud",
    help="CRUD operations for the database",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.command(
    help="Create a new user",
)
@coro
async def create_user(
    user_tg: Annotated[
        int,
        typer.Argument(
            help="User telegram id",
        ),
    ],
    username: Annotated[
        str,
        typer.Argument(
            help="Username in telegram",
        ),
    ],
) -> None:
    async with get_crud_service_with_session() as crud_service:
        user = await crud_service.user.create_user(
            {
                "user_tg": user_tg,
                "username": username,
            },
        )
        print(f"created user: {user}")


@app.command(
    help="Get a user by id",
)
@coro
async def get_by_id(
    user_id: Annotated[
        int,
        typer.Argument(
            help="User id in database",
        ),
    ],
) -> None:
    async with get_crud_service_with_session() as crud_service:
        user = await crud_service.user.get_by_id(
            user_id=user_id,
        )
        print(f"Getted user: {user}")


@app.command(
    help="Get a user by user telegram id",
)
@coro
async def get_by_tg_id(
    user_tg: Annotated[
        int,
        typer.Argument(
            help="User telegram id",
        ),
    ],
) -> None:
    async with get_crud_service_with_session() as crud_service:
        user = await crud_service.user.get_by_tg_id(
            user_tg=user_tg,
        )
        print(f"Getted user: {user}")
