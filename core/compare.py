from dbt.compilation import Compiler
from dbt.config import RuntimeConfig
import dbt.adapters.factory
from dbt.node_types import NodeType

from dbt.utils import is_enabled as check_is_enabled
import dbt.loader
import dbt.ui
from dbt.logger import GLOBAL_LOGGER as logger


class CompareTask:
    def __init__(self, args):
        self.args = args
        self.config = RuntimeConfig.from_args(args)

    def _get_manifest(self):
        compiler = Compiler(self.config)
        compiler.initialize()

        all_projects = compiler.get_all_projects()

        manifest = dbt.loader.GraphLoader.load_all(self.config, all_projects)
        return manifest

    def run(self):

        # Look up all of the relations in the DB
        adapter = dbt.adapters.factory.get_adapter(self.config)
        manifest = self._get_manifest()

        checked_schemas = manifest.get_used_schemas()

        db_relations = []
        for schema in checked_schemas:
            db_relations.extend(adapter.list_relations(schema))

        database_relations = set()
        database_relations_map = dict()
        for relation in db_relations:
            relation_id = (relation.schema.lower(), relation.identifier.lower())
            database_relations_map[relation_id] = relation
            database_relations.add(relation_id)

        logger.info(
            "Comparing local models to the database catalog. " "Checking schemas:"
        )
        for schema_name in checked_schemas:
            logger.info("- {}".format(schema_name))

        # Look up all of the relations dbt knows about
        model_relations = set()
        for node in manifest.nodes.values():
            node = node.to_dict()
            is_refable = node["resource_type"] in NodeType.refable() or node["resource_type"] == 'archive'
            is_enabled = check_is_enabled(node)
            is_ephemeral = node["config"]["materialized"] == "ephemeral"
            if is_refable and is_enabled and not is_ephemeral:
                rel = (node["schema"].lower(), node["alias"].lower())
                model_relations.add(rel)

        problems = database_relations - model_relations

        if len(problems) == 0:
            logger.info(
                dbt.ui.printer.green(
                    "All clear! There are no relations in the checked schemas in the database"
                    "that are not defined in dbt models."
                )
            )
        else:
            logger.info(
                dbt.ui.printer.yellow(
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
