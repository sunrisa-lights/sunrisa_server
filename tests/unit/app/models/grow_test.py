from app.models.grow import Grow
from datetime import datetime, timedelta, timezone


def test_create_grow():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start -= timedelta(microseconds=start.microsecond)
    end = start + timedelta(0, 2)  # 5 seconds from now

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

    grow = Grow(
        1,
        2,
        start,
        end,
        True,
        True,
        5,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )

    assert grow.grow_id == 1
    assert grow.recipe_id == 2
    assert grow.start_datetime == start
    assert grow.estimated_end_datetime == end
    assert grow.is_finished == True
    assert grow.all_fields_complete == True
    assert grow.olcc_number == 5
    assert grow.current_phase == 6
    assert grow.is_new_recipe == True
    assert grow.tag_set == "tag_set"
    assert grow.nutrients == "nutrients"
    assert grow.weekly_reps == 1000
    assert grow.pruning_date_1 == pruning_date_1
    assert grow.pruning_date_2 == pruning_date_2
    assert grow.harvest_weight == 7
    assert grow.trim_weight == 70
    assert grow.dry_weight == 700
    assert grow.notes == "notes"


def test_create_grow_from_json():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start -= timedelta(microseconds=start.microsecond)
    end = start + timedelta(0, 2)  # 5 seconds from now

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

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
            "tag_set": "test_tag_set",
            "nutrients": "test_nutrients",
            "weekly_reps": 1000,
            "pruning_date_1": pruning_date_1.isoformat(),
            "pruning_date_2": pruning_date_2.isoformat(),
            "harvest_weight": 7,
            "trim_weight": 70,
            "dry_weight": 700,
            "notes": "test_notes",
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
    assert grow.tag_set == "test_tag_set"
    assert grow.nutrients == "test_nutrients"
    assert grow.weekly_reps == 1000
    assert grow.pruning_date_1 == pruning_date_1
    assert grow.pruning_date_2 == pruning_date_2
    assert grow.harvest_weight == 7
    assert grow.trim_weight == 70
    assert grow.dry_weight == 700
    assert grow.notes == "test_notes"


def test_create_grow_from_json_string_format():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start -= timedelta(microseconds=start.microsecond)
    end = start + timedelta(0, 2)  # 5 seconds from now

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

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
            "tag_set": "test_tag_set",
            "nutrients": "test_nutrients",
            "weekly_reps": 1000,
            "pruning_date_1": pruning_date_1.strftime("%Y-%m-%d %H:%M:%S"),
            "pruning_date_2": pruning_date_2.strftime("%Y-%m-%d %H:%M:%S"),
            "harvest_weight": 7,
            "trim_weight": 70,
            "dry_weight": 700,
            "notes": "test_notes",
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
    assert grow.tag_set == "test_tag_set"
    assert grow.nutrients == "test_nutrients"
    assert grow.weekly_reps == 1000
    assert grow.pruning_date_1 == pruning_date_1
    assert grow.pruning_date_2 == pruning_date_2
    assert grow.harvest_weight == 7
    assert grow.trim_weight == 70
    assert grow.dry_weight == 700
    assert grow.notes == "test_notes"


def test_grow_to_json():
    start = datetime.utcnow() + timedelta(0, 4)
    start -= timedelta(microseconds=start.microsecond)
    end = start + timedelta(0, 2)

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

    grow_to_json = Grow(
        1,
        2,
        start,
        end,
        True,
        True,
        5,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )

    assert grow_to_json.to_json() == {
        "grow_id": 1,
        "recipe_id": 2,
        "start_datetime": start.replace(microsecond=0).isoformat(),
        "estimated_end_datetime": end.replace(microsecond=0).isoformat(),
        "is_finished": True,
        "all_fields_complete": True,
        "olcc_number": 5,
        "current_phase": 6,
        "is_new_recipe": True,
        "tag_set": "tag_set",
        "nutrients": "nutrients",
        "weekly_reps": 1000,
        "pruning_date_1": pruning_date_1.isoformat(),
        "pruning_date_2": pruning_date_2.isoformat(),
        "harvest_weight": 7,
        "trim_weight": 70,
        "dry_weight": 700,
        "notes": "notes",
    }


def test_grow__str__():
    start = datetime.utcnow() + timedelta(0, 4)
    end = start + timedelta(0, 2)

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

    grow = Grow(
        1,
        2,
        start,
        end,
        True,
        True,
        5,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    grow2 = Grow(
        1,
        2,
        start,
        end,
        True,
        True,
        5,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    assert str(grow2) == str(grow)


def test_grow__hash__():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    end2 = start + timedelta(0, 2)

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

    grow3 = Grow(
        2,
        3,
        start,
        end2,
        False,
        False,
        4,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    grow4 = Grow(
        2,
        3,
        start,
        end2,
        False,
        False,
        4,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    assert hash(grow4) == hash(grow3)


def test_grow__hash__unequal():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start2 = datetime.utcnow() + timedelta(0, 4)
    end2 = start + timedelta(0, 2)

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

    grow3 = Grow(
        2,
        3,
        start,
        end2,
        True,
        False,
        4,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    grow4 = Grow(
        2,
        3,
        start2,
        end2,
        True,
        True,
        4,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    assert hash(grow3) != hash(grow4)


def test__eq__():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

    grow2 = Grow(
        1,
        2,
        start,
        end,
        True,
        True,
        3,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    grow3 = Grow(
        1,
        2,
        start,
        end,
        True,
        True,
        3,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )

    assert grow2 == grow3


def test__eq__fail():
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    start2 = datetime.utcnow() + timedelta(0, 4)
    end = start + timedelta(0, 2)  # 5 seconds from now

    pruning_date_1 = start + timedelta(7, 0)  # 7 days from now
    pruning_date_2 = start + timedelta(14, 0)  # 14 days from now

    grow3 = Grow(
        1,
        2,
        start,
        end,
        True,
        False,
        6,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )
    grow4 = Grow(
        1,
        2,
        start2,
        end,
        False,
        True,
        6,
        6,
        True,
        "tag_set",
        "nutrients",
        1000,
        pruning_date_1,
        pruning_date_2,
        7,
        70,
        700,
        "notes",
    )

    assert grow3 != grow4
