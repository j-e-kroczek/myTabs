"""
URL configuration for myTabs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tab import views as tab_views
from user import views as user_views
from django.conf.urls import handler404

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", tab_views.home_view, name="home_view"),
    path("register/", user_views.register_view, name="register_view"),
    path("login/", user_views.login_view, name="login_view"),
    path("profile/", user_views.profile_view, name="profile_view"),
    path("logout/", user_views.logout_view, name="logout_view"),
    path(
        "user_tabs_detail/",
        tab_views.user_tabs_detail_view,
        name="user_tabs_detail_view",
    ),
    path("tab/<int:tab_id>/", tab_views.tab_detail_view, name="tab_detail_view"),
    path("tab/create/", tab_views.tab_create_view, name="tab_create_view"),
    path(
        "tab/<int:tab_id>/create_expense/",
        tab_views.expense_create_view,
        name="expense_create_view",
    ),
    path(
        "tab/<int:tab_id>/add_user/",
        tab_views.add_user_view,
        name="add_user_view",
    ),
    path(
        "tab/<int:tab_id>/remove_user/",
        tab_views.remove_user_view,
        name="remove_user_view",
    ),
    path(
        "tab/<int:tab_id>/edit_expense/<int:expense_id>/",
        tab_views.expense_edit_view,
        name="expense_edit_view",
    ),
]
