from typing import Any, Dict, List, Tuple, Optional
from collections import Counter

from app_config import AppConfig

from app.models.grow import Grow
from app.models.grow_phase import GrowPhase
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase


def validate_modify_grow(app_config: AppConfig, message) -> Tuple[bool, str]:
    if "grow_id" not in message:
        return (False, "Grow ID not included")
    elif "grow_phases" not in message:
        return (False, "Grow phases not included")
    elif "end_date" not in message:
        return (False, "End date not included")
    elif "recipe_name" not in message:
        return (False, "Recipe name not included")

    grow_id: int = message["grow_id"]
    grow: Optional[Grow] = app_config.db.read_grow(grow_id)
    if not grow:
        return (False, "Grow not found")

    old_grow_phases: List[GrowPhase] = app_config.db.read_grow_phases(grow_id)
    if not old_grow_phases:
        return (False, "Previous grow phases not found")

    recipe: Optional[Recipe] = app_config.db.read_recipe(grow.recipe_id)
    if not recipe:
        return (False, "Recipe not found")

    old_recipe_phases: List[RecipePhase] = app_config.db.read_phases_from_recipe(
        grow.recipe_id
    )
    if not old_recipe_phases:
        return (False, "Previous recipe phases not found")

    return (True, "")
