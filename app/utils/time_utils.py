from datetime import datetime
from dateutil.parser import parse
import calendar

# takes an iso8601 formatted string and returns a python UTC datetime
def iso8601_string_to_datetime(date_string: str) -> datetime:
    parsed_datetime = datetime.utcfromtimestamp(
        calendar.timegm(parse(date_string).utctimetuple())
    )
    return parsed_datetime
