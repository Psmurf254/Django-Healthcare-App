from django.contrib import admin
from . models import About, Contact,FAQ, Notification


admin.site.register(About)
admin.site.register(Notification)
admin.site.register(Contact)
admin.site.register(FAQ)

