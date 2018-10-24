from django.contrib import admin
from .models import Event, UserBook, Profile

# Register your models here.
admin.site.register(Event)
admin.site.register(UserBook)
admin.site.register(Profile)