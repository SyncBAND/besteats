###################################
# Django app for storing dynamic settings in pluggable
# backends with an integration with the Django admin app.
# https://django-constance.readthedocs.io/en/latest/
###################################
CONSTANCE_CONFIG_FIELDSETS = {
    "Restaurant Settings": (
        "USER_DAILY_VOTES",
    ),
}

CONSTANCE_CONFIG = {
    "USER_DAILY_VOTES": (
        10,
        "Votes each user is given a day",
        int
    )
}
