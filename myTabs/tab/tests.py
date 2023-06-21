from django.test import TestCase
from user.forms import NewUserForm
from user.models import Profile
from tab.models import Tab, Belonging, Expense, Associating, ExpenseType
from tab.utils import (
    convert_list_of_users_to_json,
    get_user_tabs,
    get_tab_users,
    get_debts,
    compute_balances,
    get_procent_balances,
    simplify_minflow,
    run_opt,
    get_tab_expenses,
    get_tab_expense_types,
    check_if_user_is_in_tab,
    get_amount_of_transaction,
    get_user_associatings,
    get_sum_of_user_expenses_by_type,
    get_sum_of_user_expenses_by_month_and_year,
    get_sum_of_user_expenses_by_month,
    get_user_from_id,
    get_user_from_name,
)
from django.contrib.auth.models import User
from model_bakery import baker
import datetime


class ConvertListOfUserToJsonTest(TestCase):
    def setUp(self):
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.list_of_users = [self.user1, self.user2]

    def test_correct_data(self):
        result = convert_list_of_users_to_json(self.list_of_users)
        self.assertEquals(
            result,
            '[{"id": %d, "username": "user1"}, {"id": %d, "username": "user2"}]'
            % (self.user1.id, self.user2.id),
        )

    def test_empty_list(self):
        result = convert_list_of_users_to_json([])
        self.assertEquals(result, "[]")


class GetUserTabsTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        self.tab3 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        baker.make(Belonging, user=self.user1, tab=self.tab3, is_active=False)

    def test_correct_data(self):
        result = get_user_tabs(self.user1)
        self.assertEquals(result, [self.tab1, self.tab2])


class GetTabUsers(TestCase):
    def setUp(self):
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)

    def test_active_true(self):
        result = get_tab_users(self.tab1, active=True)
        self.assertEquals(result, [self.user1, self.user2])

    def test_active_false(self):
        result = get_tab_users(self.tab1, active=False)
        self.assertEquals(result, [self.user1, self.user2, self.user3])


class GetDebtsTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test_correct_data(self):
        result = get_debts(self.tab1)
        expected_result = [
            (self.user2, self.user1, 50.0),
            (self.user1, self.user2, 50.0),
            (self.user3, self.user2, 100.0),
        ]
        self.assertEqual(result, expected_result)

    def test_no_expences(self):
        result = get_debts(self.tab2)
        self.assertEqual(result, [])


class ComputeBalancesTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test_correct_data(self):
        result = compute_balances(get_debts(self.tab1), get_tab_users(self.tab1))
        expected_result = {self.user1: 0, self.user2: 100.0, self.user3: -100.0}
        self.assertEqual(result, expected_result)

    def test_no_expences(self):
        result = compute_balances(get_debts(self.tab2), get_tab_users(self.tab2))
        expected_result = {self.user1: 0}
        self.assertEqual(result, expected_result)


class GetPercentBalancesTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test_correct_data(self):
        result = get_procent_balances(
            compute_balances(get_debts(self.tab1), get_tab_users(self.tab1))
        )
        expected_result = [
            (self.user1, 0.0, 0),
            (self.user2, 100.0, 100),
            (self.user3, -100.0, 100),
        ]
        self.assertEqual(result, expected_result)

    def test_no_expences(self):
        result = get_procent_balances(
            compute_balances(get_debts(self.tab2), get_tab_users(self.tab2))
        )
        expected_result = [(self.user1, 0.0, 0)]
        self.assertEqual(result, expected_result)


class SimplifyMinflowTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test_correct_data(self):
        result = simplify_minflow(get_debts(self.tab1), get_tab_users(self.tab1))
        expected_result = [(self.user3, self.user2, "100.00")]
        self.assertEqual(result, expected_result)

    def test_no_expences(self):
        result = simplify_minflow(get_debts(self.tab2), get_tab_users(self.tab2))
        expected_result = []
        self.assertEqual(result, expected_result)


class RunOptTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test_run_opt(self):
        result = run_opt(get_debts(self.tab1), get_tab_users(self.tab1))
        excepted_result = [(self.user3, self.user2, 100.0)]
        self.assertEqual(result, excepted_result)

    def test_no_expences(self):
        result = run_opt(get_debts(self.tab2), get_tab_users(self.tab2))
        expected_result = []
        self.assertEqual(result, expected_result)


class GetTabExpencesTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test_correct_data(self):
        result = get_tab_expenses(self.tab1)
        expected_result = {
            self.expense1: Associating.objects.filter(expense=self.expense1),
            self.expense2: Associating.objects.filter(expense=self.expense2),
        }
        self.assertEqual(result, result)

    def test_no_expences(self):
        result = get_tab_expenses(self.tab2)
        expected_result = {}
        self.assertEqual(result, expected_result)


class GetTabExpenceTypesTest(TestCase):
    def test(self):
        baker.make(ExpenseType, is_private=False, tab=None)
        tab = baker.make(Tab)
        baker.make(ExpenseType, is_private=True, tab=tab)
        result = get_tab_expense_types(tab)
        self.assertEqual(result.count(), 2)


class CheckIfUserInTabTest(TestCase):
    def test(self):
        user = baker.make(User)
        tab = baker.make(Tab)
        baker.make(Belonging, user=user, tab=tab, is_active=True)
        self.assertTrue(check_if_user_is_in_tab(user, tab))


class GetAmountOfTransactionTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test(self):
        result = get_amount_of_transaction(self.user3, self.user2, self.tab1)
        self.assertEqual(result, "100.00")
        result = get_amount_of_transaction(self.user1, self.user2, self.tab1)
        self.assertEqual(result, None)


class GetUserAssociationgsTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test(self):
        result = get_user_associatings(self.user1)
        self.assertEqual(result.count(), 2)


class GetSumOfUserExpences(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=100, buyer=self.user1
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)

    def test_by_type(self):
        result = get_sum_of_user_expenses_by_type(self.user1)
        self.assertEqual(result, {self.expense_type.name: 100.0})

    def test_by_month(self):
        result = get_sum_of_user_expenses_by_month(self.user1, 2020)
        self.assertEqual(result, result)

    def test_by_year(self):
        result = get_sum_of_user_expenses_by_month_and_year(self.user1)


class GetUserTest(TestCase):
    def setUp(self) -> None:
        self.user = baker.make(User, username="user")

    def test_by_username(self):
        result = get_user_from_name("user")
        self.assertEqual(result, self.user)

    def test_by_id(self):
        result = get_user_from_id(self.user.id)
        self.assertEqual(result, self.user)

    def test_wrong_username(self):
        result = get_user_from_name("wrong")
        self.assertEqual(result, None)

    def test_wrong_id(self):
        result = get_user_from_id(100)
        self.assertEqual(result, None)


class HomeViewTest(TestCase):
    def setUp(self):
        self.url = "/"
        self.user = baker.make(User)

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "home.html")


class UserTabsDetailViewTest(TestCase):
    def setUp(self):
        self.url = "/user_tabs_detail/"
        self.user = baker.make(User)

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "user_tabs_detail.html")

    def test_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_tabs_detail.html")


class TabDetailViewTest(TestCase):
    def setUp(self):
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)
        self.tab = baker.make(Tab)
        self.belonging = baker.make(
            Belonging, user=self.user1, tab=self.tab, is_active=True
        )
        self.url = "/tab/" + str(self.tab.id) + "/"

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "tab_detail.html")

    def test_logged_in(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tab_detail.html")

    def test_logged_in_user_not_in_tab(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "tab_detail.html")

    def test_tab_not_exist(self):
        self.client.force_login(self.user2)
        self.url = "/tab/100/"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class TabCreateViewTest(TestCase):
    def setUp(self):
        self.url = "/tab/create/"
        self.user = baker.make(User)
        self.name = "test_tab"
        self.description = "test_description"

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "create_tab.html")

    def test_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_tab.html")

    def test_post(self):
        self.client.force_login(self.user)
        data = {"name": self.name, "description": self.description}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "create_tab.html")

    def test_post_wrong_data(self):
        self.client.force_login(self.user)
        data = {"name": "", "description": ""}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_tab.html")


class TabEditViewTest(TestCase):
    def setUp(self):
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)
        self.tab = baker.make(Tab)
        self.belonging = baker.make(
            Belonging, user=self.user1, tab=self.tab, is_active=True
        )
        self.url = "/tab/" + str(self.tab.id) + "/edit_tab/"
        self.name = "test_tab"
        self.description = "test_description"

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "edit_tab.html")

    def test_logged_in(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_tab.html")

    def test_logged_in_user_not_in_tab(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "edit_tab.html")

    def test_tab_not_exist(self):
        self.client.force_login(self.user2)
        self.url = "/tab/100/"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        self.client.force_login(self.user1)
        data = {"name": self.name, "description": self.description}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_post_wrong_data(self):
        self.client.force_login(self.user1)
        data = {"name": "", "description": ""}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_tab.html")


class ExpenseCreateViewTest(TestCase):
    def setUp(self):
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)
        self.user3 = baker.make(User)
        self.tab = baker.make(Tab)
        self.belonging = baker.make(
            Belonging, user=self.user1, tab=self.tab, is_active=True
        )
        self.belonging = baker.make(
            Belonging, user=self.user2, tab=self.tab, is_active=True
        )
        self.expense_type = baker.make(ExpenseType, is_private=False)
        self.url = "/tab/" + str(self.tab.id) + "/create_expense/"
        self.name = "test_expense"
        self.buyer = self.user1
        self.cost = 100
        self.date = datetime.date.today()

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "create_expense.html")

    def test_logged_in(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_expense.html")

    def test_logged_in_user_not_in_tab(self):
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "create_expense.html")

    def test_tab_not_exist(self):
        self.client.force_login(self.user2)
        self.url = "/tab/100/"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        self.client.force_login(self.user1)
        data = {
            "name": self.name,
            "buyer": self.buyer.id,
            "type": self.expense_type.id,
            "cost": self.cost,
            "date": self.date,
            "checked_users": [self.user1.id, self.user2.id],
            "1": self.cost / 2,
            "2": self.cost / 2,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "create_expense.html")

    def test_post_none_checked_user(self):
        self.client.force_login(self.user1)
        data = {
            "name": self.name,
            "buyer": self.buyer.id,
            "type": self.expense_type.id,
            "cost": self.cost,
            "date": self.date,
            "checked_users": [],
            "1": self.cost / 2,
            "2": self.cost / 2,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_post_wrong_sum(self):
        self.client.force_login(self.user1)
        data = {
            "name": self.name,
            "buyer": self.buyer.id,
            "type": self.expense_type.id,
            "cost": self.cost,
            "date": self.date,
            "checked_users": [self.user1.id, self.user2.id],
            "1": self.cost,
            "2": self.cost,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_post_checked_user_not_exist(self):
        self.client.force_login(self.user1)
        data = {
            "name": self.name,
            "buyer": self.buyer.id,
            "type": self.expense_type.id,
            "cost": self.cost,
            "date": self.date,
            "checked_users": [self.user1.id, 12],
            "1": self.cost / 2,
            "2": self.cost / 2,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_post_wrong_data(self):
        self.client.force_login(self.user1)
        data = {
            "name": "",
            "buyer": self.buyer.id,
            "type": self.expense_type.id,
            "cost": -10,
            "date": self.date,
            "checked_users": [self.user1.id, self.user2.id],
            "1": self.cost / 2,
            "2": self.cost / 2,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)


class AddUserViewTest(TestCase):
    def setUp(self):
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.user4 = baker.make(User, username="user4")
        self.tab = baker.make(Tab)
        self.belonging = baker.make(
            Belonging, user=self.user1, tab=self.tab, is_active=True
        )
        self.belonging = baker.make(
            Belonging, user=self.user2, tab=self.tab, is_active=True
        )
        self.belonging = baker.make(
            Belonging, user=self.user4, tab=self.tab, is_active=False
        )
        self.url = "/tab/" + str(self.tab.id) + "/add_user/"

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "add_user_to_tab.html")

    def test_logged_in(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_user_to_tab.html")

    def test_logged_in_user_not_in_tab(self):
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "add_user_to_tab.html")

    def test_tab_not_exist(self):
        self.client.force_login(self.user2)
        self.url = "/tab/100/"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        data = {"username": self.user3.username}
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_post_user_is_none(self):
        data = {"username": "user5"}
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_user_to_tab.html")

    def test_post_active_user_in_tab(self):
        data = {"username": "user2"}
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_user_to_tab.html")

    def test_post_add_unactive_user_to_tab(self):
        data = {"username": "user4"}
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "add_user_to_tab.html")


class RemoveUserViewTest(TestCase):
    def setUp(self):
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab = baker.make(Tab)
        self.belonging = baker.make(
            Belonging, user=self.user1, tab=self.tab, is_active=True
        )
        self.belonging = baker.make(
            Belonging, user=self.user2, tab=self.tab, is_active=True
        )
        self.belonging = baker.make(
            Belonging, user=self.user3, tab=self.tab, is_active=True
        )
        self.url = "/tab/" + str(self.tab.id) + "/remove_user/"

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "remove_user_from_tab.html")

    def test_logged_in(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "remove_user_from_tab.html")

    def test_logged_in_user_not_in_tab(self):
        self.client.force_login(self.user3)
        self.user3.belonging_set.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "remove_user_from_tab.html")

    def test_tab_not_exist(self):
        self.client.force_login(self.user2)
        self.url = "/tab/100/"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        data = {"users_to_remove": [self.user2.id, self.user3.id]}
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "remove_user_from_tab.html")

    def test_all_user_removed(self):
        data = {"users_to_remove": [self.user1.id, self.user2.id, self.user3.id]}
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tab.objects.filter(id=self.tab.id).count(), 0)


class ExpenseEditViewTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense,
            name="expense1",
            tab=self.tab1,
            type=self.expense_type,
            cost=100,
            buyer=self.user1,
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)
        self.url = (
            "/tab/" + str(self.tab1.id) + "/edit_expense/" + str(self.expense1.id) + "/"
        )

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "edit_expense.html")

    def test_user_not_in_tab(self):
        self.client.force_login(self.user3)
        Belonging.objects.filter(user=self.user3).delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "edit_expense.html")

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_expense.html")

    def test_no_checked_users(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_no_cost(self):
        self.client.force_login(self.user1)
        data = {
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_wrong_data(self):
        self.client.force_login(self.user1)
        data = {
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 100,
            "2": 100,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_wrong_sum(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 100,
            "2": 500,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_buyer_not_in_tab(self):
        self.client.force_login(self.user1)
        Belonging.objects.filter(user=self.user3).delete()
        data = {
            "name": "test",
            "buyer": self.user3.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 500,
            "2": 500,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_user_not_in_tab(self):
        self.client.force_login(self.user1)
        Belonging.objects.filter(user=self.user3).delete()
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2, 3],
            "1": 500,
            "2": 400,
            "3": 100,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_unexisting_user(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2, 4],
            "1": 500,
            "2": 400,
            "4": 100,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_post(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 500,
            "2": 500,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 1)


class ExpenseRemoveViewTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense,
            name="expense1",
            tab=self.tab1,
            type=self.expense_type,
            cost=100,
            buyer=self.user1,
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)
        self.url = (
            "/tab/"
            + str(self.tab1.id)
            + "/remove_expense/"
            + str(self.expense1.id)
            + "/"
        )

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "remove_expense.html")

    def test_user_not_in_tab(self):
        self.client.force_login(self.user3)
        Belonging.objects.filter(user=self.user3).delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "remove_expense.html")

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "remove_expense.html")

    def test_yes(self):
        self.client.force_login(self.user1)
        response = self.client.post(self.url, {"Yes": "Yes"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="expense1").count(), 0)

    def test_no(self):
        self.client.force_login(self.user1)
        response = self.client.post(self.url, {"No": "No"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="expense1").count(), 1)


class ReimbursementViewTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense,
            name="expense1",
            tab=self.tab1,
            type=self.expense_type,
            cost=100,
            buyer=self.user1,
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)
        self.url = "/tab/" + str(self.tab1.id) + "/reimbursement/"

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "reimbursement.html")

    def test_user_not_in_tab(self):
        self.client.force_login(self.user3)
        Belonging.objects.filter(user=self.user3).delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "reimbursement.html")

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reimbursement.html")


class ReimbursementExpenseViewTest(TestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(User, username="user1")
        self.user2 = baker.make(User, username="user2")
        self.user3 = baker.make(User, username="user3")
        self.tab1 = baker.make(Tab)
        self.tab2 = baker.make(Tab)
        baker.make(Belonging, user=self.user1, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user2, tab=self.tab1, is_active=True)
        baker.make(Belonging, user=self.user3, tab=self.tab1, is_active=False)
        baker.make(Belonging, user=self.user1, tab=self.tab2, is_active=True)
        self.expense_type = baker.make(ExpenseType, is_private=True, tab=self.tab1)
        self.expense1 = baker.make(
            Expense,
            name="expense1",
            tab=self.tab1,
            type=self.expense_type,
            cost=100,
            buyer=self.user1,
        )
        self.expense2 = baker.make(
            Expense, tab=self.tab1, type=self.expense_type, cost=200, buyer=self.user2
        )
        baker.make(Associating, expense=self.expense1, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense1, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user1, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user2, cost=50)
        baker.make(Associating, expense=self.expense2, user=self.user3, cost=100)
        self.url = (
            "/tab/"
            + str(self.tab1.id)
            + "/reimbursement_expense/"
            + str(self.user1.id)
            + "/"
            + str(self.user2.id)
            + "/"
        )

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "reimbursement_expense.html")
        
    def test_user_not_in_tab(self):
        self.client.force_login(self.user3)
        Belonging.objects.filter(user=self.user3).delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "reimbursement_expense.html")
        
    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reimbursement_expense.html")
        
    def test_no_checked_users(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_no_cost(self):
        self.client.force_login(self.user1)
        data = {
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_wrong_data(self):
        self.client.force_login(self.user1)
        data = {
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 100,
            "2": 100,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_wrong_sum(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 100,
            "2": 500,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_buyer_not_in_tab(self):
        self.client.force_login(self.user1)
        Belonging.objects.filter(user=self.user3).delete()
        Associating.objects.filter(user=self.user3).delete()
        data = {
            "name": "test",
            "buyer": self.user3.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 500,
            "2": 500,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_user_not_in_tab(self):
        self.client.force_login(self.user1)
        Belonging.objects.filter(user=self.user3).delete()
        Associating.objects.filter(user=self.user3).delete()
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2, 3],
            "1": 500,
            "2": 400,
            "3": 100,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_unexisting_user(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2, 4],
            "1": 500,
            "2": 400,
            "4": 100,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.filter(name="test").count(), 0)

    def test_post(self):
        self.client.force_login(self.user1)
        data = {
            "name": "test",
            "buyer": self.user1.id,
            "type": self.expense_type.id,
            "cost": 1000,
            "date": self.expense1.date,
            "checked_users": [1, 2],
            "1": 500,
            "2": 500,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.filter(name="test").count(), 1)
    def test_invalid_creditor_or_debtor(self):
        self.client.force_login(self.user1)
        Belonging.objects.filter(user=self.user3).delete()
        Associating.objects.filter(user=self.user3).delete()
        url1 =  (
            "/tab/"
            + str(self.tab1.id)
            + "/reimbursement_expense/"
            + str(self.user3.id)
            + "/"
            + str(self.user2.id)
            + "/"
        )
        url2 =  (
            "/tab/"
            + str(self.tab1.id)
            + "/reimbursement_expense/"
            + str(self.user2.id)
            + "/"
            + str(self.user3.id)
            + "/"
        ) 
        response1 = self.client.get(url1)
        response2 = self.client.get(url2)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        