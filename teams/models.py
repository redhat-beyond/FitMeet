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
        team1 = Teams(name=f"{event_id}-Team1")
        team1.save()
        team2 = Teams(name=f"{event_id}-Team2")
        team2.save()

        user_ids_1 = [user_event.userID for user_event in users_events[:team_size]]
        list1 = UserEvent.objects.filter(userID__in=user_ids_1, eventID=event_id)
        list1.update(teamID=team1)
        user_names_1 = [user_event.userID.user.username for user_event in list1]  # Extract user names

        user_ids_2 = [user_event.userID for user_event in users_events[team_size:]]
        list2 = UserEvent.objects.filter(userID__in=user_ids_2, eventID=event_id)
        list2.update(teamID=team2)
        user_names_2 = [user_event.userID.user.username for user_event in list2]  # Extract user names
        return user_names_1, user_names_2
