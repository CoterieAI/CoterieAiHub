from . import serializers
from . import models
from .custompermissions import IsAdminUserOrReadonly
from kubernetes.client.rest import ApiException
from teams_api.custompermissions import IsOwnerOrContributor
from teams_api.models import Project
from .messages import HTTP_BAD_REQUEST, HTTP_NOT_FOUND
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import generics
from . import k8s_client as client
# Create your views here.


class CreateNewModelListView(generics.ListCreateAPIView):
    """
    Creates a New AI model and sets version_id to 1.

    Retrieves all models in the DB
    """
    serializer_class = serializers.NewAIModelSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminUserOrReadonly,)
    queryset = models.AiModel.objects.all()

    @swagger_auto_schema(tags=['AI_Models'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(tags=['AI_Models'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ModelVersionAPIView(generics.GenericAPIView):
    """
    Model Version API
    """
    serializer_class = serializers.NewAIModelSerializer
    permission_classes = (IsAdminUserOrReadonly,)

    def get_queryset(self):
        model_id = self.kwargs['model_id']
        models_ = models.AiModel.objects.filter(model_id=model_id)
        return models_

    @swagger_auto_schema(tags=['AI_Models'])
    def get(self, request, *args, **kwargs):
        """
        Retrieves all models tied to a model_id
        """
        model_list = self.get_queryset()
        serializer = self.serializer_class(model_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['AI_Models'])
    def post(self, request, *args, **kwargs):
        model_id = kwargs['model_id']
        user_action = "Versioning"
        serializer = self.serializer_class(data=request.data, context={
                                           "model_id": model_id, "user_action": user_action})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ModelDetailAPI(generics.GenericAPIView):
    serializer_class = serializers.ModelDetailSerializer
    permission_classes = (IsAdminUserOrReadonly,)

    def get_queryset(self):
        model_id = self.kwargs['model_id']
        models_ = models.AiModel.objects.filter(model_id=model_id)
        return models_

    @swagger_auto_schema(tags=['AI_Models'])
    def get(self, request, *args, **kwargs):
        version_id = kwargs['version_id']
        try:
            model_obj = self.get_queryset().get(version_id=version_id)
            serializer = self.serializer_class(model_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.AiModel.DoesNotExist:
            return Response(HTTP_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(HTTP_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['AI_Models'])
    def put(self, request, *args, **kwargs):
        version_id = kwargs['version_id']
        try:
            model_obj = self.get_queryset().get(version_id=version_id)
            serializer = self.serializer_class(
                instance=model_obj, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.AiModel.DoesNotExist:
            return Response(HTTP_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(HTTP_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['AI_Models'])
    def delete(self, *args, **kwargs):
        version_id = kwargs['version_id']
        try:
            model_obj = self.get_queryset().get(version_id=version_id)
            model_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.AiModel.DoesNotExist:
            return Response(HTTP_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(HTTP_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)


class DeploymentApiView(generics.GenericAPIView):
    serializer_class = serializers.DeploymentSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor)

    def get_queryset(self):
        return models.Deployment.objects.all()

    @swagger_auto_schema(tags=['Deployment'])
    def get(self, request, *args, **kwargs):
        deployments = self.get_queryset().filter(project=kwargs['proj_id'])
        serializer = self.serializer_class(deployments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Deployment'])
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if Project.objects.filter(id=kwargs['proj_id'], team=kwargs['team_id']).exists():
            project = Project.objects.get(
                id=kwargs['proj_id'], team=kwargs['team_id'])
            serializer.is_valid(raise_exception=True)
            serializer.save(project=project, creator=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data={"error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)


class DeploymentDetailApiView(generics.GenericAPIView):
    serializer_class = serializers.DeploymentSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrContributor)

    def get_queryset(self):
        return models.Deployment.objects.all()

    @swagger_auto_schema(tags=['Deployment'])
    def get(self, request, *args, **kwargs):
        try:
            deployment = self.get_queryset().get(id=kwargs['id'])
            serializer = self.serializer_class(deployment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Deployment.DoesNotExist:
            return Response({"error": "deployment not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Deployment'])
    def patch(self, request, *args, **kwargs):
        try:
            deployment = self.get_queryset().get(id=kwargs['id'])
            serializer = self.serializer_class(
                deployment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Deployment.DoesNotExist:
            return Response({"error": "deployment not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Deployment'])
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
        except models.Deployment.DoesNotExist:
            return Response({"error": "deployment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST)


class JobStatus(generics.GenericAPIView):
    serializer_class = serializers.SeldonDeploymentSerializer

    @swagger_auto_schema(tags=['Deployment_Status'])
    def get(self, *args, **kwargs):

        if models.Deployment.objects.filter(id=kwargs['id'], project=kwargs['proj_id']).exists():
            deployment = models.Deployment.objects.get(
                id=kwargs['id'], project=kwargs['proj_id'])
            name = deployment.deployment_id
            try:
                api = client.CustomObjectsApi()
                print("checking status")
                job_status = api.get_namespaced_custom_object_status(
                    group="machinelearning.seldon.io",
                    version="v1",
                    name=name,
                    namespace="seldon",
                    plural="seldondeployments",
                )
                if 'status' not in job_status:
                    return Response({"error": "a status does not exist for this job. please contact admin"})
                job_status = job_status['status']['state']
                return Response({"job status": job_status})
            except ApiException:
                return Response({"error": "job does not exist"}, status=status.HTTP_404_NOT_FOUND)
            except:
                return Response({'error': 'deployment failed'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "job does not exist"}, status=status.HTTP_404_NOT_FOUND)
