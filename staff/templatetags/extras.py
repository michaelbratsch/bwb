from django import template
from register.models import HandoutEvent, Candidate

register = template.Library()


@register.inclusion_tag('staff/event_sidebar.html')
def get_event_list(event_id=None):
    events = list(HandoutEvent.objects.all())
    events.sort(key=lambda e: e.due_date)
    return {'events': events,
            'event_id': event_id}


@register.inclusion_tag('staff/candidate_sidebar.html')
def get_candidate_list(candidate_id=None):
    candidates = list(Candidate.objects.all())
    candidates.sort(key=lambda c: c.last_name)
    return {'candidates': candidates,
            'candidate_id': candidate_id}
