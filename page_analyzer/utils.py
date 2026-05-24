def format_date(value, format="%Y-%m-%d"):
    if value is None:
        return ""
    return value.strftime(format)
