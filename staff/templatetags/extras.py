from django import template
from register.models import Event

register = template.Library()


@register.inclusion_tag('staff/event_sidebar.html')
def get_event_list(event_id=None):
    events = list(Event.objects.all())
    events.sort(key=lambda e: e.due_date)
    return {'events': events,
            'event_id': event_id}
