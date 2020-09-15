from app.validation.read_grow_with_phases import validate_read_grow_with_phases
from unittest.mock import MagicMock
import pytest

def test_read_grow_with_phases():
    AppConfig = MagicMock()
    assert validate_read_grow_with_phases(AppConfig, {"grow": {"grow_id": 6}}) == (True, "")

def test_read_grow_with_phases_fail():
    AppConfig = MagicMock()
    assert validate_read_grow_with_phases(AppConfig, {"blow": {"grow_id": 5}}) == (False, "Grow not included")