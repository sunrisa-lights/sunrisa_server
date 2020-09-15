from app.validation.search_recipes import validate_search_recipes
from unittest.mock import MagicMock
import pytest

def test_search_recipes():
    AppConfig = MagicMock()
    assert validate_search_recipes(AppConfig, {'search_name': 'OG'}) == (True, "")

def test_search_recipes_fail():
    AppConfig = MagicMock()
    assert validate_search_recipes(AppConfig, {'no_name': 'OG'}) == (False, "Search name not included")
