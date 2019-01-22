from setuptools import find_packages, setup


package_name = "mkdbt"
package_version = "0.0.1"
description = """mkdbt is a command line tool to help ease dbt development and \
        database management"""


setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description_content_type=description,
    author="Michael Kaminsky",
    author_email="michael@kaminsky.rocks",
    url="https://github.com/mikekaminsky/mkdbt",
    packages=find_packages(),
    package_data={},
    test_suite="test",
    entry_points={"console_scripts": ["mkdbt = core.main:main"]},
    scripts=[],
    install_requires=["dbt"],
)
