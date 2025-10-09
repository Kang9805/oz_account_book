# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """회원가입 입력을 검증하고 새 user를 생성하는 serializer"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "nickname", "name", "phone_number")

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({
                "password": "두 비밀번호가 일치하지 않습니다."
            })
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2", None)

        user = User.objects.create_user(
            email=validated_data["email"],
            password=password,
            name=validated_data["name"],  # 그대로 사용
            nickname=validated_data.get("nickname"),
            phone_number=validated_data.get("phone_number"),
        )
        return user
