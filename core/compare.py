from dbt.config import RuntimeConfig
import dbt.adapters.factory
from dbt.node_types import NodeType

import dbt.perf_utils
import utils.ui
from utils.logging import logger


class CompareTask:
    def __init__(self, args):
        self.args = args
        self.config = RuntimeConfig.from_args(args)

    def _get_manifest(self):
        manifest = dbt.perf_utils.get_full_manifest(self.config)
        return manifest

    def run(self):

        # Look up all of the relations in the DB
        dbt.adapters.factory.register_adapter(self.config)
        adapter = dbt.adapters.factory.get_adapter(self.config)
        self.adapter_type = adapter.type()
        manifest = self._get_manifest()

        schemas = set()
        model_relations = set()
        # Look up all of the relations dbt knows about
        for node in manifest.nodes.values():
            if node.resource_type != "source":
                schema_info = (node.database, node.schema)
                schemas.update([schema_info])
                node = node.to_dict()
                is_refable = node["resource_type"] in NodeType.refable()
                is_enabled = node["config"]["enabled"]
                is_ephemeral = node["config"]["materialized"] == "ephemeral"
                if is_refable and is_enabled and not is_ephemeral:
                    rel = (node["schema"].lower(), node["alias"].lower())
                    model_relations.add(rel)

        db_relations = []
        for database_name, schema_name in schemas:
            db_relations.extend(adapter.list_relations(database_name, schema_name))

        database_relations = set()
        database_relations_map = dict()
        for relation in db_relations:
            relation_id = (relation.schema.lower(), relation.identifier.lower())
            database_relations_map[relation_id] = relation
            database_relations.add(relation_id)

        logger.info(
            "Comparing local models to the database catalog. " "Checking schemas:"
        )
        for database_name, schema_name in schemas:
            logger.info("- {}".format(schema_name))

        problems = database_relations - model_relations

        if len(problems) == 0:
            logger.info(
                utils.ui.green(
                    "All clear! There are no relations in the checked schemas in the database"
                    "that are not defined in dbt models."
                )
            )
        else:
            logger.info(
                utils.ui.yellow(
                    "Warning: The following relations do not match any models "
                    "found in this project:"
                )
            )

        problem_relation_list = []  # Get a list of relations to return

        for relation_id in problems:
            relation = database_relations_map[relation_id]
            problem_relation_list.append(relation)
            logger.info("{} {}".format(relation.type.upper(), relation))
            # TODO: Fix this so that it doesn't break when type is None
            # logger.info("{} {}".format(relation.type, relation))

        return problem_relation_list

    def interpret_results(self, results):
        return len(results) == 0
