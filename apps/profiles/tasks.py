from besteats.celery import app

from apps.profiles.models import Profile
from apps.utils.helper import get_config_value


@app.task()
def reset_daily_votes_for_all_profles():
    Profile.objects.update(daily_votes=get_config_value("USER_DAILY_VOTES"))
