import os
import re
import yaml

from os import path


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
        with open(path.join(self.compose_dir, 'docker-compose.yml')) as docker_compose_yml:
            self.docker_compose = yaml.load(docker_compose_yml)

            self.has_docker_compose = True

        # Load rancher-compose.yml (if present).
        try:
            with open(path.join(self.compose_dir, 'rancher-compose.yml')) as rancher_compose_yml:
                self.rancher_compose = yaml.load(rancher_compose_yml)
                rancher_compose_catalog_props = self.rancher_compose['.catalog']

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

    def to_cmp_catalog_item(self):
        """
        Create a CMP catalog item to represent the template.
        """

        catalog_item = {
            'name': self.name,
            'questions': []
        }

        if self.has_questions:
            questions = catalog_item["questions"]

            for question in self.questions:
                questions.append({
                    "id": question["variable"],
                    "question": question["label"],
                    "description": question.get("description", question["variable"]),
                    "type": question["type"],
                    "required": question["required"]
                })

        return catalog_item

    def _has_docker_compose_file(self, directory):
        """
        Check if the specified directory contains docker-compose.yml.
        :param directory: The directory to examine.
        """

        template_directory = path.join(self.template_dir, directory)

        try:
            with open(path.join(template_directory, 'docker-compose.yml')):
                return True
        except OSError:
            return False


def _parse_questions(rancher_compose_catalog_props):
    questions = {}
