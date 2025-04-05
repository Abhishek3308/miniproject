from django.contrib.auth.models import AbstractUser,Group,Permission
from django.db import models





class User(AbstractUser):
    is_user = models.BooleanField(default=False)
    is_organization = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    profession = models.CharField(max_length=255, blank=True, null=True)  # Example: Entrepreneur, Developer
    expertise = models.CharField(max_length=255, blank=True, null=True)  # Example: AI, Marketing, FinTech
    bio = models.TextField(blank=True, null=True)  # Short user description
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio_website = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.profession or 'Ideator'}"

class OrganizationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organization_profile")
    company_name = models.CharField(max_length=255, unique=True)
    job_title = models.CharField(max_length=255)  # Role of the user in the company
    industry = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="organization_profiles/", blank=True, null=True)

    class Meta:
        verbose_name = "Organization_Profile"
        verbose_name_plural = "Organization_Profiles"

    def __str__(self):
        return self.company_name
    
class Idea(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ideas")
    idea_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  
    category = models.CharField(max_length=100, blank=True, null=True)  # Example: Tech, Health, AI
    funding_goal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_investment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    collaboration = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[("open", "Open for Investment"), ("progress", "In Progress"), ("completed", "Completed")],
        default="open"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when idea is posted
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when idea is modified

    class Meta:
        verbose_name = "Idea"
        verbose_name_plural = "Ideas"
        ordering = ["-created_at"]  # Show newest ideas first

    def __str__(self):
        return f"{self.idea_name} - {self.user.username}"
    

class PostEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)  # ✅ Add this field

    def __str__(self):
        return f"{self.title} by {self.user.username}"



