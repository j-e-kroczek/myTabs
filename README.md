# myTabs
Simple money management django project.

![User Chart View](__screenshots/UserChart.png?raw=true "Title")
![Tab Details View](__screenshots/TabDetails.png?raw=true "Title")
![Reimbursement View](__screenshots/Reimbursement.png?raw=true "Title")


# Getting Started

First clone the repository from Github and switch to the new directory:

    $ git clone git@github.com/j-e-kroczek/myTabs.git
    
Create .env file:

    AllOWED_HOSTS={your allowed hosts}
    DJANGO_SECRET={your django secret}

Activate the virtualenv for your project.
    
Install project dependencies:

    $ pip install -r requirements.txt

Go to project folder:

    $ cd myTabs
    
Then simply apply the migrations:

    $ python manage.py migrate
    
Create super user:

    $ python manage.py createsuperuser

Optionally generate fake data(Before create couple Expenses types in admin page!)

    $ python dummy_data_gen.py

You can now run the development server:

    $ python manage.py runserver
