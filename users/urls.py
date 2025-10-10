# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView

app_name = "users"

urlpatterns = [
    path("signup/", RegisterView.as_view(), name="user-signup"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
