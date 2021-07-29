from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import upload_file


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name',
                  'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def save(self):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name']
        )

        user.set_password(self.validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        try:
            user = User.objects.get(email=self.context['request'].user.email)
            user.set_password(attrs['password2'])
            user.save()
            return (user)
        except:
            raise serializers.ValidationError({"error": "invalid credential"})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"})
        return value


class allUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username']


class CustomTokenObtainPairSerializers(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_superuser'] = user.is_superuser
        return token


class UserSerializer(serializers.ModelSerializer):
    # dob = serializers.DateField(format="%Y-%m-%d", required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(required=False, write_only=True)
    username = serializers.CharField(max_length=256, required=False)
    first_name = serializers.CharField(max_length=256, required=False)
    last_name = serializers.CharField(max_length=256, required=False)
    profile_pic = serializers.URLField(read_only=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'picture', 'username',
                  'first_name', 'last_name', 'profile_pic']

    def validate(self, attrs):
        if attrs.get('picture', None):
            picture = attrs['picture']
            payload = upload_file(picture)
            if payload:
                attrs['profile_pic'] = payload['file_upload']
            else:
                raise serializers.ValidationError(
                    "Unable to handle file upload!")
        return super().validate(attrs)

    def update(self, instance, validated_data):
        validated_data.pop('picture', None)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.username = validated_data.get(
            'username', instance.username)
        instance.profile_pic = validated_data.get(
            'profile_pic', instance.profile_pic)
        return super().update(instance, validated_data)
