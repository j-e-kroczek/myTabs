from django.shortcuts import  render, redirect, get_object_or_404
from .forms import NewUserForm, NewProfileForm, EditProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required
from user.models import Profile

def register_view(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("/")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register.html", context={"register_form":form}) 

def login_view(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_view(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("/")

@login_required(login_url='/login')
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        print(request.POST)
        profile_form = EditProfileForm(request.POST, instance=user)
        password_form = SetPasswordForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, "Your password has been changed")
            return redirect('/login')
        elif profile_form.is_valid():
            print(profile_form.cleaned_data)
            request.user.username = profile_form.cleaned_data['username']
            request.user.email = profile_form.cleaned_data['email']
            request.user.save()
            profile = get_object_or_404(Profile, user=user)
            profile.phone_number = profile_form.cleaned_data['phone_number']
            profile.save()
            messages.success(request, "Your profile data has been changed")
            return redirect('/profile')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = SetPasswordForm(user)
    return render(request, template_name="profile.html", context={"form":form})