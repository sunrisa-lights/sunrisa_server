def write_schedule_for_shelf(conn, shelf_id: int, start_time: str, end_time: str):
    sql = (
        "INSERT INTO `schedules` VALUES (%s, %s, %s)"
    )
    conn.cursor().execute(sql, (shelf_id, start_time, end_time))


def create_schedule_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS schedules(
    shelf_id INT NOT NULL,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (shelf_id, start_time, end_time),
    CONSTRAINT fk_shelf_schedule
    FOREIGN KEY (shelf_id)
        REFERENCES shelves(shelf_id)
    );
    """
    conn.cursor().execute(sql)
