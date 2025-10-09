# -*- coding: utf-8 -*-
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import RegistrationSerializer


class RegisterView(generics.CreateAPIView):
    """
    회원가입 API
    Post 요청으로 사용자 생성
    """

    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "name": user.name,
                "phone_number": user.phone_number,
            },
            status.HTTP_201_CREATED,
        )
