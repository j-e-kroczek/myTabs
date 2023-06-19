from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .utils import (
    get_user_tabs,
    get_tab_users,
    get_debts,
    compute_balances,
    simplify_minflow,
    run_opt,
    get_procent_balances,
    get_tab_expenses,
    get_tab_expense_types,
    get_amount_of_transaction,
)
from .models import Tab, Belonging, Associating, Expense
from django.contrib import messages
from .forms import NewTabForm, NewBelongingForm, NewExpenseForm
from user.views import get_user_from_name, get_user_from_id
import datetime
from django.contrib.auth.models import User
import json
from .utils import get_active_tab_users_json, check_if_user_is_in_tab


# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return redirect("/user_tabs_detail")
    return render(request, "home.html")


@login_required(login_url="/login")
def balance_bars_view(request):
    context = {"": get_user_tabs(request.user)}
    return render(request, template_name="user_tabs.html", context=context)


@login_required(login_url="/login")
def user_tabs_detail_view(request):
    context = {"user_tabs": get_user_tabs(request.user)}
    return render(request, template_name="user_tabs_detail.html", context=context)


@login_required(login_url="/login")
def tab_detail_view(request, tab_id):
    tab = get_object_or_404(Tab, pk=tab_id)
    debts = get_debts(tab)
    people = get_tab_users(tab)
    balances = compute_balances(debts, people)
    procent_balances = get_procent_balances(balances)
    expenses = get_tab_expenses(tab)
    opt = run_opt(debts, people)

    if not Belonging.objects.filter(
        user=request.user, tab=tab, is_active=True
    ).exists():
        messages.error(request, "You do not have access to this tab.")
        return redirect("/user_tabs_detail")
    context = {
        "tab": tab,
        "user_tabs": get_user_tabs(request.user),
        "tab_users": get_tab_users(tab),
        "transactions": opt,
        "balances": balances.items(),
        "procent_balances": procent_balances,
        "expenses": expenses.items,
    }
    return render(request, template_name="tab_detail.html", context=context)


@login_required(login_url="/login")
def tab_create_view(request):
    user = request.user
    print(request)
    if request.method == "POST":
        tab_form = NewTabForm(request.POST)
        if tab_form.is_valid():
            tab = tab_form.save()
            belonging_form = Belonging.objects.create(
                tab=tab,
                user=user,
            )
            belonging_form.save()
            messages.success(request, "You have created a new tab.")
            return redirect("/user_tabs_detail")
        messages.error(request, "Unsuccessful creation of tab. Invalid information.")
    tab_form = NewTabForm(request.POST)
    belonging_form = NewBelongingForm(request.POST)
    return render(
        request=request,
        template_name="create_tab.html",
        context={
            "tab_form": tab_form,
            "belonging_form": belonging_form,
            "user_tabs": get_user_tabs(request.user),
        },
    )


@login_required(login_url="/login")
def tab_edit_view(request, tab_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    belongings = Belonging.objects.filter(tab=tab, is_active=True)
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    if request.method == "POST":
        tab_form = NewTabForm(request.POST)
        if tab_form.is_valid():
            tab.name = tab_form.cleaned_data["name"]
            tab.description = tab_form.cleaned_data["description"]
            tab.save()
            messages.success(request, "You have edited the tab.")
            return redirect("/tab/" + str(tab_id) + "/edit_tab/")
        messages.error(request, "Unsuccessful edition of tab. Invalid information.")
    return render(
        request=request,
        template_name="edit_tab.html",
        context={
            "user_tabs": get_user_tabs(request.user),
            "belongings": belongings,
            "tab": tab,
        },
    )


@login_required(login_url="/login")
def expense_create_view(request, tab_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    tab_users = get_tab_users(tab, active=True)
    tab_users_json = get_active_tab_users_json(tab_users)
    context = {
        "tab": tab,
        "user_tabs": get_user_tabs(request.user),
        "tab_users": tab_users,
        "tab_users_json": tab_users_json,
        "current_user": user,
        "expense_types": get_tab_expense_types(tab),
        "current_date": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    if request.method == "POST":
        expense_form = NewExpenseForm(request.POST)
        checked_users = request.POST.getlist("checked_users")
        if len(checked_users) == 0:
            messages.error(
                request,
                "Unsuccessful creation of expense. You have to check at least one user.",
            )
            return redirect("/tab/" + str(tab_id) + "/create_expense/")
        cost = float(request.POST.get("cost"))
        cost_per_user = round(cost / len(checked_users), 2)
        cost_per_user_rest = cost - cost_per_user * len(checked_users)
        sum = 0
        for user_id in checked_users:
            user_cost = request.POST.get(user_id)
            sum += float(user_cost)
        print(round(cost_per_user_rest, 2))
        if expense_form.is_valid():
            if sum != cost and sum != cost - round(cost_per_user_rest, 2):
                messages.error(
                    request,
                    "Unsuccessful creation of expense. The sum of costs is not equal to the cost of the expense.",
                )
                return redirect("/tab/" + str(tab_id) + "/")
            else:
                expense = expense_form.save(commit=False)
                expense.tab = tab
                expense.save()
                for user_id in checked_users:
                    user_cost = request.POST.get(user_id)
                    if User.objects.filter(pk=user_id).exists():
                        user = User.objects.get(pk=user_id)
                    else:
                        messages.error(
                            request,
                            "Unsuccessful creation of expense. Invalid information.",
                        )
                        expense.delete()
                        return render(request, "create_expense.html", context=context)
                    Associating.objects.create(
                        user=user, expense=expense, cost=user_cost
                    )

                messages.success(request, "You have created a new expense.")
                return redirect("/tab/" + str(tab_id) + "/")
        messages.error(
            request, "Unsuccessful creation of expense. Invalid information."
        )
    return render(request, "create_expense.html", context=context)


@login_required(login_url="/login")
def add_user_view(request, tab_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    context = {
        "tab": tab,
        "user_tabs": get_user_tabs(request.user),
        "tab_users": get_tab_users(tab),
        "current_user": user,
    }
    if request.method == "POST":
        added_user_name = request.POST.get("id_user")
        added_user = get_user_from_name(added_user_name)
        if added_user is None:
            messages.error(request, "This user does not exist.")

        elif Belonging.objects.filter(user=added_user.id, tab=tab).exists():
            belonging = Belonging.objects.get(user=added_user.id, tab=tab)
            if belonging.is_active:
                messages.error(request, "This user is already in the tab.")
            else:
                belonging.is_active = True
                belonging.save()
                messages.success(request, "You have added a new user.")
                return redirect("/tab/" + str(tab_id) + "/edit_tab/")
        else:
            belonging_form = Belonging.objects.create(
                tab=tab,
                user=added_user,
            )
            belonging_form.save()
            messages.success(request, "You have added a new user.")
            return redirect("/tab/" + str(tab_id) + "/edit_tab/")
    return render(request, "add_user_to_tab.html", context=context)


@login_required(login_url="/login")
def remove_user_view(request, tab_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    if request.method == "POST":
        users_to_remove = request.POST.getlist("users_to_remove")
        for user_to_remove in users_to_remove:
            belongings = Belonging.objects.filter(user=user_to_remove, tab=tab)
            for belonging in belongings:
                belonging.is_active = False
                belonging.save()
        active_tab_belongings = Belonging.objects.filter(tab=tab, is_active=True)
        if len(active_tab_belongings) == 0:
            tab.delete()
            messages.success(request, "This tab has been deleted")
            return redirect("/user_tabs_detail/")
        messages.success(request, "You have removed a user/users.")
        return redirect("/tab/" + str(tab_id) + "/edit_tab/")
    context = {
        "tab": tab,
        "user_tabs": get_user_tabs(request.user),
        "tab_users": get_tab_users(tab, active=True),
        "current_user": user,
    }
    return render(request, "remove_user_from_tab.html", context=context)


@login_required(login_url="/login")
def expense_edit_view(request, tab_id, expense_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    expense = get_object_or_404(Expense, pk=expense_id)
    associatings = Associating.objects.filter(expense=expense)
    tab_users = get_tab_users(tab, active=True)
    tab_users_json = get_active_tab_users_json(tab_users)
    users_in_division = [obj.user for obj in associatings]
    users_not_in_division = [x for x in tab_users if x not in users_in_division]
    context = {
        "tab": tab,
        "expense": expense,
        "associatings": associatings,
        "users_not_in_division": users_not_in_division,
        "user_tabs": get_user_tabs(request.user),
        "tab_users": tab_users,
        "tab_users_json": tab_users_json,
        "current_user": user,
        "expense_types": get_tab_expense_types(tab),
        "current_date": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    if request.method == "POST":
        expense_form = NewExpenseForm(request.POST)
        checked_users = request.POST.getlist("checked_users")
        if len(checked_users) == 0:
            messages.error(
                request,
                "Unsuccessful edition of expense. You have to check at least one user.",
            )
            return redirect(
                "/tab/" + str(tab_id) + "/edit_expense/" + str(expense_id) + "/"
            )
        cost = float(request.POST.get("cost"))
        cost_per_user = round(cost / len(checked_users), 2)
        cost_per_user_rest = cost - cost_per_user * len(checked_users)
        sum = 0
        for user_id in checked_users:
            user_cost = request.POST.get(user_id)
            sum += float(user_cost)

        if expense_form.is_valid():
            if sum != cost and sum != cost - round(cost_per_user_rest, 2):
                messages.error(
                    request,
                    "Unsuccessful creation of expense. The sum of costs is not equal to the cost of the expense.",
                )
                return redirect(
                    "/tab/" + str(tab_id) + "/edit_expense/" + str(expense_id) + "/"
                )
            else:
                expense.name = expense_form.cleaned_data["name"]
                expense.buyer = expense_form.cleaned_data["buyer"]
                expense.type = expense_form.cleaned_data["type"]
                expense.cost = expense_form.cleaned_data["cost"]
                expense.date = expense_form.cleaned_data["date"]

                if expense.buyer not in tab_users:
                    messages.error(
                        request,
                        "Unsuccessful edition of expense. Invalid information.",
                    )
                    return redirect(
                        "/tab/" + str(tab_id) + "/edit_expense/" + str(expense_id) + "/"
                    )

                for user_id in checked_users:
                    if get_user_from_id(user_id) not in tab_users:
                        messages.error(
                            request,
                            "Unsuccessful edition of expense. Invalid information.",
                        )
                        return redirect(
                            "/tab/"
                            + str(tab_id)
                            + "/edit_expense/"
                            + str(expense_id)
                            + "/"
                        )

                for user_id in checked_users:
                    user_cost = request.POST.get(user_id)
                    if User.objects.filter(pk=user_id).exists():
                        user = User.objects.get(pk=user_id)
                    else:
                        messages.error(
                            request,
                            "Unsuccessful edition of expense. Invalid information.",
                        )
                        return redirect(
                            "/tab/"
                            + str(tab_id)
                            + "/edit_expense/"
                            + str(expense_id)
                            + "/"
                        )
                    expense.save()
                    if Associating.objects.filter(expense=expense, user=user).exists():
                        Associating.objects.filter(expense=expense, user=user).update(
                            cost=user_cost
                        )
                    else:
                        Associating.objects.create(
                            user=user, expense=expense, cost=user_cost
                        )
                print(checked_users)
                for user in users_in_division:
                    if str(user.id) not in checked_users:
                        Associating.objects.filter(expense=expense, user=user).delete()
            messages.success(request, "You have edited the expense.")
            return redirect("/tab/" + str(tab_id) + "/")
        messages.error(request, "Unsuccessful edition of expense. Invalid information.")
        print(expense_form.errors)
    return render(request, "edit_expense.html", context=context)


@login_required(login_url="/login")
def expense_remove_view(request, tab_id, expense_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    expense = get_object_or_404(Expense, pk=expense_id)
    associatings = Associating.objects.filter(expense=expense)
    tab_users = get_tab_users(tab, active=True)
    context = {
        "tab": tab,
        "expense": expense,
        "associatings": associatings,
        "user_tabs": get_user_tabs(request.user),
        "tab_users": tab_users,
        "expense_types": get_tab_expense_types(tab),
    }

    if request.method == "POST":
        if "Yes" in request.POST:
            for associating in associatings:
                associating.delete()
            expense.delete()
            messages.success(request, "You have removed the expense.")
            return redirect("/tab/" + str(tab_id) + "/")
        elif "No" in request.POST:
            return redirect("/tab/" + str(tab_id) + "/")
    return render(request, "remove_expense.html", context=context)


@login_required(login_url="/login")
def reimbursement_view(request, tab_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    debts = get_debts(tab)
    tab_users = get_tab_users(tab)
    transactions = simplify_minflow(debts, tab_users)
    print(transactions)
    context = {
        "tab": tab,
        "user_tabs": get_user_tabs(request.user),
        "transactions": transactions,
    }
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    return render(request, "reimbursement.html", context=context)


@login_required(login_url="/login")
def reimbursement_expense_view(request, tab_id, debtor_id, creditor_id):
    user = request.user
    tab = get_object_or_404(Tab, pk=tab_id)
    if not check_if_user_is_in_tab(user, tab):
        return redirect("/404/")
    debtor = get_user_from_id(debtor_id)
    creditor = get_user_from_id(creditor_id)
    amount = get_amount_of_transaction(debtor, creditor, tab)
    tab_users = get_tab_users(tab, active=True)
    tab_users_json = get_active_tab_users_json(tab_users)
    context = {
        "user_tabs": get_user_tabs(request.user),
        "tab_users": tab_users,
        "amount": amount,
        "tab": tab,
        "tab_users_json": tab_users_json,
        "debtor": debtor,
        "creditor": creditor,
        "current_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "expense_types": get_tab_expense_types(tab),
    }
    if request.method == "POST":
        expense_form = NewExpenseForm(request.POST)
        checked_users = request.POST.getlist("checked_users")
        if len(checked_users) == 0:
            messages.error(
                request,
                "Unsuccessful creation of expense. You have to check at least one user.",
            )
            return redirect(
                "/tab/"
                + str(tab_id)
                + "/reimbursement_expense/"
                + str(debtor_id)
                + "/"
                + str(creditor_id)
                + "/"
            )
        cost = float(request.POST.get("cost"))
        cost_per_user = round(cost / len(checked_users), 2)
        cost_per_user_rest = cost - cost_per_user * len(checked_users)
        sum = 0
        for user_id in checked_users:
            user_cost = request.POST.get(user_id)
            sum += float(user_cost)
        print(round(cost_per_user_rest, 2))
        if expense_form.is_valid():
            if sum != cost and sum != cost - round(cost_per_user_rest, 2):
                messages.error(
                    request,
                    "Unsuccessful creation of expense. The sum of costs is not equal to the cost of the expense.",
                )
                return redirect("/tab/" + str(tab_id) + "/")
            else:
                expense = expense_form.save(commit=False)
                expense.tab = tab
                expense.save()
                for user_id in checked_users:
                    user_cost = request.POST.get(user_id)
                    if User.objects.filter(pk=user_id).exists():
                        user = User.objects.get(pk=user_id)
                    else:
                        messages.error(
                            request,
                            "Unsuccessful creation of expense. Invalid information.",
                        )
                        expense.delete()
                        return render(request, "create_expense.html", context=context)
                    Associating.objects.create(
                        user=user, expense=expense, cost=user_cost
                    )

                messages.success(request, "You have created a new expense.")
                return redirect("/tab/" + str(tab_id) + "/")
        messages.error(
            request, "Unsuccessful creation of expense. Invalid information."
        )
    return render(request, template_name="reimbursement_expense.html", context=context)
