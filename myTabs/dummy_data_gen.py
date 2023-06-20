import os 
from tqdm import trange, tqdm
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myTabs.settings")

import django 
django.setup() 

from faker import Faker
import faker_commerce
import random
from datetime import date
from tab.models import Tab, Expense, User, Associating, Belonging, ExpenseType
from model_bakery import baker
    
def generate_expences(tab_id:int, how_many:int=10):
    fake = Faker(['pl_PL'])
    fake.add_provider(faker_commerce.Provider)
    tab = Tab.objects.get(id=tab_id)
    expense_types = ExpenseType.objects.filter(is_private=False)
    users = []
    for user in Belonging.objects.filter(tab=tab, is_active=True):
        users.append(user.user)
    for _ in trange(0, how_many, desc="Generating expences"):
        user = random.choice(users)
        name = fake.ecommerce_name()
        amount = random.randint(1, 1000)
        date = fake.date_between(start_date='-3y', end_date='today')
        expense = baker.make(Expense, tab=tab, buyer=user, name=name, cost=amount, date=date, type=random.choice(expense_types))
        current_amount = amount
        for user in random.sample(list(users), random.randint(1, len(users))):
            if current_amount>0 and not Associating.objects.filter(expense=expense, user=user).exists():
                cost = random.randint(1, current_amount)
                baker.make(Associating, expense=expense, user=user, cost=cost)
                current_amount -= cost
    print("Done.")

def start_script():
    try:
        input("This script will create fake data. Press ENTER to continue...")
        x = input("Are you sure you want to continue? (y/n): ")
        if x == 'y':
            tab_id = int(input("Enter tab id: "))
            how_many = int(input("How many expences do you want to add? "))
        if not Tab.objects.filter(id=tab_id).exists():
            print("Tab with given id does not exist.")
            return
        if how_many < 1:
            print("Number of expences must be positive.")
            return
        generate_expences(tab_id, how_many)
    except KeyboardInterrupt:
        print("\nAborted.")
        
if __name__ == "__main__":
    start_script()