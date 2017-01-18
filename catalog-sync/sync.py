#!../env/bin/python

"""
Scans the rancher community catalog, creating corresponding entries
in the CMP service catalog.

For now, all this script does is clone the community catalog
and enumerate its contents.
"""

import os
import shutil
import requests

from git import Repo
from os import path
from template import CatalogTemplate

print "Purging local catalog (if present)..."

catalog_repo_dir = path.join(
    path.dirname(__file__),
    "repo"
)
shutil.rmtree(catalog_repo_dir, ignore_errors=True)

print "Cloning catalog repository..."

Repo.clone_from(
    url='https://github.com/rancher/community-catalog.git',
    to_path=catalog_repo_dir
)

print "Scanning catalog..."

templates_dir = path.join(catalog_repo_dir, "templates")
templates = [
    CatalogTemplate(
        path.join(templates_dir, template_dir)
    )
    for template_dir in os.listdir(templates_dir)
]

for template in templates:
    print("[{}] {}".format(
        template.category,
        template.name
    ))

print "Done."
