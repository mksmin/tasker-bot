import logging
from typing import Any, cast

from faststream.rabbit import RabbitMessage, RabbitRouter
from pydantic import BaseModel

from rabbit_service.dispatcher import dp

log = logging.getLogger(__name__)

router = RabbitRouter()


@router.subscriber("cmd.affirmations")
async def handle_commands(
    msg: dict[str, Any],
    message: RabbitMessage,
) -> None:
    try:
        command_type = cast(str, msg.get("type"))
        payload = msg.get("payload", {})

        log.info(
            "Processing command %s from %s",
            command_type,
            message.message_id[:10] if message.message_id else "unknown",
        )

        await dp.dispatch(
            command_type,
            payload,
        )

        log.info(
            "Command %s processed successfully",
            command_type,
        )
    except Exception:
        log.exception("Error processing command")
        raise


class IncomingMessage(BaseModel):
    type: str
    payload: dict[str, Any]


@router.subscriber("qry.affirmations")
async def handle_queries(
    msg: IncomingMessage,
    message: RabbitMessage,
) -> Any:
    try:
        log.info(
            "Processing query %s from %s",
            msg.type,
            message.message_id[:10] if message.message_id else "unknown",
        )

        result = await dp.dispatch(
            msg.type,
            msg.payload,
        )
        log.info("Query processed successfully")

    except Exception as e:
        log.exception("Error processing query")
        return {
            "status": "error",
            "message": str(e),
        }
    else:
        return result
