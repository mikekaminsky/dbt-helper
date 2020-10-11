import os
from datetime import datetime

from dbt.config import RuntimeConfig
import dbt.adapters.factory

import dbt.perf_utils
import utils.ui
from utils.logging import logger
from dbt.task.generate import Catalog, CatalogResults
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
        manifest = dbt.perf_utils.get_full_manifest(self.config)
        return manifest

    def render_relations(self, models):
        return SCHEMA_YML_TEMPLATE.render(models=models)

    def write_relation(self, design_file_path, yml):
        if os.path.isfile(design_file_path):
            logger.info(
                utils.ui.yellow(
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

    def generate_catalog_dict(self, manifest, columns):
        """
        Ported from
        https://github.com/fishtown-analytics/dbt/blob/dev/octavius-catto/test/unit/test_docs_generate.py
        """
        nodes, sources = Catalog(columns).make_unique_id_map(manifest)
        result = CatalogResults(
            nodes=nodes,
            sources=sources,
            generated_at=datetime.utcnow(),
            errors=None,
        )
        return result.to_dict(omit_none=False)["nodes"]

    def run(self):
        single_file = self.args.single_file
        write_files = self.args.write_files
        schemas = self.args.schemas

        logger.info("Bootstrapping the following schemas:")
        for schema in schemas:
            logger.info("- {}".format(schema))

        # Look up all of the relations in the DB
        dbt.adapters.factory.register_adapter(self.config)
        adapter = dbt.adapters.factory.get_adapter(self.config)
        self.adapter_type = adapter.type()
        self.adapter = adapter
        manifest = self._get_manifest()
        all_relations, exceptions = adapter.get_catalog(manifest)

        selected_relations = all_relations.where(
            lambda row: row["table_schema"] in schemas
        )

        zipped_relations = [
            dict(zip(selected_relations.column_names, row))
            for row in selected_relations
        ]

        relations_to_design = self.generate_catalog_dict(manifest, zipped_relations)

        if len(relations_to_design) == 0:
            logger.info(
                utils.ui.yellow(
                    "Warning: No relations found in selected schemas: {}."
                    "\nAborting.".format(schemas)
                )
            )
            return {}

        for table_id, relations in relations_to_design.items():
            all_models = []

            schema = relations["metadata"]["schema"]
            schema_path = os.path.join(self.config.source_paths[0], schema)
            if not write_files:
                pass
            elif os.path.isdir(schema_path):
                pass
            else:
                os.mkdir(schema_path)

            relation = relations["metadata"]["name"]

            relation_dict = self.prep_metadata(relations)
            all_models.append(relation_dict)

            if not single_file:
                if not write_files:
                    logger.info("-" * 20)
                    logger.info("Design for relation: {}.{}".format(schema, relation))
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
