from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewUserForm, NewProfileForm, EditProfileForm

from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required
from user.models import Profile


def register_view(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already logged in.")
        return redirect("/")
    if request.method == "POST":
        user_form = NewUserForm(request.POST)
        profile_form = NewProfileForm(request.POST)
        print(request.POST.get("phone_number"))
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, profile.user)
            messages.success(request, "Registration successful.")
            return redirect("/")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    user_form = NewUserForm()
    profile_form = NewProfileForm()
    return render(
        request=request,
        template_name="register.html",
        context={"user_form": user_form, "profile_form": profile_form},
    )


def login_view(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already logged in.")
        return redirect("/")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("/")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(
        request=request, template_name="login.html", context={"login_form": form}
    )


def logout_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You are not logged in.")
    else:
        logout(request)
        messages.info(request, "You have successfully logged out.")
    return redirect("/login/")


@login_required(login_url="/login")
def profile_view(request):
    user = request.user
    if request.method == "POST":
        profile_form = EditProfileForm(request.POST, instance=user)
        password_form = SetPasswordForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, "Your password has been changed")
            return redirect("/login")
        elif profile_form.is_valid():
            request.user.username = profile_form.cleaned_data["username"]
            request.user.email = profile_form.cleaned_data["email"]
            request.user.save()
            profile = get_object_or_404(Profile, user=user)
            profile.phone_number = profile_form.cleaned_data["phone_number"]
            profile.save()
            messages.success(request, "Your profile data has been changed")
            return redirect("/profile")
        else:
            for error in list(profile_form.errors.values()):
                messages.error(request, error)

            for error in list(password_form.errors.values()):
                messages.error(request, error)
    form = SetPasswordForm(user)
    return render(request, template_name="profile.html", context={"form": form})
