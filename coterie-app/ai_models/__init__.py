from kubernetes import client
import urllib3
from django.conf import settings
from google.cloud.container_v1 import ClusterManagerClient
from google.oauth2 import service_account
# Create your views here.


def start_k8s_client(service_account_cred, scope, proj_id, zone, cluster_id):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    credentials = service_account.Credentials.from_service_account_file(
        service_account_cred, scopes=scope)
    cluster_manager_client = ClusterManagerClient(credentials=credentials)
    cluster = cluster_manager_client.get_cluster(
        proj_id, zone, cluster_id)
    configuration = client.Configuration()
    configuration.host = "https://"+cluster.endpoint+":443"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + credentials.token}
    client.Configuration.set_default(configuration)
    return client


# def start_k8s_client(host, token):
#     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#     configuration = client.Configuration()
#     configuration.host = host
#     configuration.verify_ssl = False
#     configuration.api_key = {"authorization": "Bearer " + token}
#     client.Configuration.set_default(configuration)
#     return client


k8s_client = start_k8s_client(
    settings.GOOGLE_APPLICATION_CREDENTIALS, settings.SCOPES, settings.PROJECT_ID, settings.ZONE, settings.CLUSTER_ID)
