from app.validation.read_grow_with_phases import validate_read_grow_with_phases
from unittest.mock import MagicMock, Mock
import pytest


def test_read_grow_with_phases():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_read_grow_with_phases(AppConfig, {"grow": {"grow_id": 6}}) == (
        True,
        "",
    )
    mock.validate_read_grow_with_phases(AppConfig, {"grow": {"grow_id": 6}})
    mock.validate_read_grow_with_phases.assert_called_with(
        AppConfig, {"grow": {"grow_id": 6}}
    )


def test_read_grow_with_phases_fail():
    AppConfig = MagicMock()
    mock = Mock()
    assert validate_read_grow_with_phases(AppConfig, {"blow": {"grow_id": 5}}) == (
        False,
        "Grow not included",
    )
    mock.validate_read_grow_with_phases(AppConfig, {"blow": {"grow_id": 5}})
    mock.validate_read_grow_with_phases.assert_called_with(
        AppConfig, {"blow": {"grow_id": 5}}
    )
