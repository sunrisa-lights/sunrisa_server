from app.models.grow import Grow
from datetime import datetime, timedelta, timezone


def test_create_grow():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start -= timedelta(microseconds=start.microsecond)
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow = Grow(1, 2, start, end, True, True, 5, 6, True)

    assert grow.grow_id == 1
    assert grow.recipe_id == 2
    assert grow.start_datetime == start
    assert grow.estimated_end_datetime == end
    assert grow.is_finished == True
    assert grow.all_fields_complete == True
    assert grow.olcc_number == 5
    assert grow.current_phase == 6
    assert grow.is_new_recipe == True


def test_create_grow_from_json():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start -= timedelta(microseconds=start.microsecond)
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow = Grow.from_json(
        {
            "grow_id": 1,
            "recipe_id": 2,
            "start_datetime": start.isoformat(),
            "estimated_end_datetime": end.isoformat(),
            "is_finished": True,
            "all_fields_complete": True,
            "olcc_number": 5,
            "current_phase": 6,
            "is_new_recipe": True,
        }
    )

    assert grow.grow_id == 1
    assert grow.recipe_id == 2
    # needs to round because calendar.timegm is converting to seconds losing microsecond precision
    assert grow.start_datetime == start
    assert grow.estimated_end_datetime == end
    assert grow.is_finished == True
    assert grow.all_fields_complete == True
    assert grow.olcc_number == 5
    assert grow.current_phase == 6
    assert grow.is_new_recipe == True


def test_create_grow_from_json_string_format():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start -= timedelta(microseconds=start.microsecond)
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow = Grow.from_json(
        {
            "grow_id": 1,
            "recipe_id": 2,
            "start_datetime": start.strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_end_datetime": end.strftime("%Y-%m-%d %H:%M:%S"),
            "is_finished": True,
            "all_fields_complete": True,
            "olcc_number": 5,
            "current_phase": 6,
            "is_new_recipe": True,
        }
    )

    assert grow.grow_id == 1
    assert grow.recipe_id == 2
    # needs to round because calendar.timegm is converting to seconds losing microsecond precision
    assert grow.start_datetime == start
    assert grow.estimated_end_datetime == end
    assert grow.is_finished == True
    assert grow.all_fields_complete == True
    assert grow.olcc_number == 5


def test_to_json():
    start5 = datetime.utcnow() + timedelta(0, 4)
    start5 -= timedelta(microseconds=start5.microsecond)
    end = start5 + timedelta(0, 2)
    grow_to_json = Grow(1, 2, start5, end, True, True, 5, 6, True)
    assert grow_to_json.to_json() == {
        "grow_id": 1,
        "recipe_id": 2,
        "start_datetime": start5.replace(microsecond=0).isoformat(),
        "estimated_end_datetime": end.replace(microsecond=0).isoformat(),
        "is_finished": True,
        "all_fields_complete": True,
        "olcc_number": 5,
        "current_phase": 6,
        "is_new_recipe": True,
    }


def test__str__():
    start6 = datetime.utcnow() + timedelta(0, 4)
    end = start6 + timedelta(0, 2)
    grow = Grow(1, 2, start6, end, True, True, 5, 6, True)
    grow2 = Grow(1, 2, start6, end, True, True, 5, 6, True)
    assert str(grow2) == str(grow)


def test__hash__():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    end2 = start + timedelta(0, 2)
    grow3 = Grow(2, 3, start, end2, False, False, 4, 6, True)
    grow4 = Grow(2, 3, start, end2, False, False, 4, 6, True)
    assert hash(grow4) == hash(grow3)


def test__hash__fail():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start2 = datetime.utcnow() + timedelta(0, 4)
    end2 = start + timedelta(0, 2)
    grow3 = Grow(2, 3, start, end2, True, False, 4, 6, True)
    grow4 = Grow(2, 3, start2, end2, True, True, 4, 6, True)
    assert hash(grow3) != hash(grow4)


def test__eq__():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow2 = Grow(1, 2, start, end, True, True, 3, 6, True)
    grow3 = Grow(1, 2, start, end, True, True, 3, 6, True)

    assert grow2 == grow3


def test__eq__fail():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start2 = datetime.utcnow() + timedelta(0, 4)
    end = start + timedelta(0, 2)  # 5 seconds from now

    grow3 = Grow(1, 2, start, end, True, False, 6, 6, True)
    grow4 = Grow(1, 2, start2, end, False, True, 6, 6, True)

    assert grow3 != grow4
