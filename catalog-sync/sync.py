"""
Scans the rancher community catalog, creating corresponding entries
in the CMP service catalog.

For now, all this script does is clone the community catalog
and enumerate its contents.
"""

import os

from git import Repo
from os import path
from template import CatalogTemplate


def get_catalog_repo_dir():
    return path.join(
        path.dirname(__file__),
        "repo"
    )


def ensure_local_catalog(local_repo_dir):
    print "Looking for local catalog..."

    try:
        os.stat(local_repo_dir)

        print "Found local catalog in '{}'...".format(
            local_repo_dir
        )
    except OSError:
        print "Cloning catalog repository into '{}'...".format(
            local_repo_dir
        )

        Repo.clone_from(
            url='https://github.com/rancher/community-catalog.git',
            to_path=local_repo_dir
        )


def template_sorter(template_metadata):
    return "{}/{}".format(
        template_metadata.category,
        template_metadata.name
    )


if __name__ == "__main__":
    catalog_repo_dir = get_catalog_repo_dir()
    ensure_local_catalog(catalog_repo_dir)

    print "Scanning catalog..."

    templates_dir = path.join(catalog_repo_dir, "templates")
    templates = [
        CatalogTemplate(
            path.join(templates_dir, template_dir)
        )
        for template_dir in os.listdir(templates_dir)
    ]

    templates = sorted(templates, key=template_sorter)
    for template in templates:
        print("\t[{}] {} - DC={}, RC={}".format(
            template.category,
            template.name,
            template.has_docker_compose,
            template.has_rancher_compose
        ))

        if template.has_questions:
            for question in sorted(template.questions, key=lambda q: q["label"]):
                print("\t\t{} ({})".format(
                    question["label"],
                    question["variable"]
                ))

    print "Done."
