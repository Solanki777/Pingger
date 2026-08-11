from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=150,required=True)

    email = forms.EmailField(required=True)

    profession = forms.CharField(required=True,max_length=150)

    company = forms.CharField(
        max_length=150,
        required=False
    )

    class Meta:
        model = User
        fields = [
            "name",
            "email",
            "profession",
            "company",
            "password1",
            "password2",
                  ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with the same email is already exists."
            )

        return email
