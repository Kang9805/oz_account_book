# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase

from users.serializers import RegistrationSerializer

# get_user_model을 한 번 더 임포트하지 않아도 되지만, 명확성을 위해 유지합니다.
User = get_user_model()


class RegistrationSerializerTest(TestCase):
    def test_success_registration(self):
        """회원가입 성공 시 user가 생성되고 비밀번호가 올바른지 테스트"""
        data = {
            "email": "test@example.com",
            "password": "StrongP@ssw0rd1!",
            "password2": "StrongP@ssw0rd1!",
            "nickname": "tester",
            "name": "홍길동",
            "phone_number": "01012345678",
        }
        serializer = RegistrationSerializer(data=data)

        # is_valid가 성공해야 합니다. 실패 시 오류 메시지를 출력합니다.
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        # 1. user 객체가 생성되었는지 확인
        self.assertIsInstance(user, User)
        # 2. 이메일이 정확한지 확인
        self.assertEqual(user.email, data["email"])
        # 3. 비밀번호가 암호화되어 저장되었고, 일치하는지 확인 (True 반환 기대)
        self.assertTrue(user.check_password(data["password"]))
        # 4. 닉네임이 정확한지 확인
        self.assertEqual(user.nickname, data["nickname"])

    def test_password_mismatch(self):
        """비밀번호 불일치시 ValidationError 발생을 테스트"""
        data = {
            "email": "fail@example.com",
            "password": "StrongP@ssw0rd1!",
            "password2": "different!",
            "nickname": "tester2",
            "name": "아무개",
            "phone_number": "01098765432",
        }
        serializer = RegistrationSerializer(data=data)

        # is_valid가 실패해야 합니다.
        self.assertFalse(serializer.is_valid())

        # 'password' 필드에 오류가 포함되어 있는지 확인합니다.
        self.assertIn("password", serializer.errors)
