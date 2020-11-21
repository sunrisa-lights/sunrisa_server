from app.validation.modify_grow import validate_modify_grow
from unittest.mock import MagicMock, Mock
import pytest


def test_modify_grow():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_modify_grow(
        AppConfig, {"grow_phases": 1, "grow_id": 5, "end_date": 3, "recipe_name": "OGK"}
    ) == (True, "")
    mock.validate_modify_grow(
        AppConfig, {"grow_phases": 1, "grow_id": 5, "end_date": 3, "recipe_name": "OGK"}
    )
    mock.validate_modify_grow.assert_called_with(
        AppConfig, {"grow_phases": 1, "grow_id": 5, "end_date": 3, "recipe_name": "OGK"}
    )


def test_modify_grow_fail():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_modify_grow(
        AppConfig, {"grow_id": 5, "end_date": 3, "recipe_name": "OGK"}
    ) == (False, "Grow phases not included")
    mock.validate_modify_grow(
        AppConfig, {"grow_id": 5, "end_date": 3, "recipe_name": "OGK"}
    )
    mock.validate_modify_grow.assert_called_with(
        AppConfig, {"grow_id": 5, "end_date": 3, "recipe_name": "OGK"}
    )
