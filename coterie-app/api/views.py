from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from .serializers import TeamSerializer, TeamInviteSerializer, TeamMemberUpdateSerializer, EmailVerificationSerializer, ProjectSerializer, AiModelSerializer, SeldonDeploymentSerializer, DeploymentSerializer
from django.db.models import Q
from .models import Team, Enrollments, Project, AiModel, Deployment
from .utils import Util, Status as STATUS, deploy_to_seldon, create_job #, producer
import jwt
import uuid
from os import path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from authentication.models import User
from .custompermissions import IsOwnerOrContributor, hasTeamDetailPermissions, CanInviteUser, IsAdminUserOrReadonly
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from kubernetes import client, config
# Create your views here.


class TeamListApiView(GenericAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    name = 'team-list'

    def get_queryset(self):
        """
        This view should return a list of all teams a user
        created or was invited to.
        """
        user = self.request.user
        return Team.objects.filter(Q(owner=user.id) | Q(members__id=user.id)).distinct()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        data = self.get_queryset()
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamDetailApiView(GenericAPIView):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated, hasTeamDetailPermissions)
    name = 'team-detail'
    lookup_field = 'team_id'

    def get(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=kwargs['team_id'])
            serializer = self.serializer_class(team)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response({"error":"team not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=kwargs['team_id'])
            serializer = self.serializer_class(team, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=kwargs['team_id'])
            deleted = team.delete()
            msg = {}
            if deleted:
                msg['success'] = "Deleted successfully"
            else:
                msg["failure"] = "Delete failed"
            return Response(data=msg, status=status.HTTP_204_NO_CONTENT)
        except Team.DoesNotExist:
            return Response({"error": "team does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
        

class ProjectListView(GenericAPIView):
    #this view handles project listing and creation for a particular team
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor)
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
        


class TeamInviteListAPIView(GenericAPIView):
    serializer_class = TeamInviteSerializer
    permission_classes = (permissions.IsAuthenticated, CanInviteUser)

    def get_queryset(self):
        user = self.request.user
        return Enrollments.objects.filter(team__owner=user.id)
    
    def post(self, request, *args, **kwargs):
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

        
        team =Team.objects.get(id=user_data['team'])
        role = str(user_data['role']).lower()
        inviter = request.user.username
        payload ={'user':user_data['user'], 'team':user_data['team']}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode('utf-8')
        current_site = get_current_site(request).domain
        relativeLink = reverse('invite-acceptance')
        abs_url = 'http://'+current_site+relativeLink+'?token='+token
        email_body = "Hi "+ " " + user.username +",\n " + inviter + " invited you to join "+ team.name + " as " + role + " follow the link below to accept invitation. link expires in 7 days \n" + abs_url

        data ={'email_body':email_body, 'to_email':user.email, 'email_subject':'Team invitation'}

        Util.send_email(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        data = Enrollments.objects.filter(team=kwargs['team_id'])
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamInviteDetailAPIView(GenericAPIView):
    serializer_class = TeamMemberUpdateSerializer
    permission_classes = (permissions.IsAuthenticated, CanInviteUser)
    name = 'membership-modify'
    lookup_field = 'invite_id'

    def get(self, request, *args, **kwargs):
        try:
            enrollment = Enrollments.objects.get(id=kwargs['invite_id'])
        except Enrollments.DoesNotExist:
            return Response({"error": "team member not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        try:
            enrollment = Enrollments.objects.get(id=kwargs['invite_id'])

        except Enrollments.DoesNotExist:
            return Response({"error": "team member not found"}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(enrollment, data=request.data, partial=True)
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
        msg = {}
        if deleted:
            msg['success'] = "Deleted successfully"
        else:
            msg["failure"] = "Delete failed"
        return Response(data=msg, status=status.HTTP_204_NO_CONTENT)



class AcceptEmailInvite(APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithm='HS256')
            invite = Enrollments.objects.get(user=payload['user'], team=payload['team'])
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


class AiModelListView(ListCreateAPIView):
    serializer_class = AiModelSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminUserOrReadonly,)
    queryset = AiModel.objects.all()


class AiModelDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = AiModelSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminUserOrReadonly,)
    queryset = AiModel.objects.all()
    lookup_url_kwarg = 'model_id'

class SeldonDepolymentAPIView(APIView):
    serializer_class = SeldonDeploymentSerializer
    name_param_config = openapi.Parameter('name', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[name_param_config])
    def get(self, request):
        name = request.GET.get('name')
        data ={}
        try:
            #use the deploy function
            data['payload'] = create_job(name)
            data['key'] = str(uuid.uuid4())
            print(data)
            producer.send(settings.KAFKA_TOPIC, data) #settings.KAFKA_TOPIC
            return Response({"success": "job submitted successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'deployment failed'}, status=status.HTTP_400_BAD_REQUEST)

class JobStatus(GenericAPIView):
    serializer_class = SeldonDeploymentSerializer
    def get(self, *args, **kwargs):
        #get the job name
        name = kwargs['job_name']
        print("loading config...")
        config.load_kube_config(path.join(path.dirname(__file__),'kube-config.yaml'))
        print("succesfully loaded!")
        #query the api for status
        api = client.CustomObjectsApi()
        print("checking status")
        status = api.get_namespaced_custom_object_status(
            group="machinelearning.seldon.io",
            version="v1",
            name=name,
            namespace="seldon",
            plural="seldondeployments",
        )
        if 'status' not in status:
            return Response({"error": "a status does not exist for this job. please contact admin"})
        status = status['status']['state']
        return Response({"job status": status})

#detail -> api/team_id/proj_id/deployments/id
class DeploymentApiView(GenericAPIView):
    serializer_class = DeploymentSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor)
    
    def get_queryset(self):
        return Deployment.objects.all()

    def get(self, request, *args, **kwargs):
        deployments = self.get_queryset().filter(project=kwargs['proj_id'])
        serializer = self.serializer_class(deployments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if Project.objects.filter(id=kwargs['proj_id'], team=kwargs['team_id']).exists():
            project = Project.objects.get(id=kwargs['proj_id'], team=kwargs['team_id'])
            serializer.is_valid(raise_exception=True)
            serializer.save(project=project, creator=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data={"error":"bad request"}, status=status.HTTP_400_BAD_REQUEST)


class DeploymentDetailApiView(GenericAPIView):
    serializer_class = DeploymentSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor) 
    
    def get_queryset(self):
        return Deployment.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            deployment = self.get_queryset().get(id=kwargs['id'])
            serializer = self.serializer_class(deployment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Deployment.DoesNotExist:
            return Response({"error":"deployment not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        try:
            deployment = self.get_queryset().get(id=kwargs['id'])
            serializer = self.serializer_class(deployment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Deployment.DoesNotExist:
            return Response({"error":"deployment not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            deployment = self.get_queryset().get(id=kwargs['id'])
            deleted = deployment.delete()
            msg = {}
            if deleted:
                msg['success'] = "Deleted successfully"
            else:
                msg["failure"] = "Delete failed"
            return Response(data=msg, status=status.HTTP_204_NO_CONTENT)
        except Deployment.DoesNotExist:
            return Response({"error": "deployment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error":"invalid request"}, status=status.HTTP_400_BAD_REQUEST)