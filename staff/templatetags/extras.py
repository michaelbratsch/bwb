from django import template
from register.models import Release

register = template.Library()


@register.inclusion_tag('staff/releases.html')
def get_release_list(act_release=None):
    releases = Release.objects.all()
    return {'releases': releases, 'act_release': act_release}
