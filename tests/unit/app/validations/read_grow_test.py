from app.validation.read_grow import validate_read_grow
from unittest.mock import MagicMock
import pytest

def test_read_grow_fail():
    AppConfig = MagicMock()
    assert validate_read_grow(AppConfig, {"blow": {"glow": 3}}) == (False, "Grow not included")

def test_read_grow():
    AppConfig = MagicMock()
    assert validate_read_grow(AppConfig, {"grow": {"grow_id": 6}}) == (True, "")