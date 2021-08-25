from rest_framework import serializers
from django.conf import settings
import json
import requests
from .models import Team, Enrollments, Project
from .utils import Roles, default_role
from authentication.models import User


class TeamMemberSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email')

    class Meta:
        model = Enrollments
        fields = ['user', 'email', 'role', 'status']


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    def get_members(self, obj):
        members = Enrollments.objects.filter(team=obj.id)
        serializer = TeamMemberSerializer(members, many=True)
        return serializer.data

    class Meta:
        model = Team
        fields = ['id', 'name', 'owner', 'created_at', 'members', 'updated_at']
        extra_kwargs = {'name': {'required': True}, 'owner': {
            'read_only': True}, 'members': {'required': False}}


class TeamInviteSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Roles, default=default_role)
    email = serializers.ReadOnlyField(source='user.email')
    invite_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Enrollments
        fields = ['id', 'email', 'invite_email', 'user', 'team', 'role',
                  'status', 'created_at', 'updated_at']
        extra_kwargs = {'status': {'read_only': True},
                        'user': {'read_only': True}}

    def validate(self, attrs):
        if not User.objects.filter(email=attrs['invite_email']).exists():
            raise serializers.ValidationError(
                {"error": "no user matching this email was found"})
        return attrs

    def create(self, validated_data):
        # eliminate the email filed as it is not in the model.
        validated_data.pop('invite_email', None)

        return super().create(validated_data)


class TeamMemberUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Roles, default=default_role)

    class Meta:
        model = Enrollments
        fields = ['id', 'user', 'team', 'role',
                  'status', 'created_at', 'updated_at']
        extra_kwargs = {'status': {'read_only': True}}


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        fields = ['token']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', "is_archived",
                  'url', 'team', 'creator', 'created_at', 'updated_at']
        extra_kwargs = {'creator': {'read_only': True}, 'url': {'required': False}, 'team': {
            'read_only': True}, 'description': {'required': False}, "is_archived": {"required": False, "default": False}}


class UserProjectSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source='team.name')
    team_id = serializers.ReadOnlyField(source='team.id')
    owner = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Project
        fields = ['id', 'title', 'owner', 'description',
                  'is_archived', 'team_name', 'team_id', ]
