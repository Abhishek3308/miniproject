from django.urls import path
from . import views 

urlpatterns = [
    # Authentication
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),

    # Profiles
    path('user/profile/', views.user_profile, name='user_profile'),
    path('organization/profile/', views.organization_profile, name='organization_profile'),
    path('user/profile/edit/', views.edit_userprofile, name='edit_userprofile'),
    path('organization/profile/edit/',views.edit_organization_profile, name='edit_organization_profile'),
    # path('organization/<int:id>/', views.organization_detail, name='organization_detail'),
    path('organization/delete/<int:id>/', views.delete_organization, name='delete_organization'),
    path('admin_dashboard/users/delete/<int:id>/',views.delete_user, name='delete_user'),


    # Idea Management
    path('ideas/<int:idea_id>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:idea_id>/edit/', views.edit_idea, name='edit_idea'),
    path('ideas/<int:idea_id>/delete/', views.delete_idea, name='delete_idea'),
    path('ideas/', views.idea_list, name='idea_list'),
    path("post_idea/", views.post_idea, name="post_idea"),
    # path('delete_idea/', views.delete_idea, name='delete_idea'),
    path('search_ideas/',views.search_ideas, name='search_ideas'),
    # path("explore-ideas/", views.explore_ideas, name="explore_ideas"),
    path("investors/", views.investors, name="investors"),
    path("admin_dashboard/",views.admin_dashboard, name="admin_dashboard"),
    path("admin_dashboard/users/",views. admin_users, name="admin_users"),
    path("admin_dashboard/organizations/",views. admin_organizations, name="admin_organizations"),
    path("admin_dashboard/ideas/",views. admin_ideas, name="admin_ideas"),
    path("admin/events/",views.admin_events, name="admin_events"),
    path("admin/trending-ideas/",views.admin_trending_ideas, name="admin_trending_ideas"),
    path("dashboard/events/", views.admin_events, name="admin_events"),
    
    path('notifications/',views.notifications_view, name='notifications'),
    path('post-event/',views.post_event_view, name='post_event'),
    path("events/",views.events_view, name="events"),
    path('events/<int:event_id>/', views.event_details, name='event_details'),
    path('dashboard/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('user-growth/',views.user_growth_view, name='user_growth'),

    path('your-ideas/', views.your_ideas_view, name='your_ideas'),
    path('admin_dashboard/ideas/<int:idea_id>/delete/', views.admin_delete_idea, name='admin_delete_idea'),
    path('your-events/', views.your_events_view, name='your_events'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('profile/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('profile/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('profile/<str:username>/followers/', views.view_followers, name='view_followers'),
    path('profile/<str:username>/following/', views.view_following, name='view_following'),


]
