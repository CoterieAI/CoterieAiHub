from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from .serializers import TeamSerializer, TeamInviteSerializer, TeamMemberUpdateSerializer, EmailVerificationSerializer, ProjectSerializer
from django.db.models import Q
from .models import Team, Enrollments, Project
from .utils import Util, Status as STATUS
import jwt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from authentication.models import User
from .custompermissions import IsTeamMember, IsOwnerOrContributor
# Create your views here.


class TeamApiView(GenericAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    name = 'team-list'

    def get_queryset(self):
        """
        This view should return a list of all the students
        linked to the currently authenticated Instructor.
        """
        user = self.request.user
        return Team.objects.filter(Q(owner=user.id) | Q(members__id=user.id))

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        data = self.get_queryset()
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class TeamInviteListAPIView(GenericAPIView):
    serializer_class = TeamInviteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    name = 'membership-invite'

    def get_queryset(self):
        user = self.request.user
        return Enrollments.objects.filter(team__owner=user.id)
    
    def post(self, request):
        #validate serializer
        #get user object from email
        #save serilizer and fill user field with user object
        #use serializer data to send email
        serializer = self.serializer_class(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = User.objects.get(email=email)
        serializer.save(user=user)

        user_data = serializer.data
        #{'id': 4, 'user': 3, 'team': 1, 'role': <Roles.VIEWER: 'VIEWER'>, 'status': 'PENDING'}
        print(request.user.username)

        
        team =Team.objects.get(id=user_data['team'])
        role = str(user_data['role']).lower()
        inviter = request.user.username
        payload ={'user':user_data['user'], 'team':user_data['team']}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
        current_site = get_current_site(request).domain
        relativeLink = reverse('invite-acceptance')
        abs_url = 'http://'+current_site+relativeLink+'?token='+str(token)
        email_body = "Hi "+ " " + user.username +",\n " + inviter + " invited you to join "+ team.name + " as " + role + " follow the link below to accept invitation. link expires in 7 days \n" + abs_url

        data ={'email_body':email_body, 'to_email':user.email, 'email_subject':'Team invitation'}

        Util.send_email(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        data = self.get_queryset()
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AcceptEmailInvite(APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            print(token)
            print(f'looking to decode {token} with {settings.JWT_SECRET}')
            payload = jwt.decode(token.decode('utf-8'), str(settings.JWT_SECRET))
            invite = Enrollments.objects.get(user=payload['user'], team=payload['team'])
            #incase a user follows the url twice:
            if invite.status == STATUS.PENDING:
                invite.status = STATUS.ACCEPTED
                invite.save()

            return Response({"Success": "invite status update successful"}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation expired'})
        except jwt.exceptions.DecodeError:
            return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)



class TeamInviteDetailAPIView(GenericAPIView):
    serializer_class = TeamMemberUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    name = 'membership-modify'
    lookup_field = 'invite_id'

    def get(self, request, invite_id):
        user = self.request.user
        try:
            enrollment = Enrollments.objects.get(id=invite_id, team__owner=user.id)
        except:
            raise PermissionDenied({'msg':'you can only modify team invites for teams you own'})
        serializer = self.serializer_class(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, invite_id):
        user = self.request.user

        try:
            enrollment = Enrollments.objects.get(id=invite_id, team__owner=user.id)
        except:
            raise PermissionDenied({'msg':'you can only modify team invites for teams you own'})

        serializer = self.serializer_class(enrollment, data=request.data, context={"request":request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, invite_id):
        user = self.request.user

        try:
            enrollment = Enrollments.objects.get(id=invite_id, team__owner=user.id)
        except enrollment.DoesNotExist:
            return Response({"error": "team memeber does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        deleted = enrollment.delete()
        if deleted:
            msg['success'] = "Deleted successfully"
        else:
            msg["failure"] = "Delete failed"
        return Response(data=msg, status=status.HTTP_204_NO_CONTENT)
        


class ProjectListView(GenericAPIView):
    #this view handles project listing and creation for a particular team
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsTeamMember)
    queryset = Project.objects.all()

    def get(self, request, *args, **kwargs):
        params = kwargs # -> {'team_id': 1}
        projects = Project.objects.filter(team=params['team_id'])
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        params = kwargs
        if Team.objects.filter(id=params['team_id']).exists():
            team = Team.objects.get(id=params['team_id'])
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(creator=request.user, team=team)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error":"error creating project"}, status=status.HTTP_400_BAD_REQUEST)



class ProjectDetailView(GenericAPIView):
    #this view handles project listing and creation for a particular team
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor)
    lookup_field = 'id'
    queryset = Project.objects.all() 

    def get(self, request, *args, **kwargs):
        params = kwargs # -> {'team_id': 1, 'id': 1}
        try:
            project = Project.objects.get(id=params['id'], team=params['team_id'])
            serializer = self.serializer_class(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error":"project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, *args, **kwargs):
        params = kwargs # -> {'team_id': 1, 'id': 1}

        try:
            project = Project.objects.get(id=params['id'], team=params['team_id'])
        except Project.DoesNotExist:
            return Response({"error": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        params = kwargs
        try:
            project = Project.objects.get(id=params['id'])
        except Project.DoesNotExist:
            return Response({"error": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        deleted = project.delete()
        msg = {}
        if deleted:
            msg['success'] = "Deleted successfully"
        else:
            msg["failure"] = "Delete failed"
        return Response(data=msg, status=status.HTTP_204_NO_CONTENT)