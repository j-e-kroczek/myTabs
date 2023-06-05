from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, CheckConstraint
from datetime import datetime


class Tab(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.id}"


class Belonging(models.Model):
    class Meta:
        unique_together = (("user", "tab"),)

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tab}"


class ExpenseType(models.Model):
    class Meta:
        constraints = [
            CheckConstraint(
                check=(
                    Q(is_private=False) & Q(tab__isnull=True)
                    | (Q(is_private=True) & Q(tab__isnull=False))
                ),
                name="is_private_no_tab",
            )
        ]
        unique_together = ("name", "tab")

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_private = models.BooleanField(default=True)
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.id} - {self.tab}"


class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    type = models.ForeignKey(ExpenseType, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(default=datetime.today(), editable=True)

    def __str__(self):
        return f"{self.name} - {self.id}"


class Associating(models.Model):
    class Meta:
        unique_together = ("user", "expense")

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.expense} - {self.user} - {self.id} ({self.cost})"
