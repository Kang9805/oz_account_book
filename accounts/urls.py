# -*- coding: utf-8 -*-
from django.urls import path

from accounts.views import AccountListCreateView, AccountRetrieveUpdateDestroyView

app_name = "accounts"

urlpatterns = [
    path("", AccountListCreateView.as_view(), name="account-list-create"),
    path(
        "<int:id>/", AccountRetrieveUpdateDestroyView.as_view(), name="account-detail"
    ),
]
