
import calendar
import datetime


def get_current_time():
    """
    Mělo by se jednat o nejspolehlivější a nejpřesnější řešení,
    které vrací vždy aktalní čas v UTC jako UNIX timestamp.
    """
    return calendar.timegm(datetime.datetime.utcnow().utctimetuple())


def to_utc(seconds, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Převede čas v sekundách na lidsky čitelný formát v UTC zóně.
    """
    return datetime.datetime.utcfromtimestamp(int(seconds)).strftime(format_string)


def to_local(seconds, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Prevede cas v sekundach na lidsky citelny format v lokalni zone.
    """
    return datetime.datetime.fromtimestamp(int(seconds)).strftime(format_string)
