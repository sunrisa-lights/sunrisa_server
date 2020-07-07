from app.models.grow import Grow
from datetime import datetime, timedelta, timezone


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
    # needs to round because calendar.timegm is converting to seconds losing microsecond precision
    assert grow.start_datetime == start - timedelta(microseconds=start.microsecond)
    assert grow.end_datetime == end - timedelta(microseconds=end.microsecond)


def test_create_grow_from_json_string_format():
    start = datetime.now().utcnow() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now


    grow = Grow.from_json(
        {
            "room_id": 1,
            "rack_id": 2,
            "shelf_id": 3,
            "recipe_id": 4,
            "recipe_phase_num": 5,
            "start_datetime": start.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "end_datetime": end.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
    )

    assert grow.room_id == 1
    assert grow.rack_id == 2
    assert grow.shelf_id == 3
    assert grow.recipe_id == 4
    assert grow.recipe_phase_num == 5
    # needs to round because calendar.timegm is converting to seconds losing microsecond precision
    assert grow.start_datetime == start - timedelta(microseconds=start.microsecond)
    assert grow.end_datetime == end - timedelta(microseconds=end.microsecond)



def test_to_json():
    start5 = datetime.utcnow() + timedelta(0, 4)
    end = start5 + timedelta(0, 2)
    grow_to_json = Grow(1, 2, 3, 4, 5, start5, end)
    assert grow_to_json.to_json() == {
        "room_id": 1,
        "rack_id": 2,
        "shelf_id": 3,
        "recipe_id": grow_to_json.recipe_id,
        "recipe_phase_num": grow_to_json.recipe_phase_num,
        "start_datetime": grow_to_json.start_datetime.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "end_datetime": grow_to_json.end_datetime.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
    }


def test_to_job_id():
    date_format = "%b %d %Y %H:%M:%S"
    start = datetime.now() + timedelta(0, 3)  # 3 seconds from now
    start2 = datetime.now() + timedelta(0, 4)
    end2 = start + timedelta(0, 2)
    grow = Grow(2, 3, 4, 5, 6, start, end2)
    assert grow.to_job_id() == "room-2-rack-3-shelf-4-recipe-5-phase-6-start-{}-end-{}".format(start.strftime(date_format), end2.strftime(date_format))


def test__str__():
    start6 = datetime.now() + timedelta(0, 4)
    end = start6 + timedelta(0, 2)
    grow = Grow(1, 2, 3, 4, 5, start6, end)
    grow2 = Grow(1, 2, 3, 4, 5, start6, end)
    assert str(grow2) == str(grow)


def test__hash__():
    start = datetime.now() + timedelta(0, 3)  # 3 seconds from now
    end2 = start + timedelta(0, 2)
    grow3 = Grow(2, 3, 4, 5, 6, start, end2)
    grow4 = Grow(2, 3, 4, 5, 6, start, end2)
    assert hash(grow4) == hash(grow3)


def test__hash__fail():
    start = datetime.now() + timedelta(0, 3)  # 3 seconds from now
    start2 = datetime.now() + timedelta(0, 4)
    end2 = start + timedelta(0, 2)
    grow3 = Grow(2, 3, 4, 5, 6, start, end2)
    grow4 = Grow(2, 3, 4, 5, 6, start2, end2)
    assert hash(grow3) != hash(grow4)


def test__eq__():
    start = datetime.now() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow2 = Grow(1, 2, 3, 4, 5, start, end)
    grow3 = Grow(1, 2, 3, 4, 5, start, end)

    assert grow2 == grow3


def test__eq__fail():
    start = datetime.now() + timedelta(0, 3)  # 3 seconds from now
    start2 = datetime.now() + timedelta(0, 4)
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow3 = Grow(1, 2, 3, 4, 5, start, end)
    grow4 = Grow(1, 2, 3, 4, 5, start2, end)

    assert grow3 != grow4
