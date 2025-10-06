# -*- coding: utf-8 -*-
# base.py에 정의된 모든 설정 상속
from .base import *

# 개발 환경 설정 덮어쓰기
DEBUG = True
ALLOWED_HOSTS = ["*"]  # 개발 편의를 위해 모든 호스트 허용
