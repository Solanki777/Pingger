from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):

    name = forms.CharField(
        max_length=150,
        required=True
    )

    email = forms.EmailField(
        required=True
    )

    profession = forms.CharField(
        max_length=100,
        required=True
    )

    company = forms.CharField(
        max_length=150,
        required=False
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True
    )

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data