# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


# ====================================================================
# 1. 회원가입 Serializer
# ====================================================================
class RegistrationSerializer(serializers.ModelSerializer):
    """회원가입 입력을 검증하고 새 user를 생성하는 serializer"""

    # 비밀번호 유효성 검사 및 쓰기 전용 설정
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    # 비밀번호 확인 필드 (쓰기 전용)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "nickname", "name", "phone_number")
        # email 필드는 읽기 전용으로 설정하지 않음 (회원가입 시 입력 받아야 하므로)

    def validate(self, attrs):
        # 두 비밀번호 일치 여부 확인
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({
                "password": "두 비밀번호가 일치하지 않습니다."
            })
        return attrs

    def create(self, validated_data):
        # 비밀번호와 password2를 validated_data에서 분리
        password = validated_data.pop("password")
        validated_data.pop("password2", None)

        # create_user를 사용하여 비밀번호를 안전하게 해싱하여 저장
        user = User.objects.create_user(
            email=validated_data["email"],
            password=password,
            name=validated_data["name"],
            nickname=validated_data.get("nickname"),
            phone_number=validated_data.get("phone_number"),
        )
        return user


# ====================================================================
# 2. 프로필 조회/수정 Serializer
# ====================================================================
class UserSerializer(serializers.ModelSerializer):
    """사용자 프로필 조회 및 수정 (PUT/PATCH)을 위한 serializer"""

    class Meta:
        model = User
        fields = ("id", "email", "nickname", "name", "phone_number")
        read_only_fields = ("email", "id")  # ID와 이메일은 수정할 수 없도록 설정 (권장)


# ====================================================================
# 3. 비밀번호 변경 Serializer
# ====================================================================
class PasswordChangeSerializer(serializers.Serializer):
    """비밀번호 변경 시 현재 비밀번호와 새 비밀번호를 검증하는 serializer"""

    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],  # 새 비밀번호도 유효성 검사
    )

    def validate_current_password(self, value):
        # context에서 현재 요청의 User 객체를 가져옴
        user = self.context["request"].user

        # 현재 비밀번호 일치 여부 확인
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 일치하지 않습니다.")
        return value

    def save(self, **kwargs):
        # User 객체는 validate_current_password를 통해 이미 검증됨
        user = self.context["request"].user

        # 새 비밀번호를 해싱하여 저장
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
