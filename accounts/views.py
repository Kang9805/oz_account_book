# -*- coding: utf-8 -*-
from rest_framework import generics, permissions

from accounts.models import Account, Transaction
from accounts.serializers import AccountSerializer, TransactionSerializer


class AuthenticatedAPIView:
    """로그인 필수 View 공통 부모"""

    permission_classes = [permissions.IsAuthenticated]


class AccountListCreateView(AuthenticatedAPIView, generics.ListCreateAPIView):
    """내 계좌 목록 조회 + 계좌 생성"""

    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountRetrieveUpdateDestroyView(
    AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView
):
    """계좌 상세 조회 / 수정 / 삭제"""

    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_deleted=False)


class TransactionListCreateView(AuthenticatedAPIView, generics.ListCreateAPIView):
    """거래 내역 조회 및 생성 (입/출금)"""

    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        account = serializer.validated_data["account"]
        amount = serializer.validated_data["transaction_amount"]
        tx_type = serializer.validated_data["transaction_type"]

        # 입금이면 +, 출금이면 -
        if tx_type == "DEPOSIT":
            post_amount = account.balance + amount
        else:
            post_amount = account.balance - amount

        # 거래 내역 저장 + 계좌 잔액 갱신
        serializer.save(post_transaction_amount=post_amount)
        account.balance = post_amount
        account.save()


class TransactionRetrieveUpdateDestroyView(
    AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView
):
    """거래 건당 조회/수정/삭제"""

    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user)
