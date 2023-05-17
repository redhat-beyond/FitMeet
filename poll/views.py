# from django.shortcuts import render
from django.shortcuts import render
from .models import Poll


def view_poll(request):
    poll_id = request.GET["id"]
    poll = Poll.manager.get(id=poll_id)
    return render(request, 'event/event_info.html', {'poll': poll})
