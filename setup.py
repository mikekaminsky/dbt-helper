from setuptools import find_packages, setup


package_name = "dbt-helper"
package_version = "0.0.2"
description = """dbt-helper is a command line tool to help ease dbt development and database management"""


setup(
    name=package_name,
    version=package_version,
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
)
