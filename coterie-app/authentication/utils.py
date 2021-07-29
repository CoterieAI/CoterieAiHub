import requests
from io import BytesIO
from django.conf import settings


def upload_file(content: bytes) -> dict:
    file_ = content.read()
    file_ = BytesIO(file_)
    file_.name = content.name

    file_data = {"file_upload": file_}
    url = settings.FILE_SERVICE_URL
    res = requests.post(url, files=file_data)
    if res.status_code == 201:
        return res.json()
    else:
        return {}
