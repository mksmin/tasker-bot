from typing import TYPE_CHECKING, Annotated

import typer

from app_exceptions.exceptions import TaskNotFoundError
from commands.coro import coro
from crud.crud_service import get_crud_service_with_session

if TYPE_CHECKING:
    from crud.crud_service import CRUDService  # noqa: F401

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
    async with get_crud_service_with_session() as crud_service:  # type: CRUDService
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
    async with get_crud_service_with_session() as crud_service:  # type: CRUDService
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
    async with get_crud_service_with_session() as crud_service:  # type: CRUDService
        user = await crud_service.user.get_by_tg_id(
            user_tg=user_tg,
        )
        print(f"Getted user: {user}")


@app.command(
    help="get random user affirmations",
)
@coro
async def get_random_affirmations(
    user_tg: Annotated[
        int,
        typer.Argument(
            help="User telegram id",
        ),
    ],
    count: Annotated[
        int | None,
        typer.Argument(
            help="Count of affirmations to get",
        ),
    ] = None,
) -> None:
    async with get_crud_service_with_session() as crud_service:  # type: CRUDService
        try:
            affirmations = await crud_service.affirm.get_random_affirmations(
                user_tg=user_tg,
                count=count,
            )
        except TaskNotFoundError:
            print("Tasks not found")
        else:
            for i, affirmation in enumerate(affirmations, 1):
                print(f"{i}. {affirmation}")


@app.command(
    help="get random user affirmations",
)
@coro
async def get_paginated_affirmations(
    user_tg: Annotated[
        int,
        typer.Argument(
            help="User telegram id",
        ),
    ],
    limit: Annotated[
        int | None,
        typer.Argument(
            help="Count of affirmations to get",
        ),
    ] = 10,
    offset: Annotated[
        int | None,
        typer.Argument(
            help="Count of affirmations to get",
        ),
    ] = 0,
) -> None:
    async with get_crud_service_with_session() as crud_service:  # type: CRUDService
        try:
            affirmations = await crud_service.affirm.get_paginated_affirmations(
                user_tg=user_tg,
                limit=limit,
                offset=offset,
            )
        except TaskNotFoundError:
            print("Tasks not found")
        else:
            for i, affirmation in enumerate(affirmations, 1):
                print(f"{i}. {affirmation}")


@app.command(
    help="Remove a user affirmation",
)
@coro
async def remove_affirmation(
    user_tg: Annotated[
        int,
        typer.Argument(
            help="User telegram id",
        ),
    ],
    affirm_id: Annotated[
        int,
        typer.Argument(
            help="Affirmation id",
        ),
    ],
) -> None:
    async with get_crud_service_with_session() as crud_service:  # type: CRUDService
        try:
            await crud_service.affirm.remove_affirmation(
                user_tg=user_tg,
                affirm_id=affirm_id,
            )
        except TaskNotFoundError:
            print("Task not found or already removed")
        else:
            print("Successfully removed affirmation")
