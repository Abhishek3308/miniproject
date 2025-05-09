from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages,admin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import User, UserProfile, OrganizationProfile, Idea ,PostEvent ,Follow ,Like,Comment,Report,Notification,IdeaAccess
from .forms import SignUpForm, SignInForm, UserProfileForm, OrganizationProfileForm, IdeaForm ,PostEventForm ,Follow,CommentForm,ReportForm,RatingForm,NotificationSettingsForm
from django.urls import path
from django.template.response import TemplateResponse
from rapidfuzz import fuzz
from django.db.models import Q,Count
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt





# Home Page (Shows All Ideas)
def home_view(request):
    ideas = Idea.objects.all()
    return render(request, "home.html", {"ideas": ideas})

# User Registration
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please sign in.")
            return redirect("signin")
        else:
            # Don't use messages here — just re-render the form with errors
            return render(request, "signup.html", {"form": form})
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})




# User Login
def signin_view(request):
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                
                # Redirect based on user role
                if user.is_superuser:
                    return redirect("admin_dashboard")  # Redirect admin to admin dashboard
                elif user.is_organization:
                    return redirect("home")  # Redirect organizations to home
                elif user.is_user:
                    return redirect("home")  # Redirect users (ideators) to home
                else:
                    return redirect("home")  # Fallback in case of unexpected role

            else:
                messages.error(request, "Invalid username or password")
    
    else:
        form = SignInForm()
    
    return render(request, "signin.html", {"form": form})


# User Logout
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("signin")


# User Profile (View & Update)
@login_required(login_url='signin')
def user_profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username, is_user=True)
    else:
        user = request.user

    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Handling form submission if it's the current user's profile
    if request.method == "POST" and user == request.user:
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile", username=user.username)
    else:
        form = UserProfileForm(instance=profile) if user == request.user else None

    # Calculate follower and following counts
    follower_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    # Get the user's ideas
    ideas = Idea.objects.filter(user=user)

    # Check if the current user is following the profile user
    is_following = Follow.objects.filter(
        follower=request.user,
        following=user
    ).exists()

    # Pass the profile and related information to the template
    return render(request, "user_profile.html", {
        "form": form,
        "follower_count": follower_count,
        "following_count": following_count,
        "ideas": ideas,
        "user_profile": profile,  # This is the profile you passed
        "viewing_own_profile": user == request.user,
        "is_following": is_following,
    })










@login_required(login_url='signin')
def view_user_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)

    # Check if it's a user or an organization profile
    if viewed_user.is_organization:
        return redirect('view_organization_profile', username=viewed_user.username)
    
    if not viewed_user.is_user:
        return redirect('home')

    # Safely get or create user profile
    try:
        profile = UserProfile.objects.get(user=viewed_user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=viewed_user)

    ideas = Idea.objects.filter(user=viewed_user)
    follower_count = Follow.objects.filter(following=viewed_user).count()
    following_count = Follow.objects.filter(follower=viewed_user).count()
    is_following = Follow.objects.filter(follower=request.user, following=viewed_user).exists()

    return render(request, "user_profile.html", {
        "viewed_user": viewed_user,
        "profile": profile,
        "ideas": ideas,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
        "viewing_own_profile": viewed_user == request.user,
    })







@login_required(login_url='signin') 
def edit_userprofile(request):
    # Get or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=request.user.username)  # ✅ fixed
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'edit_profile.html', {'form': form})




# Organization Profile (View & Update)
login_required(login_url='signin')
def organization_profile(request, username=None):
    if username:
        # Viewing another organization's profile
        user = get_object_or_404(User, username=username, is_organization=True)
        org_profile = get_object_or_404(OrganizationProfile, user=user)
        events = PostEvent.objects.filter(user=user)
        profile_pic_url = org_profile.profile_picture.url if org_profile.profile_picture else "/static/images/org-placeholder.png"
        
        return render(request, "organization_profile.html", {
            "organization_profile": org_profile,
            "events": events,
            "profile_pic_url": profile_pic_url,
            "viewing_own_profile": False,
        })
    else:
        # Viewing own profile
        user = request.user
        org_profile, created = OrganizationProfile.objects.get_or_create(user=user)

        if request.method == "POST":
            form = OrganizationProfileForm(request.POST, request.FILES, instance=org_profile)
            if form.is_valid():
                form.save()
                return redirect("organization_profile")
        else:
            form = OrganizationProfileForm(instance=org_profile)

        events = PostEvent.objects.filter(user=user)
        profile_pic_url = org_profile.profile_picture.url if org_profile.profile_picture else "/static/images/org-placeholder.png"

        return render(request, "organization_profile.html", {
            "form": form,
            "organization_profile": org_profile,
            "events": events,
            "profile_pic_url": profile_pic_url,
            "viewing_own_profile": True,
        })


@login_required(login_url='signin')
def view_organization_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    
    # Ensure the user is an organization
    if not viewed_user.is_organization:
        return redirect('home')

    try:
        organization_profile = viewed_user.organization_profile  # Get the OrganizationProfile
    except OrganizationProfile.DoesNotExist:
        return redirect('profile_not_found')  # Handle missing profiles appropriately
    
    events = PostEvent.objects.filter(user=viewed_user)
    
    return render(request, 'organization_profile.html', {
        'organization_profile': organization_profile,
        'viewed_user': viewed_user,
        'events': events,
    })









@login_required(login_url='signin')
def edit_organization_profile(request):
    profile = request.user.organization_profile
    user = request.user  # Get the User object

    if request.method == 'POST':
        profile.company_name = request.POST.get('name', '')
        profile.description = request.POST.get('description', '')

        # Save uploaded image if available
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        # Update username if provided
        new_username = request.POST.get('username', '').strip()
        if new_username and new_username != user.username:
            user.username = new_username
            user.save()  # Save the updated user

        profile.save()

        # Redirect to the organization profile with the updated username
        return redirect('organization_profile', username=user.username)

    profile_picture_url = profile.profile_picture.url if profile.profile_picture else None

    return render(request, 'edit_organization_profile.html', {
        'form': profile,
        'profile_picture_url': profile_picture_url,
    })




# Idea Submission
@login_required(login_url='signin')
def post_idea(request):
    if request.method == "POST":
        form = IdeaForm(request.POST)
        if form.is_valid():
            # Custom duplicate check in view (optional - you already do this in form)
            new_idea_name = form.cleaned_data.get('idea_name', '').strip()
            new_abstract = form.cleaned_data.get('abstract', '').strip() 
            new_description = form.cleaned_data.get('description', '').strip()

            for existing_idea in Idea.objects.all():
                name_similarity = fuzz.token_sort_ratio(new_idea_name, existing_idea.idea_name)
                desc_similarity = fuzz.token_sort_ratio(new_description, existing_idea.description)
                
                if name_similarity > 85 or desc_similarity > 80:
                    messages.error(request, "🚫 An idea with a similar name or description already exists.")
                    return redirect("post_idea")
                
                  # Payment validation
            is_paid = form.cleaned_data.get('is_paid', False)
            price = form.cleaned_data.get('price', None)

            if is_paid and (price is None or price <= 0):
                messages.error(request, "🚫 Please enter a valid price greater than 0 for a paid idea.")
                return redirect("post_idea")   

            idea = form.save(commit=False)
            idea.user = request.user
            idea.save()

            messages.success(request, "✅ Your idea has been successfully posted!")
            return redirect("post_idea")
        else:
            # 👇 Extract error message from form and send to messages
            for error in form.non_field_errors():
                messages.error(request, f"🚫 {error}")
    else:
        form = IdeaForm()

    return render(request, "post_idea.html", {"form": form})




# Idea Detail Page
@login_required(login_url='signin')
def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    has_access = False

    if request.user.is_authenticated:
        if request.user.is_organization:
            has_access = True
        else:
            access = IdeaAccess.objects.filter(user=request.user, idea=idea, has_paid=True).first()
            if access:
                has_access = True

    return render(request, "view_idea.html", {
        'idea': idea,
        'has_access': has_access,
    })


# Edit Idea
@login_required(login_url='signin')
def edit_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, user=request.user)
    if request.method == "POST":
        form = IdeaForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            return redirect('your_ideas')

    else:
        form = IdeaForm(instance=idea)
    return render(request, "edit_idea.html", {"form": form})

# Delete Idea
@login_required(login_url='signin')
def delete_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)

    # Ensure only the user who posted the idea can delete it
    if idea.user != request.user:
        return redirect('your_ideas')  # Or raise a 403

    idea.delete()
    return redirect('your_ideas')



@login_required(login_url='signin')
def idea_list(request):
    query = request.GET.get("q", "")
    filter_type = request.GET.get("filter", "trending")
    
    ideas = Idea.objects.all()
    filters_applied = False

    # Filter by category (ai/social/business)
    if filter_type in ["ai", "social", "business"]:
        ideas = ideas.filter(category__iexact=filter_type)
        filters_applied = True

    # Apply additional filters
    if filter_type == "trending":
        ideas = ideas.annotate(likes_count=Count('like')).order_by('-likes_count')
    elif filter_type == "recent":
        ideas = ideas.order_by('-created_at')
    elif filter_type == "top_week":
        week_ago = timezone.now() - timedelta(days=7)
        ideas = ideas.filter(created_at__gte=week_ago).annotate(
            likes_count=Count('like')
        ).order_by('-likes_count')

    # Search filter
    if query:
        ideas = ideas.filter(idea_name__icontains=query)

    # ✅ Ensure likes_count is annotated for all ideas
    if not hasattr(ideas, 'likes_count'):
        ideas = ideas.annotate(likes_count=Count('like'))

    # Like info
    for idea in ideas:
        idea.user_liked = idea.like_set.filter(user=request.user).exists()

    return render(request, "idea_list.html", {
        "ideas": ideas,
        "filter_type": filter_type,
        "query": query,
        "filters_applied": filters_applied,
    })



# @login_required(login_url='signin')
# def explore_ideas(request):
#     ideas = Idea.objects.all()  # or filter as needed
#     return render(request, "explore_ideas.html", {"ideas": ideas})


# @login_required(login_url='signin')
# def investors(request):
#     return render(request, "investors.html")

# def is_admin(user):
#     return user.is_authenticated and user.is_superuser

# @user_passes_test(is_admin)
# def admin_dashboard(request):
#     # Admin-specific functionality
#     return render(request, 'admin_dashboard.html')



def is_admin(user):
    return user.is_authenticated and user.is_superuser


# Admin Dashboard View
@user_passes_test(is_admin, login_url="signin")
def admin_dashboard(request):
    # Fetch counts
    total_users = User.objects.filter(is_user=True).count()
    total_organizations = User.objects.filter(is_organization=True).count()
    total_ideas = Idea.objects.count()
    total_events = PostEvent.objects.count()  # Fetch total events

    # Fetch latest entries
    latest_users = User.objects.filter(is_user=True).order_by("-date_joined")[:5]
    latest_organizations = User.objects.filter(is_organization=True).order_by("-date_joined")[:5]
    latest_ideas = Idea.objects.order_by("-created_at")[:5]
    latest_events = PostEvent.objects.order_by("-date")[:5]  # ✅ Correct field name


    context = {
        "total_users": total_users,
        "total_organizations": total_organizations,
        "total_ideas": total_ideas,
        "total_events": total_events,  # Added total events
        "latest_users": latest_users,  # Latest 5 users
        "latest_organizations": latest_organizations,  # Latest 5 organizations
        "latest_ideas": latest_ideas,  # Latest 5 ideas
        "latest_events": latest_events,  # Latest 5 events
    }
    return render(request, "admin_dashboard.html", context)

@user_passes_test(is_admin, login_url="signin")
def admin_users(request):
    users = User.objects.filter(is_user=True)
    return render(request, "admin_users.html", {"users": users})

@user_passes_test(is_admin, login_url="signin")
def admin_organizations(request):
    organizations = User.objects.filter(is_organization=True)
    return render(request, "admin_organizations.html", {"organizations": organizations})

@user_passes_test(is_admin, login_url="signin")
def admin_ideas(request):
    ideas = Idea.objects.all()
    return render(request, "admin_ideas.html", {"ideas": ideas})


@user_passes_test(is_admin, login_url="signin")
def admin_delete_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    idea.delete()
    return redirect('admin_ideas')  # Redirect to home or any other page


@user_passes_test(is_admin, login_url="signin")
def admin_delete_events(request, event_id):
    # Get the event object by ID or 404 if not found
    event = get_object_or_404(PostEvent, id=event_id)
    
    # Delete the event
    event.delete()
    
    # Redirect to the admin events page after deletion
    return redirect('admin_events')



@user_passes_test(is_admin, login_url="signin")
def admin_events(request):
    events = PostEvent.objects.all()  # Fetch all events
    return render(request, "admin_events.html", {"events": events})



@login_required(login_url='signin')
def search_ideas(request):
    query = request.GET.get('q', '')
    ideas = Idea.objects.filter(idea_name__icontains=query) if query else Idea.objects.all()
    return render(request, 'partials.html', {'ideas': ideas})





@login_required(login_url='signin')  # Ensures only logged-in users can post events
def post_event_view(request):
    if not request.user.is_organization:
        raise PermissionDenied("Only organizations can post events.")  # Restrict to organizations

    if request.method == "POST":
        form = PostEventForm(request.POST, request.FILES)  # Handle image upload
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user  # Assign current user (organization) as event creator
            event.save()
            return redirect('events')  # Redirect to events page
    else:
        form = PostEventForm()

    return render(request, "post_event.html", {"form": form})



@login_required(login_url='signin')
def events_view(request):
    # Get the search query from GET request
    query = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')
    
    # Start with base queryset
    events = PostEvent.objects.filter(user__is_organization=True).select_related('user')  # Use 'user__is_organization' for filtering
    
    # Apply search filter if query exists
    if query:
        events = events.filter(title__icontains=query)
    
    # Apply date filters
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'upcoming':
            events = events.filter(date__gte=today)
        elif date_filter == 'this_week':
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            events = events.filter(date__range=[start_week, end_week])
        elif date_filter == 'this_month':
            events = events.filter(date_month=today.month, date_year=today.year)
    
    return render(request, "events.html", {
        'events': events,
    })






@login_required(login_url='signin')
def event_details(request, event_id):
    event = get_object_or_404(PostEvent, id=event_id)  # Correct model name
    return render(request, 'event_details.html', {'event': event})



@user_passes_test(is_admin)
def admin_delete_event(request, event_id):
    event = get_object_or_404(PostEvent, id=event_id)  # <-- Corrected here!

    if request.method == 'POST':
        event.delete()
        messages.success(request, "✅ Event deleted successfully by Admin.")
        return redirect('admin_events')  # make sure this URL name exists
    else:
        messages.error(request, "🚫 Invalid request method.")
        return redirect('admin_events')



@login_required(login_url='signin')
def delete_event(request, event_id):
    event = get_object_or_404(PostEvent, id=event_id)

    if request.method == "POST":
        event.delete()
        messages.success(request, "✅ Event deleted successfully!")
    
    return redirect('your_events')  # Always redirect, don't render here



@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    # Get only normal users (non-organizations)
    normal_users = User.objects.filter(is_organization=False).order_by('-date_joined')
    return render(request, 'admin_users.html', {'users': normal_users})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User {user.username} has been deleted.')
    return redirect('admin_users')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_users')


def admin_toggle_organization_status(request, org_id):
    if request.method == 'POST':
        org = get_object_or_404(User, id=org_id, is_organization=True)
        org.is_active = not org.is_active
        org.save()
        messages.success(request, f"Organization {'activated' if org.is_active else 'deactivated'} successfully")
    return redirect('admin_organizations')



# def admin_view_user(request, user_id):
#     profile_user = get_object_or_404(User, id=user_id)
#     # Make sure to include all necessary context data
#     context = {
#         'profile_user': profile_user,
#         'follower_count': profile_user.followers.count(),
#         'following_count': profile_user.following.count(),
#         'ideas': profile_user.ideas.all(),
#         # Add other context data as needed
#     }
#     return render(request, 'user_profile.html', context)




# def organization_detail(request, id):
#     organization = get_object_or_404(OrganizationProfile, id=id)  # Ensure correct model
#     return render(request, 'organization_detail.html', {'organization': organization})

@user_passes_test(is_admin, login_url="signin")
def delete_organization(request, id):
    user = get_object_or_404(User, id=id, is_organization=True)
    if hasattr(user, "organizationprofile"):
        user.organizationprofile.delete()  # Delete the profile
    user.delete()  # Delete the user account
    return redirect('admin_organizations')




# @user_passes_test(is_admin, login_url="signin")
# def delete_user(request, id):
#     user = get_object_or_404(User, id=id)
#     user.delete()
#     messages.success(request, "User deleted successfully.")
#     return redirect('admin_users')



@login_required(login_url='signin')
def your_ideas_view(request):
    user_ideas = Idea.objects.filter(user=request.user).order_by('-created_at')  # or '-id'
    return render(request, 'your_ideas.html', {'ideas': user_ideas})


@login_required(login_url='signin')
def your_events_view(request):
    events = PostEvent.objects.filter(user=request.user)
    return render(request, 'your_events.html', {'events': events})





@login_required(login_url='signin')
def edit_event(request, event_id):
    event = get_object_or_404(PostEvent, id=event_id, user=request.user)
    if request.method == 'POST':
        form = PostEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('your_events')
    else:
        form = PostEventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form})




from django.utils.timezone import now
from datetime import timedelta
from collections import Counter


@user_passes_test(is_admin, login_url="signin")
def user_growth_view(request):
    # Total users and organizations
    total_users = User.objects.count()
    total_organizations = User.objects.filter(is_organization=True).count()

    # New users this month
    one_month_ago = now() - timedelta(days=30)
    new_users = User.objects.filter(date_joined__gte=one_month_ago).count()

    # Recent Users List
    recent_users = User.objects.order_by('-date_joined')[:5]

    # User growth over time (last 6 months)
    last_six_months = [now() - timedelta(days=30 * i) for i in range(6)][::-1]
    dates = [date.strftime('%b %Y') for date in last_six_months]
    user_counts = [User.objects.filter(date_joined__lte=date).count() for date in last_six_months]

    return render(request, 'user_growth.html', {
        'total_users': total_users,
        'new_users': new_users,
        'total_organizations': total_organizations,
        'recent_users': recent_users,
        'dates': dates,
        'user_counts': user_counts,
    })


@login_required(login_url='signin')
def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Use the correct related_name ("user_profile" instead of "userprofile")
    try:
        profile = user.user_profile
    except User.user_profile.RelatedObjectDoesNotExist:
        # Create a profile if it doesn't exist
        from myapp.models import UserProfile
        profile = UserProfile.objects.create(user=user)
    
    # Rest of your view code...
    ideas = Idea.objects.filter(user=user)
    follower_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    return render(request, "user_profile.html", {
        "viewed_user": user,
        "profile": profile,
        "ideas": ideas,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
        "viewing_own_profile": user == request.user,
    })









@login_required(login_url='signin')
def follow_user(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        Follow.objects.get_or_create(follower=request.user, following=profile_user)  # Change 'following_user' to 'following'
    return redirect('view_profile', username=username)

@login_required(login_url='signin')
def unfollow_user(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        Follow.objects.filter(follower=request.user, following=profile_user).delete()  # Change 'following_user' to 'following'
    return redirect('view_profile', username=username)




@login_required(login_url='signin')
def view_followers(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Get all followers of the profile_user
    followers = Follow.objects.filter(following=profile_user).select_related('follower')

    return render(request, 'followers_list.html', {
        'profile_user': profile_user,
        'followers': followers
    })



@login_required(login_url='signin')
def view_following(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Get all users the profile_user is following
    following = Follow.objects.filter(follower=profile_user).select_related('following')

    return render(request, 'following_list.html', {
        'profile_user': profile_user,
        'following': following
    })


@login_required
def initiate_payment(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)

    if not idea.is_paid:
        return redirect('view_idea', idea_id=idea_id)

    # Check if user already paid
    if IdeaAccess.objects.filter(user=request.user, idea=idea, has_paid=True).exists():
        return redirect('view_idea', idea_id=idea_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    DATA = {
        "amount": int(idea.price * 100),  # Razorpay uses paise
        "currency": "INR",
        "receipt": f"receipt_{request.user.id}_{idea.id}",
        "payment_capture": 1,
    }

    order = client.order.create(data=DATA)

    # Save access request with order ID
    IdeaAccess.objects.update_or_create(
        user=request.user,
        idea=idea,
        defaults={'razorpay_order_id': order['id']}
    )

    return render(request, "payment.html", {
        "idea": idea,
        "order": order,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "user": request.user
    })


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST

        try:
            access = IdeaAccess.objects.get(razorpay_order_id=data['razorpay_order_id'])
            access.razorpay_payment_id = data['razorpay_payment_id']
            access.razorpay_signature = data['razorpay_signature']
            access.has_paid = True
            access.save()
            return redirect('idea_detail', idea_id=access.idea.id)
        except IdeaAccess.DoesNotExist:
            return HttpResponse("Invalid payment", status=400)

    return HttpResponse("Invalid request", status=400)


@login_required
def view_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)

    if idea.is_paid:
        paid_access = IdeaAccess.objects.filter(user=request.user, idea=idea, has_paid=True).exists()
        if not paid_access:
            return redirect('initiate_payment', idea_id=idea_id)

    return render(request, 'view_idea.html', {'idea': idea})



@login_required(login_url='signin')
def like_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    like, created = Like.objects.get_or_create(user=request.user, idea=idea)

    if not created:
        # Already liked → unlike
        like.delete()

    return redirect('idea_list')


@login_required(login_url='signin')
def unlike_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    Like.objects.filter(user=request.user, idea=idea).delete()
    return redirect('idea_list')





@login_required(login_url='signin')
def comment_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    comments = Comment.objects.filter(idea=idea).order_by('-created_at')

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.idea = idea
            comment.user = request.user
            comment.save()
            
            # Create notification for the idea owner if it's not their own comment
            if request.user != idea.user:
                Notification.objects.create(
                    recipient=idea.user,
                    sender=request.user,
                    notification_type='comment_idea',
                    idea=idea,
                    is_read=False
                )
            
            return redirect('comment_idea', idea_id=idea.id)
    else:
        form = CommentForm()

    return render(request, 'comment_idea.html', {
        'idea': idea,
        'form': form,
        'comments': comments
    })




def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You are not allowed to delete this comment.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def edit_comment(request, comment_id):
    # Get the comment object
    comment = get_object_or_404(Comment, id=comment_id)

    # Ensure that the user is the one who created the comment
    if request.user == comment.user:
        if request.method == "POST":
            content = request.POST.get('content')
            comment.content = content
            comment.save()  # Save the updated content
            return redirect('comment_idea', idea_id=comment.idea.id)  # Redirect to the idea detail page

    return redirect('comment_idea', idea_id=comment.idea.id)



# @login_required(login_url='signin')
# def react_to_comment(request, comment_id):
#     comment = get_object_or_404(Comment, id=comment_id)
#     is_like = request.POST.get('is_like') == 'true'

#     reaction, created = CommentReaction.objects.get_or_create(
#         comment=comment,
#         user=request.user,
#         defaults={'is_like': is_like}
#     )

#     if not created:
#         if reaction.is_like == is_like:
#             # Toggle off
#             reaction.delete()
#         else:
#             # Update the reaction
#             reaction.is_like = is_like
#             reaction.save()

#     return redirect('comment_idea', idea_id=comment.idea.id)




@login_required(login_url='signin')
def report_idea(request, idea_id):
    idea = Idea.objects.get(id=idea_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.idea = idea
            report.save()
            return redirect('idea_list')
    else:
        form = ReportForm()

    return render(request, 'report_idea.html', {'form': form, 'idea': idea})



  # Make sure Report (not ReportForm) is imported

def admin_reports(request):
    # Fetch all the reports
    reports = Report.objects.all()

    # Fetch totals
    total_ideas = Idea.objects.count()
    total_events = PostEvent.objects.count()

    context = {
        'reports': reports,
        'total_ideas': total_ideas,
        'total_events': total_events,
    }

    return render(request, 'admin_reports.html', context)





def about_us(request):
    return render(request, 'about_us.html')




def add_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User or Organization added successfully!')
            return redirect('home')  # or wherever you want to redirect after successful creation
    else:
        form = SignUpForm()
    
    return render(request, 'add_user.html', {'form': form})




def send_announcement_view(request):
    # Your logic for sending an announcement
    return render(request, 'send_announcement.html')


def rate_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    
    # Check if the user has already rated the idea
    rating, created = Rating.objects.get_or_create(idea=idea, user=request.user)

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()  # Save the updated rating
            return redirect('idea_detail', idea_id=idea.id)
    else:
        form = RatingForm(instance=rating)  # Pre-fill the form with the existing rating if any

    return render(request, 'rate_idea.html', {'idea': idea, 'form': form})



def privacy_policy(request):
    return render(request, 'privacy_policy.html')



def terms_conditions(request):
    return render(request, 'terms_conditions.html')



@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    # Mark as read
    notifications.filter(is_read=False).update(is_read=True)

    context = {}

    if request.user.is_user:
        # Normal users: only show comment, like, and follow notifications
        context['comment_notifications'] = notifications.filter(
            notification_type='comment_idea'
        ).select_related('sender', 'idea')

        # Optional: you can also include likes and follows if needed
        context['like_notifications'] = notifications.filter(
            notification_type='like_idea'
        ).select_related('sender', 'idea')

        context['follow_notifications'] = notifications.filter(
            notification_type='new_follower'
        ).select_related('sender')

    elif request.user.is_organization:
        # Organizations: only show event-related notifications
        context['event_notifications'] = notifications.filter(
            Q(notification_type='event_interest') | 
            Q(notification_type='event_comment')
        ).select_related('sender', 'event')

    return render(request, 'notifications.html', context)