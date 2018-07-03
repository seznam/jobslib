
import calendar
import datetime


def get_current_time():
    """
    Return current UTC time as a UNIX timestamp.
    """
    return calendar.timegm(datetime.datetime.utcnow().utctimetuple())


def to_utc(seconds, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Return UNIX timestamp *seconds* as a readable UTC time in
    format *format_string*.
    """
    return datetime.datetime.utcfromtimestamp(
        int(seconds)).strftime(format_string)


def to_local(seconds, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Return UNIX timestamp *seconds* as a readable local time in
    format *format_string*.
    """
    return datetime.datetime.fromtimestamp(
        int(seconds)).strftime(format_string)
