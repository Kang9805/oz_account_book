# -*- coding: utf-8 -*-
"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # 🌟 모든 API를 'api/v1/' 접두사 아래에 통합하여 관리
    path(
        "api/v1/",
        include([
            # 1. users 앱의 URL (로그인/토큰 발급 등)
            # users.urls 안에 token/ 및 join/ 등이 있다고 가정
            path("users/", include("users.urls", namespace="users")),
            # 2. accounts 앱의 URL (계좌 및 거래)
            path("accounts/", include("accounts.urls")),
            # 3. JWT Refresh URL (토큰 재발급)
            # 이 URL은 프로젝트의 루트에 가까이 두는 것이 일반적이며,
            # 'api/v1/' 접두사를 유지하면서 'token/refresh/' 이름으로 연결합니다.
            path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        ]),
    ),
]
