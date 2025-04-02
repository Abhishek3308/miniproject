from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import User, UserProfile, OrganizationProfile, Idea 
from .forms import SignUpForm, SignInForm, UserProfileForm, OrganizationProfileForm, IdeaForm

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
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "user_profile.html", {"form": form})

def edit_userprofile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile)

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


def edit_organization_profile(request):
    organization = request.user.organization_profile  # Ensure the user is an org
    
    if request.method == "POST":
        form = OrganizationProfileForm(request.POST, request.FILES, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('organization_profile')
    else:
        form = OrganizationProfileForm(instance=organization)

    # Avoid profile_picture.url error
    profile_picture_url = organization.profile_picture.url if organization.profile_picture else None

    return render(request, 'edit_organization_profile.html', {
        'form': form,
        'profile_picture_url': profile_picture_url,
    })


# Idea Submission
@login_required(login_url='signin')
def post_idea(request):
    if request.method == "POST":
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.user = request.user
            idea.save()
            return redirect("post_idea")
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
    idea = get_object_or_404(Idea, id=idea_id, user=request.user)
    if request.method == "POST":
        idea.delete()
        return redirect("home")
    return render(request, "delete_idea.html", {"idea": idea})

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

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Admin-specific functionality
    return render(request, 'admin_dashboard.html')



def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Admin Dashboard View
@user_passes_test(is_admin, login_url="signin")
def admin_dashboard(request):
    total_users = User.objects.filter(is_user=True).count()
    total_organizations = User.objects.filter(is_organization=True).count()
    total_ideas = Idea.objects.count()

    context = {
        "total_users": total_users,
        "total_organizations": total_organizations,
        "total_ideas": total_ideas,
    }
    return render(request, "admin_dashboard.html", context)


@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.filter(is_user=True)
    return render(request, "admin_users.html", {"users": users})

@user_passes_test(is_admin)
def admin_organizations(request):
    organizations = User.objects.filter(is_organization=True)
    return render(request, "admin_organizations.html", {"organizations": organizations})

@user_passes_test(is_admin)
def admin_ideas(request):
    ideas = Idea.objects.all()
    return render(request, "admin_ideas.html", {"ideas": ideas})

def delete_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)  # This prevents 404 errors
    idea.delete()
    return redirect('admin_dashboard')  # Redirect to home or any other page



def search_ideas(request):
    query = request.GET.get('q', '')
    ideas = Idea.objects.filter(idea_name__icontains=query) if query else Idea.objects.all()
    return render(request, 'partials.html', {'ideas': ideas})


def notifications_view(request):
    return render(request, 'notifications.html')