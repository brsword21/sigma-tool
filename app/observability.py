import json
import logging
from typing import Any

logger = logging.getLogger("picky.shopping_agent")


def log_event(event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **fields}, ensure_ascii=False, default=str))
