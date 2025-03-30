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

    # Idea Management
    path('ideas/<int:idea_id>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:idea_id>/edit/', views.edit_idea, name='edit_idea'),
    path('ideas/<int:idea_id>/delete/', views.delete_idea, name='delete_idea'),
    path('ideas/', views.idea_list, name='idea_list'),
    path("post-idea/", views.post_idea, name="post_idea"),
    path('delete_idea/', views.delete_idea, name='delete_idea'),
    # path("explore-ideas/", views.explore_ideas, name="explore_ideas"),
    path("investors/", views.investors, name="investors"),
    path("admin_dashboard/",views.admin_dashboard, name="admin_dashboard"),
    path("admin_dashboard/users/",views. admin_users, name="admin_users"),
    path("admin_dashboard/organizations/",views. admin_organizations, name="admin_organizations"),
    path("admin_dashboard/ideas/",views. admin_ideas, name="admin_ideas"),
    

]
