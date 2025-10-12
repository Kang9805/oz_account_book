# -*- coding: utf-8 -*-
# config/settings/prod.py (예시)

from .base import *

# ... (다른 prod 설정) ...

# 배포 환경에서는 HTTPS를 사용하므로 True로 설정
REFRESH_TOKEN_COOKIE_SECURE = True
