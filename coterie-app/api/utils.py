from django.db import models
from django.core.mail import EmailMessage
import requests
import sys
import time
import json
from os import path
from kubernetes import client, config
from kafka import KafkaProducer
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent, SendGridException
from django.conf import settings


class MailSender:
    @staticmethod
    def send_email(data):
        message = Mail(from_email=From(settings.FROM_EMAIL),
                       to_emails=To(data['to_email']),
                       subject=Subject(data['email_subject']),
                       plain_text_content=PlainTextContent(data['email_body']))
        message = message.get()
        sendgrid_client = SendGridAPIClient(settings.EMAIL_HOST_PASSWORD)
        sendgrid_client.send(message=message)


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'],
                             from_email=settings.FROM_EMAIL, to=[data['to_email']])
        email.send()


class Roles(models.TextChoices):
    OWNER = "OWNER", "Owner"
    CONTRIBUTOR = "CONTRIBUTOR", "Contributor"
    VIEWER = "VIEWER", "Viewer"


class Status(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"


default_role = Roles.VIEWER
default_status = Status.PENDING


def deploy_to_seldon(name):
    config.load_kube_config(
        path.join(path.dirname(__file__), 'kube-config.yaml'))

    with open(path.join(path.dirname(__file__), "heart.json")) as f:
        template = json.load(f)

    api = client.CustomObjectsApi()
    template["metadata"]["name"] = name
    template["spec"]['annotations']["project_name"] = name
    template["spec"]["name"] = name

    # check if the deployment exists
    try:
        resource = api.get_namespaced_custom_object(
            group="machinelearning.seldon.io",
            version="v1",
            name=name,
            namespace="seldon",
            plural="seldondeployments",
        )

        # deletes the depoyment if it exists
        api.delete_namespaced_custom_object(
            group="machinelearning.seldon.io",
            version="v1",
            name=name,
            namespace="seldon",
            plural="seldondeployments",
            body=client.V1DeleteOptions(),
        )
        print("Resource deleted")
    except:
        pass
    # creates the ne deployment
    api.create_namespaced_custom_object(
        group="machinelearning.seldon.io",
        version="v1",
        namespace="seldon",
        plural="seldondeployments",
        body=template,
    )
    print("Resource created")

    # checks the status
    def is_ready():
        status = api.get_namespaced_custom_object_status(
            group="machinelearning.seldon.io",
            version="v1",
            name=name,
            namespace="seldon",
            plural="seldondeployments",
        )
        if 'status' not in status:
            print('No Status')
            return False
        status = status['status']['state']
        if status == 'Available':
            return True
        if status == 'Creating':
            return False
        if status == "Failed":
            sys.exit(-1)

    start_time = time.time()
    while not is_ready():
        time.sleep(2)
        if time.time() - start_time > 300:  # 5 minute timeout
            print("Timeout waiting for service to start")
            sys.exit(-1)

    # returns the endpoint
    v1 = client.CoreV1Api()
    svc = v1.read_namespaced_service('istio-ingressgateway', 'istio-system')
    gateway = svc.to_dict()['status']['load_balancer']['ingress'][0]['ip']
    endpoint = "http://" + gateway + \
        f'/seldon/seldon/{name}/api/v1.0/predictions'
    print(endpoint)
    return endpoint


def create_job(name):
    """This function creates the JSON required for seldon deploy job"""

    with open(path.join(path.dirname(__file__), "heart.json")) as f:
        template = json.load(f)

    template["metadata"]["name"] = name
    template["spec"]['annotations']["project_name"] = name
    template["spec"]["name"] = name

    return template


class MailClient:
    @staticmethod
    def send_email(data):
        res = requests.post(settings.MAIL_SERVICE_URL, data=data)
        return res
