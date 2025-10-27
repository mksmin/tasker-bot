import typer

from commands.crud import app as crud_service_app

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.callback()
def callback() -> None:
    """ """


app.add_typer(crud_service_app)
