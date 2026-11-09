from django.contrib import admin

from .models import Booking, Category, Comment, Profile, Tour

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Tour)
admin.site.register(Booking)
admin.site.register(Comment)
