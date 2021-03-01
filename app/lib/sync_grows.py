import traceback
from datetime import datetime
from typing import Any, List, Optional
from app.models.shelf_light_record import ShelfLightRecord
from app_config import AppConfig

# Returns true if light recrods saved successfully to DB, false if not
def sync_grows(app_config: AppConfig, light_info: Any) -> bool:
    recorded_at = datetime.now()
    print("LIGHT INFO!:", light_info)
    shelf_light_records: List[ShelfLightRecord] = []
    for room in light_info:
        for rack in light_info[room]:
            for shelf in light_info[room][rack]:
                shelf_light_dict = light_info[room][rack][shelf]
                red = shelf_light_dict.get("red_level")
                blue = shelf_light_dict.get("blue_level")
                power = shelf_light_dict.get("power_level")
                shelf_light_record: ShelfLightRecord = ShelfLightRecord(
                    shelf, rack, room, red, blue, power, recorded_at
                )
                shelf_light_records.append(shelf_light_record)

    try:
        db_conn = app_config.db._new_transaction()
        app_config.db.write_shelf_light_records(db_conn, shelf_light_records)
        db_conn.commit()
        return True
    except Exception as e:
        exception_str: str = str(e)
        print(
            "Error with writing shelf light records",
            light_info,
            exception_str,
            traceback.format_exc(),
        )
        # rollback connection if it exists
        if db_conn:
            db_conn.rollback()
        return False
    finally:
        # close connection if defined
        if db_conn:
            db_conn.close()
