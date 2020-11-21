from app.validation.harvest_grow import validate_harvest_grow
from unittest.mock import MagicMock, Mock
import pytest


def test_harvest_grow():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_harvest_grow(AppConfig, {"grow": {"grow_id": 4}}) == (True, "")
    mock.validate_harvest_grow(AppConfig, {"grow": {"grow_id": 4}})
    mock.validate_harvest_grow.assert_called_with(AppConfig, {"grow": {"grow_id": 4}})


def test_harvest_grow_fail():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_harvest_grow(AppConfig, {"blow": {"grow_id": 3}}) == (
        False,
        "Grow not included",
    )
    mock.validate_harvest_grow(AppConfig, {"blow": {"grow_id": 3}})
    mock.validate_harvest_grow.assert_called_with(AppConfig, {"blow": {"grow_id": 3}})
