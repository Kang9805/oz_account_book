# -*- coding: utf-8 -*-
# users/views.py

from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# users/serializers.py에서 정의한 시리얼라이저를 임포트
from .serializers import (
    PasswordChangeSerializer,
    RegistrationSerializer,
    UserSerializer,
)

# 🌟 설정 변수 참조를 SIMPLE_JWT 딕셔너리 내부로 변경
REFRESH_TOKEN_COOKIE_NAME = settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"]
REFRESH_TOKEN_COOKIE_HTTPONLY = settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_HTTPONLY"]
REFRESH_TOKEN_COOKIE_SECURE = settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_SECURE"]
REFRESH_TOKEN_COOKIE_SAMESITE = settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_SAMESITE"]


# ====================================================================
# 1. 인증/토큰 관리 뷰 (로그인, 회원가입, 로그아웃)
# ====================================================================


# 1-1. 회원가입: 사용자 생성 및 Refresh 토큰을 HttpOnly 쿠키에 설정
class RegisterView(generics.CreateAPIView):
    """
    회원가입 API: 사용자 생성 후 Refresh 토큰을 HttpOnly 쿠키에 설정
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 1. JWT 토큰 발급
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 2. 응답 객체 생성
        response = Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "name": user.name,
                    "phone_number": user.phone_number,
                },
                # Refresh 토큰은 바디에서 제외하고 Access 토큰만 전송
                "tokens": {
                    "access": access_token,
                },
            },
            status=status.HTTP_201_CREATED,
        )

        # 3. Refresh 토큰을 HttpOnly 쿠키에 설정 (보안 강화)
        response.set_cookie(
            REFRESH_TOKEN_COOKIE_NAME,  # 👈 수정된 변수 사용
            str(refresh),
            httponly=REFRESH_TOKEN_COOKIE_HTTPONLY,  # 👈 수정된 변수 사용
            secure=REFRESH_TOKEN_COOKIE_SECURE,  # 👈 수정된 변수 사용
            samesite=REFRESH_TOKEN_COOKIE_SAMESITE,  # 👈 수정된 변수 사용
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )

        return response


# 1-2. 로그인: SimpleJWT의 기본 뷰를 상속받아 Refresh 토큰을 HttpOnly 쿠키에 설정
class CookieTokenObtainPairView(TokenObtainPairView):
    """
    로그인 API: 인증 성공 시 access/refresh 토큰 발급.
    Refresh 토큰은 HttpOnly 쿠키에 저장.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # 부모 클래스의 post 메서드를 실행하여 access/refresh 토큰을 얻음
        resp = super().post(request, *args, **kwargs)

        if resp.status_code == 200:
            refresh = resp.data.get("refresh")
            if refresh:
                # Refresh 토큰을 HttpOnly 쿠키에 설정
                resp.set_cookie(
                    REFRESH_TOKEN_COOKIE_NAME,  # 👈 수정된 변수 사용
                    refresh,
                    httponly=REFRESH_TOKEN_COOKIE_HTTPONLY,  # 👈 수정된 변수 사용
                    secure=REFRESH_TOKEN_COOKIE_SECURE,  # 👈 수정된 변수 사용
                    samesite=REFRESH_TOKEN_COOKIE_SAMESITE,  # 👈 수정된 변수 사용
                    max_age=int(
                        settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
                    ),
                )
                # 바디에서 refresh 토큰을 제거하여 클라이언트 노출 방지
                resp.data.pop("refresh", None)
        return resp


# 1-3. 로그아웃: Refresh 토큰 블랙리스트 추가 및 쿠키 삭제
class LogoutView(APIView):
    """
    로그아웃 API: HttpOnly 쿠키의 Refresh 토큰을 블랙리스트에 추가하고 쿠키 삭제.
    """

    permission_classes = [IsAuthenticated]  # 인증된 사용자만 로그아웃 가능

    def post(self, request):
        # 1. 쿠키에서 Refresh 토큰을 가져옴
        refresh_token = request.COOKIES.get(
            REFRESH_TOKEN_COOKIE_NAME
        )  # 👈 수정된 변수 사용

        if refresh_token:
            try:
                # 2. Simple JWT의 RefreshToken 객체를 사용하여 토큰을 블랙리스트에 추가
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                # 이미 블랙리스트이거나 만료된 경우는 무시하고 다음 단계(쿠키 삭제) 진행
                pass

        # 3. 응답 객체 생성 및 쿠키 삭제 명령 추가
        resp = Response(
            {"detail": "Logged out successfully."}, status=status.HTTP_200_OK
        )
        # 클라이언트에게 쿠키를 삭제하도록 명령 (Max-Age=0)
        resp.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)  # 👈 수정된 변수 사용

        return resp


# ====================================================================
# 2. 프로필 관리 뷰 (MyProfile, 비밀번호 변경, 탈퇴)
# ====================================================================


# 2-1. 프로필 조회 및 수정
class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    현재 인증된 사용자의 정보를 조회(GET) 및 수정(PUT/PATCH)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        # 요청한 사용자 본인의 정보를 반환
        return self.request.user


# 2-2. 비밀번호 변경
class PasswordChangeView(APIView):
    """
    비밀번호 변경 API: 현재 비밀번호 확인 후 새 비밀번호로 변경
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # 시리얼라이저의 save() 메서드에서 set_password 처리
        serializer.save()

        # 비밀번호 변경 후 강제 로그아웃 (선택 사항이지만 보안상 권장)
        # 로그아웃 뷰의 로직을 재사용하여 토큰 블랙리스트 처리 및 쿠키 삭제
        LogoutView().post(request)

        return Response(
            {"detail": "Password changed successfully. Please log in again."},
            status=status.HTTP_200_OK,
        )


# 2-3. 회원 탈퇴 (Soft Delete)
class DeleteAccountView(APIView):
    """
    회원 탈퇴 API: 사용자 계정을 비활성화 (Soft Delete) 처리
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        # 1. Soft Delete: is_active 필드를 False로 변경
        user.is_active = False
        user.save()

        # 2. 토큰 블랙리스트 처리 및 쿠키 삭제 (로그아웃 처리)
        refresh_token = request.COOKIES.get(
            REFRESH_TOKEN_COOKIE_NAME
        )  # 👈 수정된 변수 사용
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass

        resp = Response(
            {"detail": "Account deleted successfully."}, status=status.HTTP_200_OK
        )
        resp.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)  # 👈 수정된 변수 사용
        return resp
