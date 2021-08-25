from kubernetes import client
import urllib3
from django.conf import settings


def start_k8s_client(host, token):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    configuration = client.Configuration()
    configuration.host = host
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    return client


k8s_client = start_k8s_client(settings.K8S_HOST, settings.K8S_TOKEN)
