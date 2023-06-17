from tab.models import Belonging, Expense, ExpenseType
from tab.models import Tab, Associating, Belonging
from django.db.models import Q
import json
import itertools


def get_active_tab_users_json(tab_users):
    users_data = []

    for user in tab_users:
        user_data = {
            "id": user.id,
            "username": user.username,
        }
        users_data.append(user_data)
    return json.dumps(users_data)


def get_user_tabs(user):
    user_tabs = []
    for belonging in Belonging.objects.filter(user=user, is_active=True):
        user_tabs.append(belonging.tab)
    return user_tabs


def get_tab_users(tab, active=False):
    tab_users = []
    for belonging in Belonging.objects.filter(tab=tab):
        if active and belonging.is_active:
            tab_users.append(belonging.user)
        elif not active:
            tab_users.append(belonging.user)
    return tab_users


def get_user_balance_in_tab(user, tab):
    if user in get_tab_users(tab):
        for expense in Expense.objects.filter(tab=tab):
            if expense.user == user:
                return expense.amount


def get_debts(tab):
    debts = []
    for assosiation in Associating.objects.filter(expense__tab=tab):
        if assosiation.user != assosiation.expense.buyer:
            debts.append(
                (assosiation.user, assosiation.expense.buyer, float(assosiation.cost))
            )
    return debts


def compute_balances(debts, people):
    if debts == []:
        return {person: 0 for person in people}
    balances = {person: 0 for person in people}
    for debtor, creditor, value in debts:
        balances[debtor] -= value
        balances[creditor] += value
    for person, amount in balances.items():
        balances[person] = round(amount, 2)
    return balances


def get_procent_balances(balances):
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


def simplify_minflow(debts, people):
    balances = compute_balances(debts, people)
    transactions = []
    debtors = {p: b for (p, b) in balances.items() if b < 0}
    creditors = {p: b for (p, b) in balances.items() if b > 0}

    while debtors:
        (debtor, debt) = next(iter(debtors.items()))
        (creditor, credit) = next(iter(creditors.items()))
        amount = min(-debt, credit)
        transactions.append((debtor, creditor, amount))

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


def show_transactions(transactions):
    for debtor, creditor, value in transactions:
        if value > 0:
            print(f"{debtor} owes {creditor} ${value}")
        else:
            print(f"{creditor} owes {debtor} ${-value}")


def find_zero_subset(balances):
    for i in range(1, len(balances)):
        for subset in itertools.combinations(balances.items(), i):
            if sum([balance[1] for balance in subset]) == 0:
                return [balance[0] for balance in subset]
    return None


def run_opt(debts, people):
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


def get_tab_expenses(tab):
    result = {}
    expenses = Expense.objects.filter(tab=tab)
    for expense in expenses:
        result[expense] = Associating.objects.filter(expense=expense)
    return result


def get_tab_expense_types(tab):
    return ExpenseType.objects.filter(Q(tab=tab) | Q(is_private=False))


def check_if_user_is_in_tab(user, tab):
    return Belonging.objects.filter(user=user, tab=tab, is_active=True).exists()
