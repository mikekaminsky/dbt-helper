from test.integration.base import DBTIntegrationTest


class DependencyTest(DBTIntegrationTest):
    def test_dependencies(self):
        self.run_dbt(["run"])
        results = self.run_dbthelper(["show_upstream", "d"])
        self.assertTrue(len(results) == 4)
        results = self.run_dbthelper(["show_downstream", "d"])
        self.assertTrue(len(results) == 1)
        results = self.run_dbthelper(["show_upstream", "c"])
        self.assertTrue(len(results) == 3)
        results = self.run_dbthelper(["show_downstream", "c"])
        self.assertTrue(len(results) == 2)

    def test_bad_model_arg(self):
        self.run_dbt(["run"])
        results = self.run_dbthelper(["show_downstream", "non_existent_model"])
        self.assertTrue(len(results) == 0)
