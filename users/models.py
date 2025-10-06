from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """유저 모델 정의"""

    email = models.EmailField(unique=True, verbose_name='이메일')
    nickname = models.CharField(max_length=50, unique=True, verbose_name='닉네임')
    name = models.CharField(max_length=100, blank=True, verbose_name='이름')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='휴대폰 번호')

    # 이메일을 주 식별자로 설정
    username = None
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'name', 'phone_number']


    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'

    def __str__(self):
        return self.email