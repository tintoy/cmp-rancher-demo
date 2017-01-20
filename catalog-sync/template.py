import os
import re
import yaml

from os import path


_question_type_map = {
    "string": "text",
    "password": "password",
    "boolean": "checkbox",
    "int": "number",
    "enum": "select",
    "service": "text",
    "multiline": "textarea"
}


class CatalogTemplate(object):
    """
    Represents a template in a Rancher catalog.
    """

    def __init__(self, template_dir):
        """
        Create a new catalog template.

        :param template_dir: The full path to the template directory.
        """

        self.template_dir = template_dir
        self.short_name = path.basename(template_dir)

        config_file = path.join(template_dir, "config.yml")
        with open(config_file) as config_yaml:
            config = yaml.load(config_yaml)

        self.name = config["name"]
        self.description = config["description"]
        self.version = config["version"]
        self.category = config.get("category", "General")

        compose_dirs = [
            compose_dir for compose_dir in os.listdir(self.template_dir)
            if re.match("\d+", compose_dir) and self._has_docker_compose_file(compose_dir)
        ]

        if not compose_dirs:
            self.has_compose_dir = False

            return

        self.compose_dir = path.join(
            self.template_dir,
            compose_dirs[-1]
        )
        self.has_compose_dir = True

        # Load docker-compose.yml
        with open(path.join(self.compose_dir, "docker-compose.yml")) as docker_compose_yml:
            self.docker_compose = yaml.load(docker_compose_yml)

            self.has_docker_compose = True

        # Load rancher-compose.yml (if present).
        try:
            with open(path.join(self.compose_dir, "rancher-compose.yml")) as rancher_compose_yml:
                self.rancher_compose = yaml.load(rancher_compose_yml)
                rancher_compose_catalog_props = self.rancher_compose[".catalog"]

                self.has_rancher_compose = True

                self.questions = rancher_compose_catalog_props.get("questions")
                if self.questions:
                    for question in self.questions:
                        if "label" not in question:
                            question["label"] = question["variable"]

                    self.has_questions = True
                else:
                    self.has_questions = False

        except OSError:
            self.rancher_compose = {}

            self.has_rancher_compose = False

    def to_cmp_service_definition(self, module_id):
        """
        Create a CMP service definition to represent the template.
        """

        service_definition = {
            "name": self.name,
            "description": self.description,
            "category": "RANCHER " + self.category,
            "cost": "0",
            "cost_type": "One Off",
            "lead_time": "15",
            "lead_time_unit": "minute",
            "questions": [],
            "actions": {
                "create_order": [
                    {
                        "command": "run_nflex",
                        "nflex_module_id": module_id
                    }
                ],
            }
        }

        if self.has_questions:
            questions = service_definition["questions"]

            for question in self.questions:
                question_id = question["variable"]
                question_label = question["label"]
                if question_label.endswith(":"):
                    question_label = question_label.rstrip(":")

                question_description = question.get("description", question["variable"])
                question_type = _translate_question_type(question["type"])
                if question_type != "checkbox":
                    question_required = question.get("required", False)
                else:
                    question_required = False

                cmp_question = {
                    "id": question_id,
                    "question": question_label,
                    "description": question_description,
                    "type": question_type,
                    "required": question_required
                }

                if question_type == "select":
                    cmp_question["options"] = [
                        str(option) for option in question["options"]
                    ]

                questions.append(cmp_question)

        return service_definition

    def to_cmp_module_source(self):
        variable_pattern = "\\$\\{%s\\}"

        module_text = """
import re
import requests

rancher_base_url = "http://manage.au9.rancher.tintoy.io:8080/v1"
rancher_api_key = "D4BD9E3BB5025B77290E"
rancher_secret_key = "q8n35diRFA7JfsDiaDUHy5Md6VtKYXr2P8pKgAy7"

def handle(event, context):
    docker_compose = \"\"\"
{docker_compose}
    \"\"\"
    rancher_compose = \"\"\"
{rancher_compose}
    \"\"\"

    # print "docker-compose:"
    # print docker_compose

    # print "rancher-compose:"
    # print rancher_compose

    variables = {{}}
    for option in event["options"]:
        variables[str(option["key"])] = str(option["val"])

    print "variables:"
    print variables

    for variable_name in variables:
        variable_value = variables[variable_name]
        docker_compose = re.sub("{variable_pattern}" % variable_name, variable_value, docker_compose)
        rancher_compose = re.sub("{variable_pattern}" % variable_name, variable_value, rancher_compose)

    response = requests.post(rancher_base_url + "/projects/1a5/environments", auth=(rancher_api_key, rancher_secret_key), json={{
        "name": "{name}",
        "dockerCompose": docker_compose,
        "rancherCompose": rancher_compose,
        "environment": variables,
        "startOnCreate": True
    }})

    print "Deployed stack '{{}}'.".format(
        response.json()["id"]
    )

        """.format(
            docker_compose=yaml.dump(self.docker_compose, default_flow_style=False),
            rancher_compose=yaml.dump(self.rancher_compose, default_flow_style=False),
            variable_pattern=variable_pattern,
            name=self.short_name
        )

        return module_text

    def _has_docker_compose_file(self, directory):
        """
        Check if the specified directory contains docker-compose.yml.
        :param directory: The directory to examine.
        """

        template_directory = path.join(self.template_dir, directory)

        try:
            with open(path.join(template_directory, "docker-compose.yml")):
                return True
        except OSError:
            return False


def _translate_question_type(question_type):
    """
    Translate a Rancher question type to its CMP equivalent.
    """

    return _question_type_map[question_type]
