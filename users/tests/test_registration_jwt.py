# -*- coding: utf-8 -*-
# users/tests/test_registration_jwt.py

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()

# 테스트 URL 및 기본 데이터 정의
REFRESH_URL = reverse("token_refresh")


class UserAuthTest(APITestCase):
    """
    회원가입, 로그인, 로그아웃, 토큰 갱신, 프로필 접근 등
    JWT 및 HttpOnly 쿠키 기반 인증 플로우 테스트
    """

    def setUp(self):
        self.client = APIClient()
        self.SIGNUP_URL = reverse("users:user-signup")
        self.LOGIN_URL = reverse("users:token_obtain_pair")
        self.LOGOUT_URL = reverse("users:user-logout")
        self.PROFILE_URL = reverse("users:user-profile")

        # 🌟 쿠키 이름을 settings.SIMPLE_JWT에서 가져와 상수로 정의하여 사용
        self.COOKIE_NAME = settings.SIMPLE_JWT.get(
            "REFRESH_TOKEN_COOKIE_NAME", "refresh_token"
        )

        self.user_data = {
            "email": "testuser@example.com",
            "password": "TestPassword123!",
            "password2": "TestPassword123!",
            "nickname": "tester",
            "name": "Test User",
            "phone_number": "01012345678",
        }

        self.existing_user = User.objects.create_user(
            email="existing@user.com",
            password="ExistingPassword1!",
            name="Existing User",
        )
        self.EXISTING_USER_CREDENTIALS = {
            "email": "existing@user.com",
            "password": "ExistingPassword1!",
        }

    # ====================================================================
    # 1. 회원가입 (Registration) 테스트
    # ====================================================================

    def test_registration_success_and_cookie_issued(self):
        """정상 회원가입 시 201 응답과 Access 토큰 및 HttpOnly Refresh 쿠키 발급 확인"""
        response = self.client.post(self.SIGNUP_URL, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data.get("tokens", {}))

        # HttpOnly Refresh 쿠키 확인
        cookie_name = self.COOKIE_NAME  # 👈 수정된 변수 사용
        self.assertIn(cookie_name, response.cookies)
        self.assertTrue(response.cookies[cookie_name]["httponly"])

    def test_registration_password_mismatch(self):
        """비밀번호 불일치 시 400 Bad Request"""
        data = self.user_data.copy()
        data["password2"] = "DifferentPassword!"
        response = self.client.post(self.SIGNUP_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_missing_field(self):
        """필수 필드 누락 시 400 Bad Request"""
        data = self.user_data.copy()
        data.pop("email")
        response = self.client.post(self.SIGNUP_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    # ====================================================================
    # 2. 로그인 (CookieTokenObtainPairView) 테스트
    # ====================================================================

    def test_login_success_and_cookie_issued(self):
        """정상 로그인 시 200 응답, Access 토큰 발급, Refresh 쿠키 설정 확인"""
        response = self.client.post(
            self.LOGIN_URL, self.EXISTING_USER_CREDENTIALS, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
        self.assertFalse("refresh" in response.data)  # 바디에 refresh 없어야 함

        # HttpOnly Refresh 쿠키 확인
        cookie_name = self.COOKIE_NAME  # 👈 수정된 변수 사용
        self.assertIn(cookie_name, response.cookies)
        self.assertTrue(response.cookies[cookie_name]["httponly"])

    # ====================================================================
    # 3. 인증 및 프로필 접근 테스트
    # ====================================================================

    def test_profile_access_with_token(self):
        """Access Token을 이용한 인증된 API 접근 확인"""
        login_response = self.client.post(
            self.LOGIN_URL, self.EXISTING_USER_CREDENTIALS, format="json"
        )
        access_token = login_response.data.get("access")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_response = self.client.get(self.PROFILE_URL)

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)

    def test_profile_access_unauthorized(self):
        """토큰 없이 접근 시 401 Unauthorized 확인"""
        self.client.credentials()
        response = self.client.get(self.PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ====================================================================
    # 4. 로그아웃 (LogoutView) 및 블랙리스트 테스트
    # ====================================================================

    def test_logout_success_and_cookie_deleted(self):
        """로그아웃 시 200 응답, 쿠키 삭제 명령, 토큰 블랙리스트 확인"""
        # 1. 로그인하여 토큰 및 쿠키 획득
        login_response = self.client.post(
            self.LOGIN_URL, self.EXISTING_USER_CREDENTIALS, format="json"
        )
        access_token = login_response.data.get("access")

        COOKIE_NAME = self.COOKIE_NAME  # 👈 수정된 변수 사용
        refresh_token = login_response.cookies[COOKIE_NAME].value

        # 2. Access Token과 Refresh Cookie를 설정하고 로그아웃 요청
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        self.client.cookies.load({COOKIE_NAME: refresh_token})
        logout_response = self.client.post(self.LOGOUT_URL)

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # 3. 쿠키 삭제 명령 확인
        self.assertIn(COOKIE_NAME, logout_response.cookies)
        self.assertEqual(logout_response.cookies[COOKIE_NAME].value, "")

        # 4. 블랙리스트 확인 (Refresh Token 재사용 불가)
        self.client.credentials()

        # Refresh Token을 Body에 넣어 블랙리스트 검증을 시도
        self.client.cookies.load({COOKIE_NAME: refresh_token})
        refresh_response = self.client.post(
            REFRESH_URL,
            {"refresh": refresh_token},  # Body에 Refresh 토큰 직접 포함
            format="json",
        )

        # 이제 블랙리스트로 인해 401을 기대합니다.
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Token is blacklisted", refresh_response.data.get("detail", ""))
