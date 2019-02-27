from test.integration.base import DBTIntegrationTest
import os


class CompareTest(DBTIntegrationTest):
    def create_model(self, materialization):
        model = """
            {{{{ config(materialized='{mat}') }}}} SELECT 1 AS colname
            """.format(
            mat=materialization
        )

        file_path = os.path.join(self.models_path, "test_view.sql")
        with open(file_path, "w") as f:
            f.write(model)

    def get_created_models(self):
        relations = self.adapter.list_relations_without_caching(self.unique_schema())
        created_models = [rel.table.lower() for rel in relations]
        return created_models

    def check_relation_exists(self, relname):
        exists_q = """ SELECT EXISTS (
           SELECT 1
           FROM   pg_catalog.pg_class c
           JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace
           WHERE  n.nspname = '{schema}'
           AND    c.relname = '{table}'
           )
           """.format(
            schema=self.test_schema_name, table=relname
        )

        result = self.run_sql(exists_q, fetch="one")[0]
        return result

    def compare_switch_to_ephemeral(self):

        # Run dbt with test_view as a view
        self.create_model("view")
        self.run_dbt(["run"])

        # Assert the view exists in the database
        self.assertTrue(self.check_relation_exists("test_view"))
        self.assertTrue(self.check_relation_exists("downstream"))

        # Assert dbt compare passes
        results = self.run_dbthelper(["compare"])
        self.assertTrue(len(results) == 0)

        # Run dbt with test_view as ephemeral
        self.create_model("ephemeral")
        self.run_dbt(["run"])
        # Assert the view still exists in the database
        self.assertTrue(self.check_relation_exists("test_view"))
        self.assertTrue(self.check_relation_exists("downstream"))
        # Assert dbt compare fails
        results = self.run_dbthelper(["compare"])
        self.assertTrue(len(results) == 1)

    def test__postgres__compare(self):
        self.compare_switch_to_ephemeral()
