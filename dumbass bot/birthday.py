from datetime import datetime, timedelta

from config import (
    ASSIGNEES,
    TITLE_INBOX,
    TITLE_POST,
    TITLE_THU,
)


# ============================================================
# HELPERS
# ============================================================

def mention(assignee: str) -> str:
    """
    Returns a Discord mention if the assignee exists,
    otherwise returns the assignee's name.
    """
    discord_id = ASSIGNEES.get(assignee)

    if discord_id:
        return f"<@{discord_id}>"

    return assignee


def is_today(birthday: datetime, today: datetime) -> bool:
    return (
        birthday.day == today.day
        and birthday.month == today.month
    )


def is_tomorrow(birthday: datetime, today: datetime) -> bool:
    tomorrow = today + timedelta(days=1)

    return (
        birthday.day == tomorrow.day
        and birthday.month == tomorrow.month
    )


def build_message(title: str, person: dict) -> str:
    return (
        f"**{title}**\n\n"
        f"**{person['name']}**\n"
        f"Ban: **{person['department']}**\n"
        f"Gen: **{person['gen']}**"
    )


# ============================================================
# MORNING REMINDERS (09:00)
# ============================================================

def morning_messages(people):

    today = datetime.now()

    messages = []

    for person in people:

        # ====================================================
        # GEN <= 20
        # Birthday TODAY -> INBOX
        # ====================================================

        if (
            person["gen"] <= 20
            and is_today(person["birthday"], today)
        ):

            messages.append(
                (
                    mention(person["assignee"]),
                    build_message(TITLE_INBOX, person)
                )
            )

        # ====================================================
        # GEN >= 21
        # Birthday TOMORROW -> THU MERRY
        # ====================================================

        elif (
            person["gen"] >= 21
            and is_tomorrow(person["birthday"], today)
        ):

            messages.append(
                (
                    mention(person["assignee"]),
                    build_message(TITLE_THU, person)
                )
            )

    return messages


# ============================================================
# EVENING REMINDERS (20:00)
# ============================================================

def evening_messages(people):

    today = datetime.now()

    messages = []

    for person in people:

        # ====================================================
        # ONLY GEN >= 21
        # Birthday TODAY -> ĐĂNG MERRY
        # ====================================================

        if (
            person["gen"] >= 21
            and is_today(person["birthday"], today)
        ):

            messages.append(
                (
                    mention(person["assignee"]),
                    build_message(TITLE_POST, person)
                )
            )

    return messages