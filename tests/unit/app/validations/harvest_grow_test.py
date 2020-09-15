from app.validation.harvest_grow import validate_harvest_grow
from unittest.mock import MagicMock
import pytest

def test_harvest_grow():
    AppConfig = MagicMock()
    assert validate_harvest_grow(AppConfig, {"grow": {"grow_id": 4}}) == (True, "")

def test_harvest_grow_fail():
    AppConfig = MagicMock()
    assert validate_harvest_grow(AppConfig, {"blow": {"grow_id": 3}}) == (False, "Grow not included")
    