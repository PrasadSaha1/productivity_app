from django import template
import datetime
from datetime import timedelta

register = template.Library()

@register.filter
def format_custom_date(value):
    try:
        # Try to parse the date with MM-DD-YYYY format
        date_obj = datetime.datetime.strptime(value, "%m-%d-%Y")
        formatted_date = date_obj.strftime("%B {day}, %Y").replace("{day}", str(date_obj.day) + get_day_suffix(date_obj.day))
        return f"Scheduled for {formatted_date}"
    except ValueError:
        if value == "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday":
            return "Repeats every day"
        elif value == "never":
            return "Currently never used"
        else:  # specific dates, but not every day
            if value.count(",") == 0:
                return f"Repeats on {value}s"
            new_value = "Repeats on: "
            days_list = value.split(",")
            for day in days_list:
                new_value += f"<br>{day}"  # Use <br> instead of \n
            return new_value



def get_day_suffix(day):
    # Determine the correct suffix for a given day
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]


@register.filter
def duration_in_minutes(start_time, end_time):
    if start_time and end_time:
        duration = timedelta(hours=end_time.hour, minutes=end_time.minute) - \
                   timedelta(hours=start_time.hour, minutes=start_time.minute)
        return duration.total_seconds() / 60  # Convert to minutes
    return 0

@register.filter
def split_string(value, delimiter=","):
    return value.split(delimiter)


@register.filter
def in_list(task_category, category):
    return task_category in category.split(',')
