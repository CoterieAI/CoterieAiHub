from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import ProfileUpdateSerializer, SignUpSerializer, ChangePasswordSerializer, UserProjectListSerializer, allUsersSerializer, CustomTokenObtainPairSerializers, UserSerializer
from .models import User
from .permissions import IsOwnerOrReadOnly
from rest_framework.parsers import MultiPartParser, FileUploadParser
from drf_yasg.utils import swagger_auto_schema


class RegisterView(GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny, )

    @swagger_auto_schema(tags=['Sign_Up'])
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

    @swagger_auto_schema(tags=['Profile'])
    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(
            user, data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        return Response({'success': True, 'message': 'Passowrd reset success'}, status=status.HTTP_200_OK)


class MyTokenObtainPairView(TokenObtainPairView):
    # login view
    serializer_class = CustomTokenObtainPairSerializers

    @swagger_auto_schema(tags=['Login'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AllUsers(ListAPIView):
    model = User
    serializer_class = allUsersSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAdminUser, )

    @swagger_auto_schema(tags=['Users'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserProfiles(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()

    @swagger_auto_schema(tags=['Users'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserProfilesById(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return User.objects.all()

    @swagger_auto_schema(tags=['Users'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserProfile(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FileUploadParser)

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ProfileUpdateSerializer
        return UserSerializer

    @swagger_auto_schema(tags=['Profile'])
    def get(self, request, *args, **kwargs):
        user = self.get_queryset().get(id=request.user.id)
        Serializer = self.serializer_class(user)
        return Response(Serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Profile'])
    def put(self, request, *args, **kwargs):
        user_obj = self.get_queryset().get(id=request.user.id)
        update_serializer = self.get_serializer_class()
        serializer = update_serializer(
            data=request.data, instance=user_obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProjects(GenericAPIView):
    serializer_class = UserProjectListSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return User.objects.all()

    @swagger_auto_schema(tags=['User_Projects'])
    def get(self, request, *args, **kwargs):
        user = self.get_queryset().get(id=request.user.id)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
