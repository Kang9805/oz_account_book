# -*- coding: utf-8 -*-
# accounts/views.py (개선된 버전)

from rest_framework import generics, permissions

from accounts.models import Account, Transaction
from accounts.serializers import AccountSerializer, TransactionSerializer

# 🌟 커스텀 권한 클래스를 임포트해야 합니다.
from .permissions import IsOwnerOrReadOnly


class AuthenticatedAPIView:
    permission_classes = [permissions.IsAuthenticated]


# ----------------------------------------------------------------------
# 1. Account Views
# ----------------------------------------------------------------------


class AccountListCreateView(AuthenticatedAPIView, generics.ListCreateAPIView):
    # (이전 코드와 동일: 목록 조회 및 생성)
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(
            user=self.request.user, is_deleted=False
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountRetrieveUpdateDestroyView(
    AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AccountSerializer
    # 🌟 2. 객체 레벨 권한 추가
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_deleted=False)

    # 🌟 3. Soft Delete 로직 구현
    def perform_destroy(self, instance):
        """실제 삭제 대신 is_deleted 플래그를 True로 변경 (Soft Delete)"""
        instance.is_deleted = True
        instance.save()


# ----------------------------------------------------------------------
# 2. Transaction Views
# ----------------------------------------------------------------------


class TransactionListCreateView(AuthenticatedAPIView, generics.ListCreateAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user).order_by(
            "-transaction_timestamp"
        )

    def perform_create(self, serializer):
        # 🌟 1. 잔액 업데이트 로직을 Serializer로 완전히 위임
        # Serializer의 create() 메서드가 Atomic Transaction을 처리합니다.
        serializer.save()


class TransactionRetrieveUpdateDestroyView(
    AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TransactionSerializer
    # 🌟 2. 객체 레벨 권한 추가
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user)
