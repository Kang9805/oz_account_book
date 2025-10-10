# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse(
            "users:user-signup"
        )  # users/urls.py에서 RegisterView 이름 확인
        self.user_data = {
            "email": "testuser@example.com",
            "password": "TestPassword123!",
            "password2": "TestPassword123!",
            "nickname": "tester",
            "name": "Test User",
            "phone_number": "01012345678",
        }

    def test_registration_success(self):
        """정상적인 회원가입 요청 시 201 Created 응답"""
        response = self.client.post(self.url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())
        # ✅ response 구조에 맞게 수정
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])
        self.assertEqual(response.data["user"]["nickname"], self.user_data["nickname"])

    def test_registration_password_mismatch(self):
        """비밀번호와 비밀번호 확인이 다를 경우 400 Bad Request"""
        data = self.user_data.copy()
        data["password2"] = "DifferentPassword!"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_missing_field(self):
        """필수 필드 누락 시 400 Bad Request"""
        data = self.user_data.copy()
        data.pop("email")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
