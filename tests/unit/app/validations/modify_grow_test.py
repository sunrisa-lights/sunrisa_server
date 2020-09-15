from app.validation.modify_grow import validate_modify_grow
from unittest.mock import MagicMock
import pytest

def test_modify_grow():
    AppConfig = MagicMock()
    assert validate_modify_grow(AppConfig, {"grow_phases": 1, "grow_id": 5, "end_date": 3, "recipe_name": "OGK"}) == (True, "")
def test_modify_grow_fail():
    AppConfig = MagicMock()
    assert validate_modify_grow(AppConfig, {"grow_id": 5, "end_date": 3, "recipe_name": "OGK"}) == (False, "Grow phases not included")