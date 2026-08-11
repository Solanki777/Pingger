from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.models import User
from .models import Profile


def register(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            profession = form.cleaned_data["profession"]
            company = form.cleaned_data["company"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )

            Profile.objects.create(
                user=user,
                profession=profession,
                company=company
            )

            return redirect("login")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )