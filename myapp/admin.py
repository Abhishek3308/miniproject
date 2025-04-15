from django.contrib import admin
from django.urls import path
from .models import User, UserProfile, OrganizationProfile,Idea,PostEvent,Follow
from .views import user_growth_view  # Import the correct view


admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(OrganizationProfile)
admin.site.register(Idea)
admin.site.register(PostEvent)
admin.site.register(Follow)



class CustomAdmin(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('user-growth/', user_growth_view, name='admin_user_growth'),  # Custom route
        ]
        return custom_urls + urls

admin.site = CustomAdmin()
