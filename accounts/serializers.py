# -*- coding: utf-8 -*-

from django.db import IntegrityError, transaction
from rest_framework import serializers

# models.py에서 정의된 모델과 상수 임포트
from .models import (
    BANK_CHOICES,
    Account,
    Transaction,
)


class AccountSerializer(serializers.ModelSerializer):
    # 🌟 1. 가독성 개선: 은행 이름 및 계좌 종류 이름을 읽기 전용 필드로 추가
    bank_name = serializers.CharField(source="get_bank_code_display", read_only=True)
    account_type_display = serializers.CharField(
        source="get_account_type_display", read_only=True
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "account_number",
            "bank_code",
            "bank_name",
            "account_type",
            "account_type_display",
            "balance",
            "is_deleted",
            "created_at",
        ]
        # balance는 거래를 통해 업데이트되므로 읽기 전용 유지
        read_only_fields = ["id", "balance", "is_deleted", "created_at"]

    # 🌟 2. 유효성 검증 강화: 계좌 번호 중복 검사
    def validate(self, data):
        """계좌 번호 중복 검사 및 은행 코드 유효성 검사를 수행합니다."""

        account_number = data.get("account_number")
        bank_code = data.get("bank_code")

        # 은행 코드 유효성 검사 (안전성 강화)
        if bank_code and bank_code not in [code for code, name in BANK_CHOICES]:
            raise serializers.ValidationError({
                "bank_code": "유효하지 않은 은행 코드입니다."
            })

        # 계좌 번호 중복 검사 (is_deleted=False 인 활성화된 계좌만 중복으로 간주)
        if account_number:
            queryset = Account.objects.filter(
                account_number=account_number, is_deleted=False
            )
            instance = self.instance  # 수정 요청 시 기존 인스턴스

            if instance:
                queryset = queryset.exclude(pk=instance.pk)  # 수정 시 본인 제외

            if queryset.exists():
                raise serializers.ValidationError({
                    "account_number": "이미 등록된 (활성화된) 계좌 번호입니다."
                })

        return data


class TransactionSerializer(serializers.ModelSerializer):
    # 🌟 3. 가독성 개선: 거래 타입, 거래 방식 display name 추가
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )
    transaction_method_display = serializers.CharField(
        source="get_transaction_method_display", read_only=True
    )

    # 계좌 번호를 응답에 포함 (읽기 전용)
    account_number = serializers.CharField(
        source="account.account_number", read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "account_number",
            "transaction_amount",
            "post_transaction_amount",
            "transaction_details",
            "transaction_type",
            "transaction_type_display",
            "transaction_method",
            "transaction_method_display",
            "transaction_timestamp",
            "created_at",
        ]
        # post_transaction_amount는 서버가 계산
        read_only_fields = [
            "id",
            "post_transaction_amount",
            "created_at",
            "account_number",
        ]

    # 🌟 4. 핵심 비즈니스 로직: Atomic Transaction 및 잔액 업데이트
    def create(self, validated_data):
        """거래 생성 시 계좌 잔액을 업데이트하고 거래 후 잔액을 기록합니다."""

        # 🌟 DB 트랜잭션 시작: 잔액 업데이트와 거래 기록을 원자적으로 처리
        try:
            with transaction.atomic():
                account = validated_data["account"]
                amount = validated_data["transaction_amount"]
                trans_type = validated_data["transaction_type"]

                # 잔액 계산 및 출금 시 잔액 부족 검사
                if trans_type == "DEPOSIT":
                    new_balance = account.balance + amount
                elif trans_type == "WITHDRAW":
                    if account.balance < amount:
                        # 🌟 유효성 검사: 잔액 부족 시 에러 발생
                        raise serializers.ValidationError({
                            "transaction_amount": "잔액이 부족하여 출금할 수 없습니다."
                        })
                    new_balance = account.balance - amount
                else:
                    raise serializers.ValidationError({
                        "transaction_type": "유효하지 않은 거래 타입입니다."
                    })

                # 1. Account 모델의 잔액 업데이트
                account.balance = new_balance
                account.save(update_fields=["balance"])

                # 2. Transaction 모델 생성 시 거래 후 잔액(post_transaction_amount) 기록
                validated_data["post_transaction_amount"] = new_balance
                transaction_instance = Transaction.objects.create(**validated_data)

                return transaction_instance
        except IntegrityError:
            # DB 레벨의 충돌(예: Unique 제약 조건 위반) 발생 시 처리
            raise serializers.ValidationError(
                "데이터베이스 오류로 거래를 처리할 수 없습니다."
            )
