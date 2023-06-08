from django.db import models
from poll.models import Poll
from django.db.utils import IntegrityError
from users.models import Profile
from datetime import datetime


class PollSuggestion(models.Model):
    time = models.DateTimeField()
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        all_suggestions = PollSuggestion.objects.all()
        suggested_times = [poll_suggestion.time for poll_suggestion in all_suggestions]
        current_time = datetime.now()
        if self.time in suggested_times:
            raise IntegrityError
        if self.time < current_time:
            raise IntegrityError
        super().save(*args, **kwargs)


class UserPollSuggestion(models.Model):
    suggestion_id = models.ForeignKey(PollSuggestion, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
