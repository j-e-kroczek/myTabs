from tab.models import Belonging, Expense, ExpenseType
from tab.models import Tab, Associating, Belonging
from django.db.models import Q
import json
import itertools
from typing import List, Tuple, Dict
import datetime
from django.contrib.auth.models import User


def convert_list_of_users_to_json(tab_users: List[User]):
    users_data = []

    for user in tab_users:
        user_data = {
            "id": user.id,
            "username": user.username,
        }
        users_data.append(user_data)
    return json.dumps(users_data)


def get_user_tabs(user: User):
    user_tabs = []
    for belonging in Belonging.objects.filter(user=user, is_active=True):
        user_tabs.append(belonging.tab)
    return user_tabs


def get_tab_users(tab:Tab, active:bool=False):
    tab_users = []
    for belonging in Belonging.objects.filter(tab=tab):
        if active and belonging.is_active:
            tab_users.append(belonging.user)
        elif not active:
            tab_users.append(belonging.user)
    return tab_users


def get_debts(tab: Tab):
    debts = []
    for assosiation in Associating.objects.filter(expense__tab=tab):
        if assosiation.user != assosiation.expense.buyer:
            debts.append(
                (assosiation.user, assosiation.expense.buyer, float(assosiation.cost))
            )
    return debts


def compute_balances(debts:List[Tuple[User, User, float]], people:List[User]):
    if debts == []:
        return {person: 0 for person in people}
    balances = {person: 0 for person in people}
    for debtor, creditor, value in debts:
        balances[debtor] -= value
        balances[creditor] += value
    for person, amount in balances.items():
        balances[person] = round(amount, 2)
    return balances


def get_procent_balances(balances:Dict[User, float]):
    abs_balances = {person: abs(amount) for person, amount in balances.items()}
    result = []
    max_balance = max(abs_balances.values())
    for person, amount in balances.items():
        if max_balance == 0:
            procent = 0
        else:
            procent = int(round(abs(amount) / max_balance, 2) * 100)
        result.append((person, amount, procent))
    return result


def simplify_minflow(debts:List[Tuple[User, User, float]], people:List[User]):
    balances = compute_balances(debts, people)
    transactions = []
    debtors = {p: b for (p, b) in balances.items() if b < 0}
    creditors = {p: b for (p, b) in balances.items() if b > 0}

    while debtors:
        (debtor, debt) = next(iter(debtors.items()))
        (creditor, credit) = next(iter(creditors.items()))
        amount = min(-debt, credit)
        transactions.append((debtor, creditor, "{:.2f}".format(amount)))
        creditors[creditor] -= amount
        debtors[debtor] += amount
        if creditors[creditor] == 0:
            del creditors[creditor]
        if debtors[debtor] == 0:
            del debtors[debtor]

    return transactions


def simplify_with_collector(balances):
    collector = next(iter(balances.keys()))
    return [
        (collector, person, balance)
        for (person, balance) in balances.items()
        if person != collector
    ]


def find_zero_subset(balances):
    for i in range(1, len(balances)):
        for subset in itertools.combinations(balances.items(), i):
            if sum([balance[1] for balance in subset]) == 0:
                return [balance[0] for balance in subset]
    return None


def run_opt(debts:List[Tuple[User, User, float]], people:List[User]):
    remaining_set = compute_balances(debts, people)
    subsets = []
    while (subset := find_zero_subset(remaining_set)) is not None:
        subsets.append(subset)
        remaining_set = {
            x[0]: x[1] for x in remaining_set.items() if x[0] not in subset
        }
    subsets.append(list(remaining_set.keys()))
    balances = compute_balances(debts, people)
    optimal_transactions = []
    for subset in subsets:
        subset_balances = {person: balances[person] for person in subset}
        optimal_transactions.extend(simplify_with_collector(subset_balances))
    final_optimal_transactions = []
    for transaction in optimal_transactions:
        if transaction[2] < 0.0:
            new_transaction = (transaction[1], transaction[0], -transaction[2])
            final_optimal_transactions.append(new_transaction)
        else:
            final_optimal_transactions.append(transaction)
    return final_optimal_transactions


def get_tab_expenses(tab: Tab):
    result = {}
    expenses = Expense.objects.filter(tab=tab).order_by("-date")
    for expense in expenses:
        result[expense] = Associating.objects.filter(expense=expense)
    return result


def get_tab_expense_types(tab: Tab):
    if not ExpenseType.objects.filter(name='Reimbursement', is_private=False).exists():
        ExpenseType.objects.create(name='Reimbursement', is_private=False)
    return ExpenseType.objects.filter(Q(tab=tab) | Q(is_private=False))


def check_if_user_is_in_tab(user: User, tab: Tab):
    return Belonging.objects.filter(user=user, tab=tab, is_active=True).exists()


def get_amount_of_transaction(debtor:User, creditor:User, tab:Tab):
    transactions = simplify_minflow(get_debts(tab), get_tab_users(tab))
    for d, c, a in transactions:
        if debtor == d and creditor == c:
            return a
    return None


def get_user_associatings(user: User):
    return Associating.objects.filter(user=user)


def get_sum_of_user_expenses_by_type(user: User):
    associatings = get_user_associatings(user)
    cost_and_type = {}
    for associating in associatings:
        type = Expense.objects.get(id=associating.expense.id).type.name
        cost_and_type[type] = float(cost_and_type.get(type, 0)) + float(
            associating.cost
        )
    return cost_and_type


def get_sum_of_user_expenses_by_month(user: User, year: int):
    associatings = get_user_associatings(user)
    cost_and_month = {}
    for i in range(1, 13):
        month = datetime.date(1900, i, 1).strftime("%B")
        cost_and_month[month] = 0

    for associating in associatings:
        date = Expense.objects.get(id=associating.expense.id).date
        if str(date.year) == str(year):
            num_month = date.month
            month = datetime.date(1900, num_month, 1).strftime("%B")
            cost_and_month[month] += float(associating.cost)
    return cost_and_month


def get_sum_of_user_expenses_by_month_and_year(user:User):
    associatings = get_user_associatings(user)
    cost_and_month = {}
    year_and_months = {}
    for i in range(1, 13):
        cost_and_month[i] = 0

    for associating in associatings:
        date = Expense.objects.get(id=associating.expense.id).date
        year = date.year
        if year not in year_and_months.keys():
            year_and_months[year] = cost_and_month.copy()

        month = date.month
        year_and_months[year][month] += float(associating.cost)
    return year_and_months


def get_user_from_name(name: str):
    if User.objects.filter(username=name).exists():
        return User.objects.get(username=name)
    else:
        return None


def get_user_from_id(user_id: int):
    if User.objects.filter(pk=user_id).exists():
        return User.objects.get(pk=user_id)
    else:
        return None
