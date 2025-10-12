# -*- coding: utf-8 -*-
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    GET, HEAD, OPTIONS 요청에 대해서는 접근을 허용하고,
    그 외 (PUT, PATCH, DELETE) 요청은 객체의 소유자(owner)만 허용합니다.
    """

    def has_permission(self, request, view):
        # 인증된 사용자만 접근 허용
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions (PUT, PATCH, DELETE) are only allowed to the owner of the object.
        # Account, Transaction 모두 obj.account.user 또는 obj.user를 통해 소유자를 확인할 수 있어야 합니다.
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "account") and hasattr(obj.account, "user"):
            return obj.account.user == request.user

        return False
