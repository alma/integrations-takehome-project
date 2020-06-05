from datetime import datetime, timedelta

import pytz
from jinja2.utils import Markup


def format_cents_in_euros(cents: int, force_decimals=False) -> str:
    euros = cents / 100
    amount = (
        f"{euros:,.0f}"
        if cents // 100 == euros and not force_decimals
        else f"{euros:,.2f}"
    )
    return f"{amount.replace(',', ' ').replace('.', ',')} €"


def euros(cents, force_decimals=False):
    """ Format cents to euros, |safe filter is not needed """
    euros = format_cents_in_euros(cents, force_decimals=force_decimals)
    return Markup(euros.replace(" ", "&nbsp;"))


def is_today(dt):
    dt = dt.astimezone(pytz.utc)
    return dt.date() == datetime.today().date() if dt else False


def is_yesterday(dt):
    dt = dt.astimezone(pytz.utc)
    return dt.date() == (datetime.today() - timedelta(days=1)).date() if dt else False


MONTHS = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}


def humanized_date(ts, *, add_article=True, force_date=False):
    dt = datetime.utcfromtimestamp(ts)

    if is_today(dt) and not force_date:
        return "aujourd'hui"
    if is_yesterday(dt) and not force_date:
        return "hier"

    article = "le " if add_article else ""
    suffix = "er" if dt.day == 1 else ""
    return f"{article}{dt.day}{suffix} {MONTHS[dt.month]} {dt.year}"


def configure_jinja_env(jinja_env):
    jinja_env.filters["humanized_date"] = humanized_date
    jinja_env.filters["euros"] = euros
