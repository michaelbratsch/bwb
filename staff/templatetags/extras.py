from django import template

from register.forms import open_for_registration as open_registration
from register.models import HandoutEvent, Candidate, Bicycle


register = template.Library()


@register.simple_tag
def open_for_registration():
    if open_registration():
        return "OPEN"
    else:
        return ""


@register.inclusion_tag('staff/event_sidebar.html')
def get_event_list(event_id):
    events = list(HandoutEvent.objects.all())
    events.sort(key=lambda e: e.due_date)
    return {'events': events,
            'event_id': event_id}


@register.inclusion_tag('staff/candidate_sidebar.html')
def get_candidate_list(candidate_id):
    return {'status_and_candidates': Candidate.get_status_and_candidates(),
            'candidate_id': candidate_id}


@register.inclusion_tag('staff/bicycle_sidebar.html')
def get_bicycle_list(bicycle_id):
    bicycles = list(Bicycle.objects.all())
    bicycles.sort(key=lambda b: b.bicycle_number)
    return {'bicycles': bicycles,
            'bicycle_id': bicycle_id}
