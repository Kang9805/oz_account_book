# -*- coding: utf-8 -*-
from django.test import TestCase
from django.utils import timezone

from accounts.models import Account, Transaction
from users.models import User


class AccountViewTestCase(TestCase):
    def setUp(self):
        # 1️⃣ 사용자 생성
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )

        # 2️⃣ 계좌 생성 (모델 필드명 정확히 반영)
        self.account = Account.objects.create(
            user=self.user,
            account_number="123-456-789",
            bank_code="001",
            account_type="CHECKING",
            balance=100000,
        )

        # 3️⃣ 거래 생성 (모델 필드명 정확히 반영)
        self.transaction = Transaction.objects.create(
            account=self.account,
            transaction_amount=5000,
            post_transaction_amount=105000,
            transaction_details="입금 테스트",
            transaction_type="DEPOSIT",
            transaction_method="TRANSFER",
            transaction_timestamp=timezone.now(),
        )

    # 테스트 메서드 예시
    def test_account_list(self):
        accounts = Account.objects.filter(user=self.user)
        self.assertEqual(accounts.count(), 1)
        self.assertEqual(accounts.first().account_number, "123-456-789")

    def test_transaction_create_deposit(self):
        transaction = Transaction.objects.create(
            account=self.account,
            transaction_amount=2000,
            post_transaction_amount=107000,
            transaction_details="추가 입금",
            transaction_type="DEPOSIT",
            transaction_method="TRANSFER",
            transaction_timestamp=timezone.now(),
        )
        self.assertEqual(transaction.transaction_amount, 2000)

    def test_transaction_create_withdraw(self):
        transaction = Transaction.objects.create(
            account=self.account,
            transaction_amount=3000,
            post_transaction_amount=104000,
            transaction_details="출금 테스트",
            transaction_type="WITHDRAW",
            transaction_method="ATM",
            transaction_timestamp=timezone.now(),
        )
        self.assertEqual(transaction.transaction_type, "WITHDRAW")
