from django.contrib import admin
from register.models import Candidate, User_Registration, Bicycle, HandoutEvent
from register.models import Invitation

admin.site.register(Candidate)
admin.site.register(User_Registration)
admin.site.register(HandoutEvent)
admin.site.register(Bicycle)
admin.site.register(Invitation)
