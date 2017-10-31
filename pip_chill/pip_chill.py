# -*- coding: utf-8 -*-
"""Lists installed packages that are not dependencies of others"""

import pip

from .utils import Distribution
from pip.utils import dist_is_editable
from pip.vcs import vcs, get_src_requirement
import os

def chill(show_all=False):
    if show_all:
        ignored_packages = ()
    else:
        ignored_packages = {
            'pip', 'pip-chill', 'wheel', 'setuptools', 'pkg-resources'}

    # Gather all packages that are requirements and will be auto-installed.
    distributions = {}
    dependencies = {}

    for distribution in pip.get_installed_distributions():
        if distribution.key in ignored_packages:
            continue

        editable = False
        vcs_loc = None

        if distribution.key in dependencies:
            dependencies[distribution.key].version = distribution.version
        else:
            location = os.path.normcase(os.path.abspath(distribution.location))
            if dist_is_editable(distribution) and vcs.get_backend_name(location):
                vcs_loc = get_src_requirement(distribution, location)
                editable = True

            distributions[distribution.key] = \
                Distribution(distribution.key, distribution.version, editable=editable, vcs=vcs_loc)

        for requirement in distribution.requires():
            if requirement.key not in ignored_packages:
                if requirement.key in dependencies:
                    dependencies[requirement.key] \
                        .required_by.add(distribution.key)
                else:
                    dependencies[requirement.key] = Distribution(
                        requirement.key,
                        required_by=(distribution.key,),
                        editable=editable, 
                        vcs=vcs_loc
                    )

            if requirement.key in distributions:
                dependencies[requirement.key].version \
                    = distributions.pop(requirement.key).version

    return sorted(distributions.values()), sorted(dependencies.values())
