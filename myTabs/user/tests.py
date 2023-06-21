from django.test import TestCase
from user.forms import NewUserForm
from user.models import Profile
from django.contrib.auth.models import User
from model_bakery import baker


class NewUserFormTest(TestCase):
    def setUp(self):
        self.data = {}
        self.data["username"] = "testuser"
        self.data["email"] = "test@mail.com"
        self.data["password1"] = "Secret123!"
        self.data["password2"] = "Secret123!"

    def test_correct_data(self):
        form = NewUserForm(self.data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(
            User.objects.get(username="testuser").check_password("Secret123!")
        )

    def test_no_commit(self):
        form = NewUserForm(self.data)
        self.assertTrue(form.is_valid())
        form.save(commit=False)
        self.assertEqual(User.objects.count(), 0)

    def test_false_data(self):
        self.data["password2"] = "123"
        form = NewUserForm(self.data)
        self.assertFalse(form.is_valid())


class RegisterViewTest(TestCase):
    def setUp(self):
        self.data = {}
        self.url = "/register/"
        self.data["username"] = "testuser"
        self.data["email"] = "test@mail.com"
        self.data["password1"] = "Secret123!"
        self.data["password2"] = "Secret123!"
        self.user = baker.make(User)

    def test_register_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_view_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "register.html")

    def test_register_view_post(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertTrue(
            User.objects.get(username="testuser").check_password("Secret123!")
        )

    def test_register_view_post_wrong_data(self):
        self.data["password2"] = "123"
        response = self.client.post(self.url, self.data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 0)


class LoginViewTest(TestCase):
    def setUp(self):
        self.url = "/login/"
        self.user = baker.make(User, username="testuser")
        self.user.set_password("Secret123!")
        self.user.save()

    def test_login_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_view_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "login.html")

    def test_login_view_post(self):
        data = {}
        data["username"] = self.user.username
        data["password"] = "Secret123!"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_login_view_post_wrong_data(self):
        data = {}
        data["username"] = self.user.username
        data["password"] = "123"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.url = "/logout/"
        self.user = baker.make(User)

    def test_logout_view(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_logout_view_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.url = "/profile/"
        self.user = baker.make(User, email="user1@mail.com")
        self.user.set_password("Secret123!")
        self.user.save()
        self.profile = baker.make(Profile, user=self.user)

    def test_profile_view(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_profile_view_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "profile.html")

    def test_profile_view_post_edit_profile(self):
        self.client.force_login(self.user)
        data = {}
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["phone_number"] = "953496094386"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "profile.html")

    def test_profile_view_post_edit_profile_wrong_data(self):
        self.client.force_login(self.user)
        data = {}
        data["username"] = self.user.username
        data["email"] = "testuser"
        data["phone_number"] = self.profile.phone_number
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_post_change_password(self):
        self.client.force_login(self.user)
        data = {}
        data["new_password1"] = "Secret123#"
        data["new_password2"] = "Secret123#"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_post_change_password_wrong_data(self):
        self.client.force_login(self.user)
        data = {}
        data["new_password1"] = "Secret123#"
        data["new_password2"] = "Secret1"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
