# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import Account, Transaction


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "account_number",
            "bank_code",
            "account_type",
            "balance",
            "is_deleted",
            "created_at",
        ]
        read_only_fields = ["id", "balance", "created_at"]  # 읽기 전용 필드


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "transaction_amount",
            "post_transaction_amount",
            "transaction_details",
            "transaction_type",
            "transaction_method",
            "transaction_timestamp",
            "created_at",
        ]
        read_only_fields = ["id", "post_transaction_amount", "created_at"]
