from django.contrib import admin
from register.models import Candidate, UserRegistration, Bicycle, HandoutEvent
from register.models import Invitation

admin.site.register(Candidate)
admin.site.register(UserRegistration)
admin.site.register(HandoutEvent)
admin.site.register(Bicycle)
admin.site.register(Invitation)
