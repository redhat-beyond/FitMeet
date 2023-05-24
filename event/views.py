from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .forms import EventForm
from location.models import Location
from category.models import Category
from .models import Event, UserEvent
from .models import Teams


def create_event(request, user_id):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                event_id = Event.manager.create_event(
                    category_id=data['category'].id,
                    location_id=data['location'].id,
                    name=data['name'],
                    max_participants=data['max_participants'],
                    start_time=data['start_time'],
                    end_time=data['end_time'],
                    is_private=data['is_private'],
                    poll_end_time=data['poll_end_time'],
                    poll_suggestions=data['poll_max_suggestions'],
                    user_id=user_id,
                )
                return redirect(f'/{user_id}/event/info/?id={event_id}')
            except ValidationError as err:
                return render(request, 'event/create_event.html', {'form': form, 'error': err.message}, status=409)
        else:
            return render(
                request,
                'event/create_event.html',
                {'form': form, 'error': list(form.errors.values())[0][0]},
                status=409,
            )
    else:
        form = EventForm()
        return render(request, 'event/create_event.html', {'form': form})


def view_event(request, user_id):
    event_id = request.GET["id"]
    event = Event.manager.get(id=event_id)
    if request.method == "POST":
        Teams.generate_teams(event_id)

    team1 = []
    team2 = []
    users_events = UserEvent.objects.filter(eventID=event_id)
    if len(users_events) > 0 and users_events[0].teamID:
        teams = list(set([user_event.teamID for user_event in users_events]))
        team1 = [user.userID.user.username for user in
                 UserEvent.objects.filter(teamID=teams[0].id)]
        team2 = [user.userID.user.username for user in
                 UserEvent.objects.filter(teamID=teams[1].id)]
    context = {
        'team1': team1,
        'team2': team2,
        'event': event
    }
    return render(request, 'event/event_info.html', context)


def event_list(request, user_id):
    events = Event.manager.all()

    category = request.GET.get('Choose_Category', 'None')
    if category != 'None':
        events = events.filter(category__name=category)

    location = request.GET.get('Choose_Location', 'None')
    if location != 'None':
        events = events.filter(location__name=location)

    order_by = request.GET.get('Order_By', 'None')
    if order_by == 'Time':
        events = events.order_by('start_time')
    elif order_by == 'Participants':
        events = events.order_by('participants_num')

    if not request.user.is_authenticated:
        user_id = None
    locations = Location.objects.values_list('name', flat=True)
    categories = Category.objects.values_list('name', flat=True)
    context = {'events': events, 'locations': locations, 'categories': categories, 'user_id': user_id}
    return render(request, 'event/all_events.html', context)


def view_generate_teams(request):
    event_id = request.GET["id"]
    event = Event.manager.get(id=event_id)
    team1, team2 = Teams.generate_teams(event_id)
    context = {
        'team1': team1,
        'team2': team2,
        'event': event
    }
    return render(request, 'event/event_info.html', context)
