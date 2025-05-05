from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Authentication
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),

    # Profiles
    # For user profiles by username
    # For viewing your own profile (no username needed)
        # User Profile (for the logged-in user's own profile)
    path('user/profile/', views.user_profile, name='my_user_profile'),
    path('user/profile/edit/', views.edit_userprofile, name='edit_userprofile'),
    path('user/profile/<str:username>/', views.view_user_profile, name='user_profile'),

    path('organization/profile/edit/',views.edit_organization_profile, name='edit_organization_profile'),


    # Organization Profile (for the logged-in organization's own profile)
    path('organization/profile/', views.organization_profile, name='my_organization_profile'),

    # Organization Profile (for other organization's profiles)
    path('organization/profile/<str:username>/', views.view_organization_profile, name='organization_profile'),
    # path('organization/<int:id>/', views.organization_detail, name='organization_detail'),
    path('organization/delete/<int:id>/', views.delete_organization, name='delete_organization'),
    path('admin_dashboard/users/', views.admin_users, name='admin_users'),
    path('admin_dashboard/users/delete/<int:user_id>/', views.admin_delete_user, name='delete_user'),
    path('admin_dashboard/users/toggle-status/<int:user_id>/', views.admin_toggle_user_status, name='toggle_user_status'),
    path('toggle_organization_status/<int:org_id>/', views.admin_toggle_organization_status, name='toggle_organization_status'),
    


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
    path("admin_dashboard/events/",views.admin_events, name="admin_events"),
    path("dashboard/events/", views.admin_events, name="admin_delete_events"),
    # path('admin_dashboard/users/<int:user_id>/', views.admin_view_user, name='view_user'),
    
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
    path('like/<int:idea_id>/', views.like_idea, name='like_idea'),
    path('ideas/<int:idea_id>/unlike/', views.unlike_idea, name='unlike_idea'),
    path('comment/<int:idea_id>/', views.comment_idea, name='comment_idea'),
    # path('comment/<int:comment_id>/react/', views.react_to_comment, name='react_to_comment'),
    path('report/<int:idea_id>/', views.report_idea, name='report_idea'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('about-us/', views.about_us, name='about_us'),
    path('admin_reports/', views.admin_reports, name='admin_reports'),
    path('add_user/', views.add_user, name='add_user'),
    path('send-announcement/', views.send_announcement_view, name='send_announcement'),
    path('rate_idea/<int:idea_id>/', views.rate_idea, name='rate_idea'),






     path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             email_template_name='password_reset_email.html',
             subject_template_name='password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ),
         name='password_reset_complete'),
]


