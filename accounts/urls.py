# -*- coding: utf-8 -*-
from django.urls import path

from accounts.views import (
    AccountListCreateView,
    AccountRetrieveUpdateDestroyView,
    TransactionListCreateView,
    TransactionRetrieveUpdateDestroyView,
)

app_name = "accounts"

urlpatterns = [
    path("accounts/", AccountListCreateView.as_view(), name="account-list"),
    path(
        "accounts/<int:pk>/",
        AccountRetrieveUpdateDestroyView.as_view(),
        name="account-detail",
    ),
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list"),
    path(
        "transactions/<int:pk>/",
        TransactionRetrieveUpdateDestroyView.as_view(),
        name="transaction-detail",
    ),
]
