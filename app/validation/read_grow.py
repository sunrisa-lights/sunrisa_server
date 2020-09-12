from typing import Any, Dict, List, Tuple, Optional
from collections import Counter

from app_config import AppConfig

from app.models.grow import Grow


def validate_read_grow(app_config: AppConfig, message) -> Tuple[bool, str]:
    if "grow" not in message:
        return (False, "Grow not included")

    grow_json = message["grow"]
    grow_id: int = int(grow_json["grow_id"])
    grow: Optional[Grow] = app_config.db.read_grow(grow_id)
    if not grow:
        return (False, "Grow not found")

    return (True, "")
