import os
import sys
from setuptools import find_packages, setup
from setuptools.command.install import install


package_name = "dbt-helper"
VERSION = "0.5.0"
description = """dbt-helper is a command line tool to help ease dbt development and database management"""


class VerifyVersionCommand(install):
    """
    Custom command to verify that the git tag matches our version
    https://circleci.com/blog/continuously-deploying-python-packages-to-pypi-with-circleci/
    """

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CIRCLE_TAG")

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setup(
    name=package_name,
    version=VERSION,
    description=description,
    author="Michael Kaminsky",
    author_email="michael@kaminsky.rocks",
    url="https://github.com/mikekaminsky/dbt-helper",
    packages=find_packages(),
    package_data={},
    test_suite="test",
    entry_points={"console_scripts": ["dbt-helper = core.main:main"]},
    scripts=[],
    install_requires=["dbt"],
    cmdclass={"verify": VerifyVersionCommand},
)
