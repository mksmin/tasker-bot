import logging
from typing import Any

import uvicorn

from config import settings
from config.config import logger

if __name__ == "__main__":
    FORMAT = "[%(asctime)s]  %(levelname)s: —— %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=FORMAT,
    )

    run_args: dict[str, Any] = {
        "app": "webhook:app",
        "host": settings.run.host,
        "port": settings.run.port,
        "reload": False,
        "log_config": None,
        "workers": 1,
    }

    try:
        uvicorn.run(**run_args)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt")
