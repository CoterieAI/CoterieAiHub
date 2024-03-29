from django.shortcuts import render
from . import serializers
from . import models
from .custompermissions import hasTeamDetailPermissions, CanInviteUser, IsOwnerOrContributor
import jwt
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from authentication.models import User
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .utils import MailClient, Status as STATUS

# Create your views here.


class TeamListApiView(generics.GenericAPIView):
    serializer_class = serializers.TeamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    name = 'team-list'

    def get_queryset(self):
        """
        This view should return a list of all teams a user
        created or was invited to.
        """
        user = self.request.user
        return models.Team.objects.filter(Q(owner=user.id) | Q(members__id=user.id)).distinct()

    @swagger_auto_schema(tags=['Teams'])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=['Teams'])
    def get(self, request):
        data = self.get_queryset()
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamDetailApiView(generics.GenericAPIView):
    serializer_class = serializers.TeamSerializer
    permission_classes = (permissions.IsAuthenticated,
                          hasTeamDetailPermissions)
    name = 'team-detail'
    lookup_field = 'team_id'

    @swagger_auto_schema(tags=['Teams'])
    def get(self, request, *args, **kwargs):
        try:
            team = models.Team.objects.get(id=kwargs['team_id'])
            serializer = self.serializer_class(team)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Team.DoesNotExist:
            return Response({"error": "team not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Teams'])
    def patch(self, request, *args, **kwargs):
        try:
            team = models.Team.objects.get(id=kwargs['team_id'])
            serializer = self.serializer_class(
                team, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Teams'])
    def delete(self, request, *args, **kwargs):
        try:
            team = models.Team.objects.get(id=kwargs['team_id'])
            deleted = team.delete()
            msg = {}
            if deleted:
                msg['success'] = "Deleted successfully"
            else:
                msg["failure"] = "Delete failed"
            return Response(data=msg, status=status.HTTP_204_NO_CONTENT)
        except models.Team.DoesNotExist:
            return Response({"error": "team does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)


class TeamInviteListAPIView(generics.GenericAPIView):
    serializer_class = serializers.TeamInviteSerializer
    permission_classes = (permissions.IsAuthenticated, CanInviteUser)

    def get_queryset(self):
        user = self.request.user
        return models.Enrollments.objects.filter(team__owner=user.id)

    @swagger_auto_schema(tags=['Team_Members'])
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('invite_email')
        user = User.objects.get(email=email)
        serializer.save(user=user)

        user_data = serializer.data

        team = models.Team.objects.get(id=user_data['team'])
        role = str(user_data['role']).lower()
        inviter = request.user.username
        payload = {'user': user_data['user'], 'team': user_data['team']}
        token = jwt.encode(payload, settings.JWT_SECRET,
                           algorithm='HS256')

        # To Do: Use Text Wrap
        current_site = get_current_site(request).domain
        relativeLink = reverse('invite-acceptance')
        abs_url = 'http://'+current_site+relativeLink+'?token='+token
        email_body = "Hi " + " " + user.username + ",\n " + inviter + " invited you to join " + team.name + \
            " as " + role + " follow the link below to accept invitation. link expires in 7 days \n" + abs_url

        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Team invitation'}

        MailClient.send_email(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=['Team_Members'])
    def get(self, request, *args, **kwargs):
        data = models.Enrollments.objects.filter(team=kwargs['team_id'])
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamInviteDetailAPIView(generics.GenericAPIView):
    serializer_class = serializers.TeamMemberUpdateSerializer
    permission_classes = (permissions.IsAuthenticated, CanInviteUser)
    name = 'membership-modify'
    lookup_field = 'invite_id'

    @swagger_auto_schema(tags=['Team_Members'])
    def get(self, request, *args, **kwargs):
        try:
            enrollment = models.Enrollments.objects.get(id=kwargs['invite_id'])
        except models.Enrollments.DoesNotExist:
            return Response({"error": "team member not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Team_Members'])
    def patch(self, request, *args, **kwargs):
        try:
            enrollment = models.Enrollments.objects.get(id=kwargs['invite_id'])

        except models.Enrollments.DoesNotExist:
            return Response({"error": "team member not found"}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(
            enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Team_Members'])
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        invite_id = kwargs['invite_id']
        team_id = kwargs['team_id']
        try:
            enrollment = models.Enrollments.objects.get(
                id=invite_id, team__id=team_id)
        except models.Enrollments.DoesNotExist:
            return Response({"error": "team memeber does not exist"}, status=status.HTTP_404_NOT_FOUND)

        deleted = enrollment.delete()
        msg = {}
        if deleted:
            msg['success'] = "Deleted successfully"
        else:
            msg["failure"] = "Delete failed"
        return Response(data=msg, status=status.HTTP_204_NO_CONTENT)


class AcceptEmailInvite(APIView):
    serializer_class = serializers.EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config], tags=['Invite_Verification'])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=['HS256'])
            invite = models.Enrollments.objects.get(
                user=payload['user'], team=payload['team'])
            # incase a user follows the url twice:
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


class ProjectListView(generics.GenericAPIView):
    # this view handles project listing and creation for a particular team
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor)
    queryset = models.Project.objects.all()

    @swagger_auto_schema(tags=['Projects'])
    def get(self, request, *args, **kwargs):
        params = kwargs  # -> {'team_id': 1}
        projects = models.Project.objects.filter(team=params['team_id'])
        serializer = serializers.ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Projects'])
    def post(self, request, *args, **kwargs):
        params = kwargs
        if models.Team.objects.filter(id=params['team_id']).exists():
            team = models.Team.objects.get(id=params['team_id'])
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(creator=request.user, team=team)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "error creating project"}, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(generics.GenericAPIView):
    # this view handles project listing and creation for a particular team
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor)
    lookup_field = 'id'
    queryset = models.Project.objects.all()

    @swagger_auto_schema(tags=['Projects'])
    def get(self, request, *args, **kwargs):
        params = kwargs
        try:
            project = models.Project.objects.get(
                id=params['id'], team=params['team_id'])
            serializer = self.serializer_class(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "project not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(tags=['Projects'])
    def patch(self, request, *args, **kwargs):
        params = kwargs

        try:
            project = models.Project.objects.get(
                id=params['id'], team=params['team_id'])
        except models.Project.DoesNotExist:
            return Response({"error": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Projects'])
    def delete(self, request, *args, **kwargs):
        params = kwargs
        try:
            project = models.Project.objects.get(id=params['id'])
        except models.Project.DoesNotExist:
            return Response({"error": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)

        deleted = project.delete()
        msg = {}
        if deleted:
            msg['success'] = "Deleted successfully"
        else:
            msg["failure"] = "Delete failed"
        return Response(data=msg, status=status.HTTP_204_NO_CONTENT)
