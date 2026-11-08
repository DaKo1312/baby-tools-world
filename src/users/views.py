# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


# Create your views here.
def user_register(request):
    """This function handles user registrations and will delegate the user to the login page."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request,'welcome to the baby tool world')
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def user_login(request):
    """This function handles user logins and will delegate the user to the home page."""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("/")
                else:
                    messages.info(request, "User is not active")
            else:
                messages.info(request, "Something went wrong, maybe check your provided credentials or try again.")
    else:
        form = LoginForm()

    return render(
        request,
        "login.html",
        # the template context dict
        {"form": form},
    )


def user_logout(request):
    """This function handles user logouts and will delegate the user to the home page."""
    logout(request)
    return redirect("/")
