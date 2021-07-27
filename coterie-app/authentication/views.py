from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import SignUpSerializer, ChangePasswordSerializer, allUsersSerializer, CustomTokenObtainPairSerializers
from .models import User


class RegisterView(GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = {"username": user.username, "email": user.email}
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(GenericAPIView):
    # used when authenticated user wants to change password
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(
            user, data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        return Response({'success': True, 'message': 'Passowrd reset success'}, status=status.HTTP_200_OK)


class MyTokenObtainPairView(TokenObtainPairView):
    # login view
    serializer_class = CustomTokenObtainPairSerializers


class AllUsers(ListAPIView):
    model = User
    serializer_class = allUsersSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAdminUser, )
