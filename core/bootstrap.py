import os

from dbt.compilation import Compiler
from dbt.config import RuntimeConfig
import dbt.adapters.factory

import dbt.loader
import dbt.ui
from dbt.logger import GLOBAL_LOGGER as logger
from dbt.task.generate import unflatten
from jinja2 import Template


SCHEMA_YML_TEMPLATE = Template(
    """
version: 2
models:
{% for model_dict in models %}
  - name: {{model_dict['name']}}
    description: 'TODO: Replace me'
    columns:
    {% for col in model_dict['columns'] -%}
    - name: {{col['name']}}
    {% endfor %}
    {% endfor %}
"""
)


class BootstrapTask:
    def __init__(self, args):
        self.args = args
        self.config = RuntimeConfig.from_args(args)

    def _get_manifest(self):
        compiler = Compiler(self.config)
        compiler.initialize()

        all_projects = compiler.get_all_projects()

        manifest = dbt.loader.GraphLoader.load_all(self.config, all_projects)
        return manifest

    def render_relations(self, models):
        return SCHEMA_YML_TEMPLATE.render(models=models)

    def write_relation(self, design_file_path, yml):
        if os.path.isfile(design_file_path):
            logger.info(
                dbt.ui.printer.yellow(
                    "Warning: File {} already exists. Skipping".format(design_file_path)
                )
            )
            return

        logger.info("Creating design file: {}".format(design_file_path))
        with open(design_file_path, "w") as f:
            f.write(yml)

    def print_relation(self, yml):
        logger.info(yml)

    def prep_metadata(self, meta_dict):
        columns = []
        for colname in meta_dict["columns"]:
            column = {}
            column["name"] = colname
            columns.append(column)

        model = {}
        model["name"] = meta_dict["metadata"]["name"]
        if meta_dict["metadata"]["comment"]:
            description = meta_dict["metadata"]["comment"]
        else:
            description = "TODO: Replace me"

        model["description"] = description
        model["columns"] = columns

        return model

    def run(self):
        single_file = self.args.single_file
        write_files = self.args.write_files
        schemas = self.args.schemas

        logger.info("Bootstrapping the following schemas:")
        for schema in schemas:
            logger.info("- {}".format(schema))

        # Look up all of the relations in the DB
        manifest = self._get_manifest()
        adapter = dbt.adapters.factory.get_adapter(self.config)
        all_relations = adapter.get_catalog(manifest)

        selected_relations = all_relations.where(
            lambda row: row["table_schema"] in schemas
        )

        zipped_relations = [
            dict(zip(selected_relations.column_names, row))
            for row in selected_relations
        ]

        relations_to_design = unflatten(zipped_relations)

        if len(relations_to_design) == 0:
            logger.info(
                dbt.ui.printer.yellow(
                    "Warning: No relations found in selected schemas: {}."
                    "\nAborting.".format(schemas)
                )
            )
            return {}

        for schema, relations in relations_to_design.items():
            schema_path = os.path.join(self.config.source_paths[0], schema)
            if not write_files:
                pass
            elif os.path.isdir(schema_path):
                pass
            else:
                os.mkdir(schema_path)

            all_models = []

            for relation, meta_data in relations.items():

                relation_dict = self.prep_metadata(meta_data)
                all_models.append(relation_dict)

                if not single_file:
                    if not write_files:
                        logger.info("-" * 20)
                        logger.info(
                            "Design for relation: {}.{}".format(schema, relation)
                        )
                        logger.info("-" * 20)
                        yml = self.render_relations([relation_dict])
                        self.print_relation(yml)
                    else:
                        design_file_name = "{}.yml".format(relation)
                        design_file_path = os.path.join(schema_path, design_file_name)
                        yml = self.render_relations([relation_dict])
                        self.write_relation(design_file_path, yml)

            if single_file:
                if not write_files:
                    logger.info("-" * 20)
                    logger.info("Design for schmea: {}".format(schema))
                    logger.info("-" * 20)
                    yml = self.render_relations(all_models)
                    self.print_relation(yml)

                else:
                    design_file_name = "{}.yml".format(schema)
                    design_file_path = os.path.join(schema_path, design_file_name)
                    yml = self.render_relations([all_models])
                    self.write_relation(design_file_path, yml)

        return all_models

    def interpret_results(self, results):
        return len(results) != 0
