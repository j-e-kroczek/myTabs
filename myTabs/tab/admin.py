from django.contrib import admin
from .models import Tab, Belonging, ExpenseType, Expense, Associating
from user.models import Profile
# Register your models here.
admin.site.register(Tab)
admin.site.register(Belonging)
admin.site.register(ExpenseType)
admin.site.register(Expense)
admin.site.register(Associating)
admin.site.register(Profile)