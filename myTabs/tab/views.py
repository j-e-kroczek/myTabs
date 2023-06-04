from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .utils import get_user_tabs
from .models import Tab, Belonging
from django.contrib import messages
from .forms import NewTabForm, NewBelongingForm


# Create your views here.
def home_view(request):
    return render(request, "home.html")


@login_required(login_url="/login")
def user_tabs_view(request):
    context = {"user_tabs": get_user_tabs(request.user)}
    return render(request, template_name="user_tabs.html", context=context)


@login_required(login_url="/login")
def user_tabs_detail_view(request):
    context = {"user_tabs": get_user_tabs(request.user)}
    return render(request, template_name="user_tabs_detail.html", context=context)


@login_required(login_url="/login")
def tab_detail_view(request, tab_id):
    tab = get_object_or_404(Tab, pk=tab_id)
    if not Belonging.objects.filter(user=request.user, tab=tab).exists():
        messages.error(request, "You do not have access to this tab.")
        return redirect("/user_tabs_detail")
    context = {"tab": tab, "user_tabs": get_user_tabs(request.user)}
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
