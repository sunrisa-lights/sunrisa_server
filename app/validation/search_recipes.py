from typing import Any, Dict, List, Tuple, Optional
from app_config import AppConfig


def validate_search_recipes(app_config: AppConfig, message) -> Tuple[bool, str]:
    if "search_name" not in message:
        return (False, "Search name not included")
    return (True, "")
