import traceback
from typing import List


def sync_grows(app_config) -> None:
    print("In sync_grows!")

    socketio = app_config.sio

    socketio.emit("sync_grows", {})
    print("sync_grows event emitted")


"""
    db_conn = None
    try:
        db_conn = app_config.db._new_transaction()

        # check if this is the last run and we need to schedule the next phase
        schedule_next_phase_if_needed(
            app_config, db_conn, shelf_grows, grow_phase
        )

        # commit the transaction
        db_conn.commit()

        # print the datetime as well to help debug connection aborted errors (to associate with mySQL logs)
        print("Successfully scheduled grow for shelf!", datetime.utcnow())
    except Exception as e:
        exception_str: str = str(e)
        print(
            "Error with scheduling next grow phase:",
            exception_str,
            traceback.format_exc(),
        )
    finally:
        if db_conn:
            # close db_conn if it was opened
            db_conn.close()
"""
