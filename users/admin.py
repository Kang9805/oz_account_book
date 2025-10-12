# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


# 기본 UserAdmin 클래스를 커스텀하여 CustomUser 모델에 맞게 설정
class CustomUserAdmin(BaseUserAdmin):
    # 1. 목록 화면 설정
    list_display = ("email", "nickname", "name", "is_staff", "is_active", "date_joined")

    # 2. 검색 기능 설정
    search_fields = ("email", "nickname", "name", "phone_number")

    # 3. 필터링 기능 설정
    list_filter = ("is_staff", "is_active", "date_joined")

    # 4. 상세 폼 필드 설정
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인 정보", {"fields": ("nickname", "name", "phone_number")}),
        # is_staff와 is_superuser는 권한 관련 필드
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("중요 날짜", {"fields": ("last_login", "date_joined")}),
    )

    # 5. 읽기 전용 필드 설정
    # is_staff, is_superuser 등 관리자가 읽기만 가능한 필드 설정
    readonly_fields = ("date_joined", "last_login", "is_staff", "is_superuser")

    ordering = ("email",)


# User 모델을 CustomUserAdmin과 함께 등록
admin.site.register(User, CustomUserAdmin)
