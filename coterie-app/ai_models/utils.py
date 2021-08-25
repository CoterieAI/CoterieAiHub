from os import path
import json


def create_job(name):
    """This function creates the JSON required for seldon deploy job"""

    with open(path.join(path.dirname(__file__), "heart.json")) as f:
        template = json.load(f)

    template["metadata"]["name"] = name
    template["spec"]['annotations']["project_name"] = name
    template["spec"]["name"] = name

    return template
