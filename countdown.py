import datetime
from math import floor

def countdown(input_date):
    time = input_date
    time_days = floor(time / 86400)

    if time_days == 2:
        days = "يومان"
        time_days = ""
    elif time_days == 1:
        days = "يوم"
        time_days = ""
    elif time_days == 0:
        days = ""
        time_days = ""
    elif time_days <= 10:
        days = "أيّام"
    else:
        days = "يوم"

    remainder = f"""{time_days} {days}"""
    return remainder


def hours_countdown(input_time):
    time = input_time
    time_days = floor((time % 86400) / 3600)

    if time_days == 2:
        days = "ساعتان"
        time_days = ""
    elif time_days == 1:
        days = "ساعة"
        time_days = ""
    elif time_days == 0:
        days = ""
        time_days = ""
    elif time_days <= 10:
        days = "ساعات"
    else:
        days = "ساعة"

    remainder = f"""{time_days} {days}"""
    return remainder


def min_countdown(input_time):
    time = input_time
    time_days = floor((time % 3600) / 60)

    if time_days == 2:
        days = "دقيقتان"
        time_days = ""
    elif time_days == 1:
        days = "دقيقة"
        time_days = ""
    elif time_days == 0:
        days = ""
        time_days = ""
    elif time_days <= 10:
        days = "دقائق"
    else:
        days = "دقيقة"

    remainder = f"""{time_days} {days}"""
    return remainder


def sec_countdown(input_time):
    time_days = input_time
    if time_days == 2:
        days = "ثانيتان"
        time_days = ""
    elif time_days == 1:
        days = "ثانية"
        time_days = ""
    elif time_days == 0:
        days = ""
        time_days = ""
    elif time_days <= 10:
        days = "ثواني"
    else:
        days = "ثانية"

    remainder = f"""{time_days} {days}"""
    return remainder



def fullcount(event, goal: datetime, text):
    dt = event.message.date
    unix_time = dt.timestamp()
    messageTime = unix_time + 10800
    remainder = goal.timestamp() - messageTime
    days = remainder / (3600 * 24)
    hours = (remainder % 86400) / 3600
    if remainder > 0:
        response = f"""⏰ باقي على {text}:
{countdown(remainder)}
{goal.date()}
"""
        if days <= 10:
            response = f"""⏰ باقي على {text}:
{countdown(remainder)} و{hours_countdown(remainder)}
{goal.date()}
"""
            if hours < 1 and days > 1:
                response = f"""⏰ باقي على {text}:
{countdown(remainder)}
{goal.date()}
"""
            if days < 1:
                response = f"""⏰ باقي على {text}:
{hours_countdown(remainder)}
{goal.date()}
"""
                if remainder < 3600:
                    response = f"""⏰ باقي على {text}:
{min_countdown(remainder)}
{goal.date()}
"""
                    if 60 > remainder > 0:
                        response = f"""⏰ باقي على {text}:
{sec_countdown(remainder)}
{goal.date()}
"""
                        if remainder<0:
                            return
    return response