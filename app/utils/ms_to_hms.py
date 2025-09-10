import datetime


def ms_to_hms(ms):
    segundos = ms // 1000 if ms else 0
    return str(datetime.timedelta(seconds=segundos))