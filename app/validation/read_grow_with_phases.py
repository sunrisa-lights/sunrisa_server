from typing import Any, Dict, List, Tuple, Optional
from collections import Counter

from app_config import AppConfig

from app.models.grow import Grow
from app.models.grow_phase import GrowPhase
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase


def validate_read_grow_with_phases(app_config: AppConfig, message) -> Tuple[bool, str]:
    if "grow" not in message:
        return (False, "Grow not included")

    grow_json = message["grow"]
    grow_id: int = int(grow_json["grow_id"])
    grow: Optional[Grow] = app_config.db.read_grow(grow_id)
    if not grow:
        return (False, "Grow not found")

    grow_phases: List[GrowPhase] = app_config.db.read_grow_phases(grow_id)
    if not grow_phases:
        return (False, "Grow not found")

    recipe: Optional[Recipe] = app_config.db.read_recipe(grow.recipe_id)
    if not recipe:
        return (False, "Recipe not found")

    recipe_phases: List[RecipePhase] = app_config.db.read_phases_from_recipe(
        grow.recipe_id
    )
    if not recipe_phases:
        return (False, "Recipe phases not found")

    return (True, "")
