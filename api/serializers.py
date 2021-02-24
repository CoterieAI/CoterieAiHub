from rest_framework import serializers
from .models import Team, Enrollments
from .utils import Roles, default_role
from authentication.models import User

class TeamMemberSerializer(serializers.ModelSerializer):
    #team = serializers.CharField(source='team.name')
    #user = serializers.CharField(source='user.id')
    class Meta:
        model = Enrollments
        fields = ['user', 'role', 'status']

class TeamSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    def get_members(self, obj):
        members = Enrollments.objects.filter(team=obj.id)
        serializer = TeamMemberSerializer(members, many=True)
        return serializer.data


    class Meta:
        model = Team
        fields = ['name', 'owner', 'created_at', 'members', 'updated_at']
        extra_kwargs = {'name':{'required':True}, 'owner':{'read_only':True}, 'members':{'required':False}}

class TeamInviteSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Roles, default=default_role)
    email = serializers.EmailField(write_only=True)
    class Meta:
        model = Enrollments
        fields = ['id', 'email', 'user', 'team', 'role', 'status', 'created_at', 'updated_at']
        extra_kwargs = {'status':{'read_only':True}, 'user':{'read_only':True}}

    def validate(self, attrs):
        team = Team.objects.get(id=attrs['team'].id)
        if not team.owner == self.context.get('request').user:
            raise serializers.ValidationError({"error":"only team creators can make invites"})
        
        if not User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"error":"no user matching this email was found"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('email', None)
        
        return super().create(validated_data)

class TeamMemberUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Roles, default=default_role)
    class Meta:
        model = Enrollments
        fields = ['id', 'user', 'team', 'role', 'status', 'created_at', 'updated_at']
        extra_kwargs = {'status':{'read_only':True}}

    def validate(self, attrs):
        team = Team.objects.get(id=attrs['team'].id)
        if not team.owner == self.context.get('request').user:
            raise serializers.ValidationError({"error":"only team creators can make invites"})
        
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    token= serializers.CharField(max_length=555)

    class Meta:
        fields = ['token']