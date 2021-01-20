def time_formatter(seconds: float) -> str:
    """ humanize time """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "days, ") if days else "") + \
        ((str(hours) + "hours, ") if hours else "") + \
        ((str(minutes) + "minutes, ") if minutes else "") + \
        ((str(seconds) + "seconds, ") if seconds else "")
    return tmp[:-2]
