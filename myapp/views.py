from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages,admin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import User, UserProfile, OrganizationProfile, Idea ,PostEvent ,Follow 
from .forms import SignUpForm, SignInForm, UserProfileForm, OrganizationProfileForm, IdeaForm ,PostEventForm ,Follow
from django.urls import path
from django.template.response import TemplateResponse
from rapidfuzz import fuzz


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
            return redirect("signin")  # Redirect to sign-in page after signup
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field.capitalize()}: {error}")

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
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Handle form submission
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile")
    else:
        form = UserProfileForm(instance=profile)

    # ✅ Get follower/following counts
    follower_count = Follow.objects.filter(following=request.user).count()
    following_count = Follow.objects.filter(follower=request.user).count()

    # ✅ Get user's ideas
    ideas = Idea.objects.filter(user=request.user)  # or use creator=request.user if that’s the field

    return render(request, "user_profile.html", {
        "form": form,
        "follower_count": follower_count,
        "following_count": following_count,
        "ideas": ideas,
    })


@login_required(login_url='signin') 
def edit_userprofile(request):
    # Get or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # Replace with your desired redirect after saving
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'edit_profile.html', {'form': form})



# Organization Profile (View & Update)
@login_required(login_url='signin')
def organization_profile(request):
    org_profile, created = OrganizationProfile.objects.get_or_create(user=request.user)

    # Ensure `profile_picture` has a valid URL or use a default
    profile_pic_url = org_profile.profile_picture.url if org_profile.profile_picture else "/static/images/org-placeholder.png"

    if request.method == "POST":
        form = OrganizationProfileForm(request.POST, request.FILES, instance=org_profile)
        if form.is_valid():
            form.save()
            return redirect("organization_profile")
    else:
        form = OrganizationProfileForm(instance=org_profile)

    return render(request, "organization_profile.html", {
        "form": form,
        "organization_profile": org_profile,  # Ensure this is passed to template
        "profile_pic_url": profile_pic_url,
    })


@login_required
def edit_organization_profile(request):
    profile = request.user.organization_profile

    if request.method == 'POST':
        profile.company_name = request.POST.get('name', '')
        profile.description = request.POST.get('description', '')
        
        # Save uploaded image if available
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        return redirect('organization_profile')

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
            new_description = form.cleaned_data.get('description', '').strip()

            for existing_idea in Idea.objects.all():
                name_similarity = fuzz.token_sort_ratio(new_idea_name, existing_idea.idea_name)
                desc_similarity = fuzz.token_sort_ratio(new_description, existing_idea.description)
                
                if name_similarity > 85 or desc_similarity > 80:
                    messages.error(request, "🚫 An idea with a similar name or description already exists.")
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
    return render(request, "idea_detail.html", {"idea": idea})

# Edit Idea
@login_required(login_url='signin')
def edit_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, user=request.user)
    if request.method == "POST":
        form = IdeaForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            return redirect("idea_detail", idea_id=idea.id)
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
    query = request.GET.get("q", "")  # Get search query from the request
    if query:
        ideas = Idea.objects.filter(idea_name__icontains=query)  # Filter by idea_name
    else:
        ideas = Idea.objects.all()  # Show all ideas if no search query

    return render(request, 'idea_list.html', {'ideas': ideas, 'query': query})

# @login_required(login_url='signin')
# def explore_ideas(request):
#     ideas = Idea.objects.all()  # or filter as needed
#     return render(request, "explore_ideas.html", {"ideas": ideas})


@login_required(login_url='signin')
def investors(request):
    return render(request, "investors.html")

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
def admin_events(request):
    events = PostEvent.objects.all()  # Fetch all events
    return render(request, "admin_events.html", {"events": events})



@login_required(login_url='signin')
def search_ideas(request):
    query = request.GET.get('q', '')
    ideas = Idea.objects.filter(idea_name__icontains=query) if query else Idea.objects.all()
    return render(request, 'partials.html', {'ideas': ideas})




def notifications_view(request):
    return render(request, 'notifications.html')


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
    events = PostEvent.objects.filter(user__is_organization=True)  # Fetch only organization-posted events
    return render(request, "events.html", {"events": events})



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








# def organization_detail(request, id):
#     organization = get_object_or_404(OrganizationProfile, id=id)  # Ensure correct model
#     return render(request, 'organization_detail.html', {'organization': organization})

@user_passes_test(is_admin, login_url="signin")
def delete_organization(request, id):
    organization = get_object_or_404(OrganizationProfile, id=id)
    organization.delete()
    return redirect('admin_organizations')



@user_passes_test(is_admin, login_url="signin")
def delete_user(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_users')



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
    profile_user = get_object_or_404(User, username=username)
    
    # Check if the logged-in user is following the profile
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    # Get all ideas posted by the user
    ideas = Idea.objects.filter(user=profile_user)

    # Count the followers and following
    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    return render(request, 'profile_detail.html', {
        'profile_user': profile_user,
        'is_following': is_following,
        'ideas': ideas,
        'follower_count': follower_count,
        'following_count': following_count,
    })





@login_required(login_url='signin')
def follow_user(request, username):
    profile_user = get_object_or_404(User, username=username)
    # Follow the user if not already following
    if request.user != profile_user:
        Follow.objects.get_or_create(follower=request.user, following=profile_user)
    return redirect('view_profile', username=username)


@login_required(login_url='signin')
def unfollow_user(request, username):
    profile_user = get_object_or_404(User, username=username)
    # Unfollow the user
    if request.user != profile_user:
        Follow.objects.filter(follower=request.user, following=profile_user).delete()
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
