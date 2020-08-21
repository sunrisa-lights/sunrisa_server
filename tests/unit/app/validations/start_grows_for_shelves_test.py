from app.validation.start_grows_for_shelves import validate_grow_id 
from unittest.mock import MagicMock
import pytest


def test_validate_grow_id_fail():
    AppConfig = MagicMock()
    grow_id = 4
    assert validate_grow_id(AppConfig, {"grow": {"blow": grow_id}}) != (True, str(grow_id))


def test_validate_grow_id_pass():
    AppConfig = MagicMock()
    grow_id = 4
    assert validate_grow_id(AppConfig, {"grow": {"grow_id": grow_id}}) == (True, str(grow_id))
   
