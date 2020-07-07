from app.models.grow import Grow
from datetime import datetime, timedelta
from time import mktime
from dateutil.parser import parse


def test_create_grow():
    start = datetime.now() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow = Grow(1, 2, 3, 4, 5, start, end)

    assert grow.room_id == 1
    assert grow.rack_id == 2
    assert grow.shelf_id == 3
    assert grow.recipe_id == 4
    assert grow.recipe_phase_num == 5
    assert grow.start_datetime == start
    assert grow.end_datetime == end


def test_create_grow_from_json():
    start = datetime.now().utcnow() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now
    start = start.utcnow()
    end = end.utcnow()
    expected_start_datetime = datetime.fromtimestamp(
        mktime(parse(start.isoformat()).utctimetuple())
    )
    expected_end_datetime = datetime.fromtimestamp(
        mktime(parse(end.isoformat()).utctimetuple())
    )

    grow = Grow.from_json(
        {
            "room_id": 1,
            "rack_id": 2,
            "shelf_id": 3,
            "recipe_id": 4,
            "recipe_phase_num": 5,
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
        }
    )

    assert grow.room_id == 1
    assert grow.rack_id == 2
    assert grow.shelf_id == 3
    assert grow.recipe_id == 4
    assert grow.recipe_phase_num == 5
    assert grow.start_datetime == expected_start_datetime
    assert grow.end_datetime == expected_end_datetime
