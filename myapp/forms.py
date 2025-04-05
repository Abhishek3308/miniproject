from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile, OrganizationProfile, Idea ,PostEvent

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

            # If an organization, create an OrganizationProfile
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


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profession", "expertise", "bio", "resume", "profile_picture", "linkedin", "portfolio_website"]
        widgets = {
            "profession": forms.TextInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "placeholder": "Enter your profession"}),
            "expertise": forms.TextInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "placeholder": "Your expertise areas"}),
            "bio": forms.Textarea(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "rows": 3, "placeholder": "Tell us about yourself..."}),
            "resume": forms.ClearableFileInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm"}),
            "linkedin": forms.URLInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "placeholder": "LinkedIn Profile URL"}),
            "portfolio_website": forms.URLInput(attrs={"class": "w-3/4 px-3 py-1.5 border rounded-md text-sm", "placeholder": "Your portfolio website"}),
        }

# Organization Profile Form
class OrganizationProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizationProfile
        fields = ["company_name", "job_title", "industry", "location", "website", "linkedin","profile_picture"]

# Idea Submission Form
class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ["idea_name", "description", "category", "funding_goal", "estimated_investment", "collaboration", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe your idea..."}),
            "status": forms.Select(choices=Idea._meta.get_field("status").choices),
        }


class PostEventForm(forms.ModelForm):
    class Meta:
        model = PostEvent
        fields = ["title", "description", "date", "location", "image"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }