from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tab.models import Tab, Belonging, Expense


class NewExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["name", "buyer", "type", "cost", "date"]


class NewTabForm(forms.ModelForm):
    class Meta:
        model = Tab
        fields = ["name", "description"]


class NewBelongingForm(forms.ModelForm):
    class Meta:
        model = Belonging
        fields = ["user", "tab"]
