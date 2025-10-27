import typer

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.callback()
def callback() -> None:
    """ """
