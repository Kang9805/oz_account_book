# -*- coding: utf-8 -*-
from django.urls import path

from .views import (
    CookieTokenObtainPairView,
    DeleteAccountView,
    LogoutView,
    MyProfileView,
    PasswordChangeView,
    RegisterView,
)

app_name = "users"

urlpatterns = [
    # 인증/토큰 관리
    path("signup/", RegisterView.as_view(), name="user-signup"),
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    # Simple JWT의 기본 블랙리스트 URL을 통해 Refresh 토큰의 수동 블랙리스트도 허용 (선택 사항)
    # path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # 프로필 관리
    path("me/", MyProfileView.as_view(), name="user-profile"),
    path("me/password/", PasswordChangeView.as_view(), name="password-change"),
    path("me/delete/", DeleteAccountView.as_view(), name="account-delete"),
]
