import asyncio
import logging

from config.config import logger
from run_config import start_app

if __name__ == "__main__":
    FORMAT = "[%(asctime)s]  %(levelname)s: —— %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=FORMAT,
    )

    try:
        asyncio.run(
            start_app(),
        )
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt")
