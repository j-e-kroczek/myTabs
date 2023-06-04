from tab.models import Belonging


def get_user_tabs(user):
    user_tabs = []
    for belonging in Belonging.objects.filter(user=user):
        user_tabs.append(belonging.tab)
    return user_tabs