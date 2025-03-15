# import lib
import logging
import os

from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)


def get_token(name_of_token: str) -> str | None:

    path_env = Path(__file__).parent.absolute() / '.env'

    if path_env.exists():

        load_dotenv(path_env)
        return os.getenv(name_of_token)

    return None
