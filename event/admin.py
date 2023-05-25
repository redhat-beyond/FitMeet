from django.contrib import admin
from .models import Event, UserEvent


class EventFilter(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "location",
        "is_private",
        "max_participants",
        "participants_num",
        "start_time",
        "end_time",
    )
    list_filter = ("category", "location", "is_private", "max_participants", "participants_num", "start_time")


class UserEventFilter(admin.ModelAdmin):
    list_display = ("id", "userID_id", "eventID_id", "teamID_id", "isEventAdmin")
    list_filter = ("userID", "eventID", "teamID", "isEventAdmin")


admin.site.register(Event, EventFilter)
admin.site.register(UserEvent, UserEventFilter)
