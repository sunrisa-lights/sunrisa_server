def write_schedule_for_shelf(conn, shelf_id: int, start_time: str, end_time: str, power_level: int, red_level: int, blue_level: int) -> None:
    sql = (
        "INSERT INTO `schedules` VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    cursor = conn.cursor()
    cursor.execute(sql, (None, shelf_id, start_time, end_time, power_level, red_level, blue_level))
    cursor.close()


def write_schedule_for_room(conn, room_id: int, start_time: str, end_time: str, power_level: int, red_level: int, blue_level: int) -> None:
    sql = (
        "INSERT INTO `schedules` VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    cursor = conn.cursor()
    cursor.execute(sql, (room_id, None, start_time, end_time, power_level, red_level, blue_level))
    cursor.close()


def create_schedule_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS schedules(
    room_id INT,
    shelf_id INT,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    power_level INT NOT NULL,
    red_level INT NOT NULL,
    blue_level INT NOT NULL,
    PRIMARY KEY (shelf_id, start_time, end_time),
    CONSTRAINT fk_shelf_schedule
    FOREIGN KEY (shelf_id)
        REFERENCES shelves(shelf_id),
    CONSTRAINT fk_room_schedule
    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
