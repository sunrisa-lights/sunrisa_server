from app.validation.search_recipes import validate_search_recipes
from unittest.mock import MagicMock, Mock
import pytest


def test_search_recipes():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_search_recipes(AppConfig, {"search_name": "OG"}) == (True, "")
    mock.validate_search_recipes(AppConfig, {"search_name": "OG"})
    mock.validate_search_recipes.assert_called_with(AppConfig, {"search_name": "OG"})


def test_search_recipes_fail():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_search_recipes(AppConfig, {"no_name": "OG"}) == (
        False,
        "Search name not included",
    )
    mock.validate_search_recipes(AppConfig, {"no_name": "OG"})
    mock.validate_search_recipes.assert_called_with(AppConfig, {"no_name": "OG"})
