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
    TokenRefreshView,  # 👈 TokenRefreshView 임포트 추가
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # users 앱의 URL (네임스페이스 포함)
    # 참고: users.urls에서 name='token_obtain_pair'를 사용하므로,
    # login URL은 /api/users/token/ 이 될 것입니다.
    path("api/users/", include("users.urls", namespace="users")),
    path("api/accounts/", include("accounts.urls")),
    # 🌟 누락된 JWT Refresh URL 추가
    # 테스트 코드(reverse("token_refresh"))가 참조하는 이름입니다.
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
