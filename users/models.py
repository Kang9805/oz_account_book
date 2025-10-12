# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """커스텀 유저 모델"""

    email = models.EmailField(unique=True, verbose_name="이메일")
    nickname = models.CharField(max_length=50, unique=True, verbose_name="닉네임")
    name = models.CharField(max_length=100, blank=True, verbose_name="이름")
    phone_number = models.CharField(
        max_length=20, blank=True, verbose_name="휴대폰 번호"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="가입일")

    objects = UserManager()  # 커스텀 매니저 연결

    USERNAME_FIELD = "email"  # 이메일을 로그인 ID로 사용
    REQUIRED_FIELDS = ["nickname", "name", "phone_number"]  # 슈퍼유저 생성 시 필수 입력

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"

    def __str__(self):
        return self.email
