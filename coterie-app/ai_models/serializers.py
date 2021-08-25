from .models import AiModel, Deployment
import json
import requests
from django.conf import settings
from rest_framework import serializers
from .messages import MODEL_EXISTS_ERROR, MODEL_NOT_FOUND, FIELD_KEY_ERROR
from .utils import create_job


class AiModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiModel
        fields = ['id', 'model_name', 'gcr_url', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class NewAIModelSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(max_length=600, required=False)
    description = serializers.CharField(max_length=600, required=False)

    class Meta:
        model = AiModel
        fields = "__all__"
        extra_kwargs = {"model_id": {"read_only": True},
                        "version_id": {"read_only": True}}

    def create_new_model(self, attrs):
        if AiModel.objects.filter(model_name=attrs['model_name']).exists():
            raise serializers.ValidationError(
                MODEL_EXISTS_ERROR.format(attrs["model_name"]))
        model_ids = list(
            map(lambda m: m.model_id, list(AiModel.objects.all())))
        if model_ids:
            model_id = max(model_ids) + 1
            # the create endpoint only creates the first version
            attrs["model_id"] = model_id
            attrs["version_id"] = 1
            return attrs
        attrs["model_id"] = 1
        attrs["version_id"] = 1
        return attrs

    def update_existing_model(self, attrs):
        model_id = self.context.get("model_id")
        if not AiModel.objects.filter(model_id=model_id).exists():
            raise serializers.ValidationError(MODEL_NOT_FOUND)
        model_versions = list(map(lambda m: m.version_id, list(
            AiModel.objects.filter(model_id=model_id))))

        model_obj = AiModel.objects.filter(model_id=model_id).first()
        # get name
        model_name = model_obj.model_name

        # get description
        description = attrs.get("description", None)

        if len(model_versions) == 0:
            pass
        attrs['model_id'] = model_id
        attrs['version_id'] = max(model_versions) + 1
        attrs['model_name'] = model_name

        if description:
            attrs['description'] = description
        else:
            # fall back to model v1 description
            attrs['description'] = model_obj.description
        return attrs

    def validate(self, attrs):
        context_ = self.context.get("user_action", None)
        if context_ and context_ == "Versioning":
            attrs_ = self.update_existing_model(attrs)
            return attrs_

        model_name = attrs.get("model_name", None)

        if not model_name:
            raise serializers.ValidationError(
                FIELD_KEY_ERROR.format("model_name"))
        # fall to default action
        attrs_ = self.create_new_model(attrs)
        return attrs_


class ModelDetailSerializer(serializers.ModelSerializer):
    gcr_url = serializers.CharField(max_length=1000, required=False)
    description = serializers.CharField(max_length=1000, required=False)

    class Meta:
        model = AiModel
        fields = "__all__"
        extra_kwargs = {"model_id": {"read_only": True},
                        "version_id": {"read_only": True},
                        "model_name": {"read_only": True}}

    def update(self, instance, validated_data):
        # only gcr_url & model description can be modified
        instance.gcr_url = validated_data.get("gcr_url", instance.gcr_url)
        instance.description = validated_data.get(
            "description", instance.description)
        return super().update(instance, validated_data)


class DeploymentSerializer(serializers.ModelSerializer):
    model_id = serializers.IntegerField()
    model_version_id = serializers.IntegerField()

    class Meta:
        model = Deployment
        fields = ['id', 'deployment_id', 'name', 'model_id', 'model_version_id', 'model', 'project',
                  'description', 'service_endpoint', 'creator', 'created_at', 'updated_at']
        read_only_fields = ['deployment_id', 'project', 'creator',
                            'service_endpoint', 'created_at', 'updated_at', 'model']

    def validate(self, attrs):
        model_id = attrs.get('model_id')
        version_id = attrs.get('model_version_id')
        model_obj = AiModel.obejcts.filter(
            model_id=model_id, version_id=version_id)

        if not model_obj:
            raise serializers.ValidationError(MODEL_NOT_FOUND)

        attrs['model'] = model_obj.first()

        return super().validate(attrs)

    def create(self, validated_data):
        # filter out model_id and model_version_id
        validated_data.pop('model_id', None)
        validated_data.pop('model_version_id', None)

        # get the json created
        name = validated_data.get('name')
        json_job = create_job(name)
        # get the image url updated
        json_job['spec']['predictors'][0]['componentSpecs'][0]['spec']['containers'][0]['image'] = validated_data.get(
            'model').gcr_url
        # make a post to producer api
        json_job = json.dumps(json_job)
        url = settings.KAFKA_API_URL
        res = requests.post(url, data=json_job)
        try:
            validated_data['deployment_id'] = res.json()['model_name']
            return super().create(validated_data)
        except:
            raise serializers.ValidationError(
                {"error": "unable to reach producer api successfully"})

    def update(self, instance, validated_data):
        instance.description = validated_data.get(
            "description", instance.description)
        return instance


class SeldonDeploymentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=555, read_only=True)

    class Meta:
        name = ['name']
