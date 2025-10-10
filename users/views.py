# -*- coding: utf-8 -*-
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegistrationSerializer


class RegisterView(generics.CreateAPIView):
    """
    회원가입 API
    Post 요청으로 사용자 생성 + JWT 토큰 발급
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # JWT 토큰 발급
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nickname": user.nickname,
                    "name": user.name,
                    "phone_number": user.phone_number,
                },
                "tokens": {
                    "access": access_token,
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )
