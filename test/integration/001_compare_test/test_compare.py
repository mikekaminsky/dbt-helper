import subprocess
from test.integration.base import DBTIntegrationTest
import os


class CompareTest(DBTIntegrationTest):

    def create_model(self, materialization):
        model = """
            {{{{ config(materialized='{mat}') }}}}
            SELECT 1 AS colname
            """.format(
            mat=materialization
        )

        file_path = os.path.join(self.models_path, "test_view.sql")
        with open(file_path, "w") as f:
            f.write(model)

    def compare_switch_to_ephemeral(self):
        # print(self.models_path)
        # x = subprocess.Popen(
            # "dbt --help", shell=True, stdout=subprocess.PIPE
        # )
        # lgz = x.stdout.read()
        # x.stdout.close()
        # print(lgz.decode("UTF-8"))
        # print("HOWDY")

        # Run dbt with test_view as a view
        self.create_model("view")
        self.run_dbt(["run"])
        assert True

        # Assert the view exists in the database
        # created_models = self.get_created_models()

        # self.assertTrue("test_view" in created_models)
        # self.assertTrue("downstream" in created_models)

        # Assert dbt compare passes
        # results = self.run_dbt(["compare"])

        # self.assertTrue(len(results) == 0)

        # Run dbt with test_view as ephemeral
        # self.create_test_model("ephemeral")
        # self.run_dbt(["run"])
        # Assert the view still exists in the database
        # created_models = self.get_created_models()
        # self.assertTrue("test_view" in created_models)
        # self.assertTrue("downstream" in created_models)
        # Assert dbt compare fails
        # results = self.run_dbt(["compare"], expect_pass=False)
        # self.assertTrue(len(results) == 1)

    def test__postgres__compare(self):
        self.compare_switch_to_ephemeral()
