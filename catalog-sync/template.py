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
