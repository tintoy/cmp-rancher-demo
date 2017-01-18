import os
import re
import yaml

from os import path, listdir


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
            if re.match("\d+", compose_dir)
        ]

        if not compose_dirs:
            self.has_compose_dir = False

            return

        self.latest_compose_dir = path.join(
            self.template_dir,
            compose_dirs[-1]
        )
        self.has_compose_dir = True

        # TODO: Load docker-compose.yml and rancher-compose.yml
