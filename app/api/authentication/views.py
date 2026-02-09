
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework.response import Response


from .serializers import RegistrationSerializer, User, LoginSerializer


class RegistrationApiView(generics.CreateAPIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer

    def post(self, request):
        user_data = request.data

        serializer = self.serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return_message = {
            "message": "Registration successfull",
            "data": serializer.data
        }

        return Response(return_message, status=status.HTTP_201_CREATED)



class LoginAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Handle user login
        """
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)