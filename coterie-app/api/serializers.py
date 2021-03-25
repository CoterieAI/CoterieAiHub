from rest_framework import serializers
from .models import Team, Enrollments, Project, AiModel,   Deployment
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
        #team = Team.objects.get(id=attrs['team'].id)
        #if not team.owner == self.context.get('request').user:
        #    raise serializers.ValidationError({"error":"only team creators can make invites"})
        
        if not User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"error":"no user matching this email was found"})
        return attrs
    
    def create(self, validated_data):
        #eliminate the email filed as it is not in the model.
        validated_data.pop('email', None)
        
        return super().create(validated_data)

class TeamMemberUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Roles, default=default_role)
    class Meta:
        model = Enrollments
        fields = ['id', 'user', 'team', 'role', 'status', 'created_at', 'updated_at']
        extra_kwargs = {'status':{'read_only':True}}

    #def validate(self, attrs):
    #    team = Team.objects.get(id=attrs['team'].id)
    #    if not team.owner == self.context.get('request').user:
    #        raise serializers.ValidationError({"error":"only team creators can make invites"})
    #    
    #    return attrs

class EmailVerificationSerializer(serializers.Serializer):
    token= serializers.CharField(max_length=555)

    class Meta:
        fields = ['token']

#projects should have two urls, 1 serializer, two views
#we should dynamically identify the team and the creator of a project
#only team creator or users with owner role can create/delete projects
#only invited peeps have priviledge of viewing list and detail views
#contributors can only update, they can neither create nor destroy projects
#List/Create -> api/team/projects
#retrieve, update, destroy -> api/team/project/id

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', "is_archived", 'url', 'team', 'creator', 'created_at', 'updated_at']
        extra_kwargs = {'creator':{'read_only':True}, 'url':{'required':False}, 'team':{'read_only':True}, 'description':{'required':False}, "is_archived":{"required":False, "default":False}}


class AiModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiModel
        fields = ['id','model_name', 'gcr_url', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class SeldonDeploymentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=555)

    class Meta:
        name = ['name']


class DeploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deployment
        fields = ['id', 'deployment_id', 'name', 'model', 'project', 'description', 'service_endpoint', 'creator', 'created_at', 'updated_at']
        read_only_fields = ['deployment_id','project', 'creator', 'service_endpoint', 'created_at', 'updated_at']