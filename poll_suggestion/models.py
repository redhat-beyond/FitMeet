from django.db import models
from poll.models import Poll
from django.db.utils import IntegrityError
from users.models import Profile


class PollSuggestion(models.Model):
    time = models.TimeField()
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        all_suggestions = PollSuggestion.objects.all()
        suggested_times = [poll_suggestion.time for poll_suggestion in all_suggestions]
        if self.time in suggested_times:
            raise IntegrityError
        super().save(*args, **kwargs)


class UserPollSuggestion(models.Model):
    suggestion_id = models.ForeignKey(PollSuggestion, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
