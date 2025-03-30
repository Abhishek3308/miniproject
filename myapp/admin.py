from django.contrib import admin
from .models import User, UserProfile, OrganizationProfile,Idea

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(OrganizationProfile)
admin.site.register(Idea)

