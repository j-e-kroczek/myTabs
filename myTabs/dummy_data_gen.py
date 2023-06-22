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
from user.models import Profile
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
    
def generate_users(how_many:int=10):
    faker=Faker(['pl_PL'])
    for _ in trange(0, how_many, desc="Generating users"):
        user = baker.make(User, username=faker.user_name(), password=faker.password(), email=faker.email())
        profile = baker.make(Profile, user=user, phone_number=faker.phone_number())
        user.set_password("Krowa123!")
        user.save()
    print("Done.")
    print("Users:")
    for user in User.objects.all():
        print(user.username)
        
def generate_tabs(how_many:int=10, gen_expences:bool=False):
    faker=Faker(['pl_PL'])
    names = ['Wycieczka do Paryża', 'Safari w Afryce', 'Wspinaczka górska', 'Podróż dookoła świata', 'Nurkowanie na Wyspach Galapagos', 'Spacer po Wielkim Kanionie', 'Kajakowanie na rzece Amazonce', 'Wycieczka po Włoszech', 'Relaks na balijskiej plaży', 'Wycieczka po Pir...rth', 'Podróż po Japonii', 'Wspinaczka na Mount Everest', 'Zwiedzanie Machu Picchu', 'Safari w Kenii', 'Podróż statkiem po Alasce', 'Nurkowanie na Wielkiej Rafie Koralowej', 'Wycieczka po Australii', 'Podróż do Tajlandii', 'Wyprawa na biegun południowy', 'Trekking w Himalajach', 'Wakacje na Hawajach', 'Zwiedzanie Starożytnego Egiptu', 'Podróż do Islandii', 'Safari w Tanzanii', 'Wycieczka do Barcelony', 'Żeglarski rejs po Morzu Śródziemnym', 'Spacer po Wielkim Murze Chińskim']
    for _ in trange(0, how_many, desc="Generating tabs"):
        tab = baker.make(Tab, name=random.choice(names), description=faker.text())
        for user in random.sample(list(User.objects.all().exclude(username='root')), random.randint(2, 7)):
            baker.make(Belonging, tab=tab, user=user)
        if gen_expences:
            generate_expences(tab.id, random.randint(1, 20))
            

def start_script():
    try:
        input("This script will create fake data. Press ENTER to continue...")
        x = input("Are you sure you want to continue? (y/n): ")
        if x == 'y':
            choice = int(input("What do you want to generate?\n1. Users\n2. Tabs\n3. Expences\n4. All\n"))
            if choice == 1:
                how_many = int(input("How many users do you want to add? "))
                if how_many < 1:
                    print("Number of users must be positive.")
                    return
                generate_users(how_many)
            elif choice == 2:
                how_many = int(input("How many tabs do you want to add? "))
                if how_many < 1:
                    print("Number of tabs must be positive.")
                    return
                if input("Do you want to generate expences for tabs? (y/n): ") == 'y':
                    generate_tabs(how_many, True)
                else:
                    generate_tabs(how_many)
            elif choice == 3:
                tab_id = int(input("Enter tab id: "))
                how_many = int(input("How many expences do you want to add? "))
                if not Tab.objects.filter(id=tab_id).exists():
                    print("Tab with given id does not exist.")
                    return
                if how_many < 1:
                    print("Number of expences must be positive.")
                    return
                generate_expences(tab_id, how_many)
            elif choice == 4:
                how_many = int(input("How many users do you want to add? "))
                if how_many < 1:
                    print("Number of users must be positive.")
                    return
                generate_users(how_many)
                how_many = int(input("How many tabs do you want to add? "))
                if how_many < 1:
                    print("Number of tabs must be positive.")
                    return
                if input("Do you want to generate expences for tabs? (y/n): ") == 'y':
                    generate_tabs(how_many, True)
                else:
                    generate_tabs(how_many)
    except KeyboardInterrupt:
        print("\nAborted.")
        
if __name__ == "__main__":
    start_script()