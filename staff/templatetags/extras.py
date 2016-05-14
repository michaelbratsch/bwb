from django import template

from future.utils import iteritems

from register.models import HandoutEvent, Candidate, Bicycle, CandidateStatus


register = template.Library()


@register.inclusion_tag('staff/event_sidebar.html')
def get_event_list(event_id):
    events = list(HandoutEvent.objects.all())
    events.sort(key=lambda e: e.due_date)
    return {'events': events,
            'event_id': event_id}


@register.inclusion_tag('staff/candidate_sidebar.html')
def get_candidate_list(candidate_id):
    def get_status_and_canidates():
        candidate_status_list = [
            member for _, member in iteritems(CandidateStatus.__members__)]
        candidate_status_list.sort(key=lambda x: x.value)

        candidates = list(Candidate.objects.all())
        candidates.sort(key=lambda x: x.last_name)

        for candidate_status in candidate_status_list:
            yield candidate_status, \
                [candidate for candidate in candidates if
                 candidate.current_status == candidate_status]

    return {'status_and_candidates': get_status_and_canidates(),
            'candidate_id': candidate_id}


@register.inclusion_tag('staff/bicycle_sidebar.html')
def get_bicycle_list(bicycle_id):
    bicycles = list(Bicycle.objects.all())
    bicycles.sort(key=lambda b: b.bicycle_number)
    return {'bicycles': bicycles,
            'bicycle_id': bicycle_id}
