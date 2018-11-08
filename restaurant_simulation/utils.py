"""
 Generating of requests
"""


def human_readable_time(time):
    """
    Convert global time in the system to the human-readable time
    :return: human-readable time as a string
    """
    day = str(time // (3600 * 24) + 1)
    hours = str(time // 3600 % 24)
    minutes = str((time // 60) % 60)
    seconds = str(time % 60)

    if len(minutes) != 2:
        minutes = "0" + minutes

    if len(seconds) != 2:
        seconds = "0" + seconds

    return "Day " + day + " " + hours + ":" + minutes + ":" + seconds
