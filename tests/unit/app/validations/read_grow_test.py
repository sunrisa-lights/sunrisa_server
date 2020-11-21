from app.validation.read_grow import validate_read_grow
from unittest.mock import MagicMock, Mock
import pytest


def test_read_grow_fail():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_read_grow(AppConfig, {"blow": {"glow": 3}}) == (
        False,
        "Grow not included",
    )
    mock.validate_read_grow(AppConfig, {"blow": {"glow": 3}})
    mock.validate_read_grow.assert_called_with(AppConfig, {"blow": {"glow": 3}})


def test_read_grow():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_read_grow(AppConfig, {"grow": {"grow_id": 6}}) == (True, "")
    mock.validate_read_grow(AppConfig, {"grow": {"grow_id": 6}})
    mock.validate_read_grow.assert_called_with(AppConfig, {"grow": {"grow_id": 6}})
