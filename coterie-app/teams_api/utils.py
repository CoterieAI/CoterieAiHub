from django.db import models
from django.conf import settings
import requests

"""USER ROLES RELAATED UTILS"""


class Roles(models.TextChoices):
    OWNER = "OWNER", "Owner"
    CONTRIBUTOR = "CONTRIBUTOR", "Contributor"
    VIEWER = "VIEWER", "Viewer"


class Status(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"


default_role = Roles.VIEWER
default_status = Status.PENDING


""" MAIL RELATED UTILS"""


class MailClient:
    @staticmethod
    def send_email(data):
        res = requests.post(settings.MAIL_SERVICE_URL, data=data)
        return res
