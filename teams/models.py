from django.db import models
from django.db.utils import IntegrityError


class Teams(models.Model):
    name = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        all_teams = Teams.objects.all()
        teams_names = [team.name for team in all_teams]
        if self.name in teams_names:
            raise IntegrityError
        super().save(*args, **kwargs)

    @staticmethod
    def generate_teams(event_id):
        from event.models import UserEvent
        users_events = UserEvent.objects.filter(eventID=event_id)
        team_size = len(users_events) // 2
        team1 = Teams(name="Team1")
        team1.save()
        team2 = Teams(name="Team2")
        team2.save()
        UserEvent.objects.filter(userID__in=[user_event.userID for user_event in users_events[:team_size]],
                                 eventID=event_id).update(teamID=team1)
        UserEvent.objects.filter(userID__in=[user_event.userID for user_event in users_events[team_size:]],
                                 eventID=event_id).update(teamID=team2)
