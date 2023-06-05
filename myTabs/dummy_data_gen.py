import random
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tab.models import Tab, Belonging, ExpenseType, Expense, Associating


# Tworzenie 4 użytkowników
users = []
for user in User.objects.all():
    users.append(user)

# Tworzenie tablic
tabs = []
for i in range(4):
    tab = Tab.objects.create(name=f'Tab{i+1}')
    tabs.append(tab)

# Dołączanie użytkowników do tablic
for user, tab in zip(users, tabs):
    Belonging.objects.create(user=user, tab=tab)

# Tworzenie typów wydatków
expense_types = []
for i in range(10):
    expense_type = ExpenseType.objects.create(name=f'Expense Type {i+1}', tab=tabs[i % 4])
    expense_types.append(expense_type)

# Tworzenie i przypisywanie wydatków
for i in range(10):
    tab = tabs[i % 4]
    buyer = users[i % 4]
    expense_type = expense_types[i]
    expense = Expense.objects.create(tab=tab, buyer=buyer, type=expense_type, name=f'Expense {i+1}', cost=random.randint(50, 200))
    
    # Tworzenie powiązań użytkowników z wydatkiem
    for user in users:
        if user == buyer:
            cost = expense.cost
        else:
            cost = expense.cost // 4
        Associating.objects.create(user=user, expense=expense, cost=cost)
    
    # Aktualizacja daty na 10 kolejnych dni wstecz
    expense.date = timezone.now() - timedelta(days=10-i)
    expense.save()

print("Tablice i wydatki zostały utworzone.")