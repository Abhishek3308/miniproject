from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, UserProfile, OrganizationProfile, Idea ,PostEvent ,Follow ,Like, Comment ,Report,Rating
from rapidfuzz import fuzz
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    user_type = forms.ChoiceField(
        choices=[("user", "Ideator"), ("organization", "Organization")],
        required=True,
        label="Sign Up As"
    )
    company_name = forms.CharField(required=False)
    job_title = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'company_name', 'job_title')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        allowed_domains = ['@gmail.com']  # Only these domains are allowed
        
        if not any(email.endswith(domain) for domain in allowed_domains):
            raise ValidationError("Only emails ending with @gamil.com is allowed.")
        
        return email

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")

        if user_type == "organization":
            if not cleaned_data.get("company_name") or not cleaned_data.get("job_title"):
                raise forms.ValidationError("Company Name and Job Title are required for organizations.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_user = self.cleaned_data["user_type"] == "user"
        user.is_organization = self.cleaned_data["user_type"] == "organization"
        
        if commit:
            user.save()

            if user.is_organization:
                OrganizationProfile.objects.create(
                    user=user,
                    company_name=self.cleaned_data["company_name"],
                    job_title=self.cleaned_data["job_title"]
                )

        return user

class SignInForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


User = get_user_model()

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "w-3/4 px-3 py-1.5 border rounded-md text-sm",
            "placeholder": "Enter your username"
        })
    )

    class Meta:
        model = UserProfile
        fields = ["username", "profession", "expertise", "bio", "profile_picture"]
        widgets = {
            "profession": forms.TextInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "placeholder": "Enter your profession"}),
            "expertise": forms.TextInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "placeholder": "Your expertise areas"}),
            "bio": forms.Textarea(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "rows": 3, "placeholder": "Tell us about yourself..."}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm"}),
        }

    def _init_(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileForm, self)._init_(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username

    def save(self, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        if self.user:
            self.user.username = self.cleaned_data['username']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile

    
    
# Organization Profile Form
class OrganizationProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizationProfile
        fields = ['company_name','description','job_title', 'profile_picture']


# Idea Submission Form
class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = [
            "idea_name",
            "abstract",  # Added missing comma
            "category", 
            "funding_goal", 
            "estimated_investment", 
            "collaboration", 
            "status",  # Added missing comma
            "description",
            "is_paid",
            "price",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe your idea..."}),
            "status": forms.Select(choices=Idea._meta.get_field("status").choices),
        }

    def clean(self):
        cleaned_data = super().clean()
        idea_name = cleaned_data.get("idea_name")
        description = cleaned_data.get("description")
        is_paid = cleaned_data.get("is_paid")
        price = cleaned_data.get("price")

        if not idea_name or not description:
            return cleaned_data  # Let Django handle the required field errors
        
        if is_paid:
            if price is None:
                raise forms.ValidationError("Please set a price for this paid idea.")
            if price <= 0:
                raise forms.ValidationError("Price must be greater than 0 for paid ideas.")

        # Get all existing ideas except the current one if editing
        existing_ideas = Idea.objects.exclude(pk=self.instance.pk)

        for idea in existing_ideas:
            name_similarity = fuzz.ratio(idea_name.lower(), idea.idea_name.lower())
            desc_similarity = fuzz.ratio(description.lower(), idea.description.lower())

            # You can adjust the threshold (e.g., 85 for name, 90 for description)
            if name_similarity > 85 or desc_similarity > 90:
                raise forms.ValidationError(
                    "Your idea seems too similar to an existing one. Please try to make it more unique."
                )

        return cleaned_data



class PostEventForm(forms.ModelForm):
    class Meta:
        model = PostEvent
        fields = ["title", "description", "date", "location", "image"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ['following','follower']

    def _init_(self, *args, **kwargs):
        super(FollowForm, self)._init_(*args, **kwargs)


class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = []

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment...'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the reason for reporting...'}),
        }



class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']  # Only the score field is required for the rating form

    score = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],  # Ratings from 1 to 5
        widget=forms.Select(attrs={'class': 'form-select'}),  # Add your custom styles or classes
        required=True
    )


class NotificationSettingsForm(forms.Form):
    EVENT_NOTIFICATIONS = [
        ('all', 'All event notifications'),
        ('followed_only', 'Only from organizations I follow'),
        ('none', 'No event notifications'),
    ]
    
    INTERACTION_NOTIFICATIONS = [
        ('all', 'All interactions (likes, comments, follows)'),
        ('none', 'No interaction notifications'),
    ]
    
    event_notifications = forms.ChoiceField(
        choices=EVENT_NOTIFICATIONS,
        widget=forms.RadioSelect,
        initial='followed_only'
    )
    
    interaction_notifications = forms.ChoiceField(
        choices=INTERACTION_NOTIFICATIONS,
        widget=forms.RadioSelect,
        initial='all'
    )
    
    email_notifications = forms.BooleanField(
        required=False,
        initial=True,
        label='Receive email notifications'
    )


# class CommentReactionForm(forms.ModelForm):
#     class Meta:
#         model = CommentReaction
#         fields = ['is_like']
#         widgets = {
#             'is_like': forms.HiddenInput()  # Hide the field and use the view/button to set value
#         }