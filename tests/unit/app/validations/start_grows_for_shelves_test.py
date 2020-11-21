from app.validation.start_grows_for_shelves import validate_grow_id
from unittest.mock import MagicMock, Mock
import pytest


def test_validate_grow_id_fail():
    AppConfig = MagicMock()
    mock = Mock()
    grow_id = 4
    assert validate_grow_id(AppConfig, {"grow": {"blow": grow_id}}) == (
        False,
        "Grow ID not included",
    )
    mock.validate_grow_id(AppConfig, {"grow": {"blow": grow_id}})
    mock.validate_grow_id(AppConfig, {"grow": {"blow": grow_id}})


def test_validate_grow_id_pass():
    AppConfig = MagicMock()
    mock = Mock()
    grow_id = 4
    assert validate_grow_id(AppConfig, {"grow": {"grow_id": grow_id}}) == (True, "")
    mock.validate_grow_id(AppConfig, {"grow": {"grow_id": grow_id}})
    mock.validate_grow_id.assert_called_with(AppConfig, {"grow": {"grow_id": grow_id}})
