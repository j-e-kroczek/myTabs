from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user
        
class NewProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['phone_number']
  
class EditProfileForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'email']
	phone_number = forms.CharField(max_length=15, required=False)
