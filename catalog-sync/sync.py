"""
Scans the rancher community catalog, creating corresponding entries
in the CMP service catalog.

For now, all this script does is clone the community catalog
and enumerate its contents.
"""

import json
import os

from cmp_client import CMPClient
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

    client = CMPClient("https://sandbox.cmp.nflex.io/cmp/basic/api", "nflex-11", "ins1ght")
    service_definitions_by_name = {}
    for existing_service_definition in client.list_service_definitions().json():
        service_definitions_by_name[existing_service_definition["name"]] = existing_service_definition["id"]

    modules_by_name = {}
    for existing_module in client.list_modules().json():
        modules_by_name[existing_module["name"]] = existing_module["id"]

    for template in templates:
        if template.short_name in modules_by_name:
            module = client.update_module(
                modules_by_name[template.short_name],
                template.short_name,
                template.to_cmp_module_source()
            ).json()
        else:
            module = client.create_module(
                template.short_name,
                "service-catalog",
                template.to_cmp_module_source()
            ).json()

            modules_by_name[module["name"]] = module["id"]

    service_definition_ids = []
    for template in templates:
        if template.name in service_definitions_by_name:
            service_definition_ids.append(
                service_definitions_by_name[template.name]
            )
            continue

        module_id = modules_by_name[template.short_name]

        response = client.create_service_definition(
            template.to_cmp_service_definition(module_id)
        )

        created_response = response.json()

        service_definitions_by_name[created_response["name"]] = created_response["id"]
        service_definition_ids.append(
            created_response["id"]
        )

    catalog = client.get_service_catalog().json()
    for service_definition_id in service_definition_ids:
        if service_definition_id not in catalog["service_defs"]:
            catalog["service_defs"].append(service_definition_id)

    client.update_service_catalog(catalog)

    print "Done."
