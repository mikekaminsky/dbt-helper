from test.integration.base import DBTIntegrationTest


class SourceSchemaTest(DBTIntegrationTest):
    def test_dependencies(self):
        self.run_dbt(["run"])
        results = self.run_dbthelper(["show_upstream", "d"])
        self.assertTrue(len(results) == 5)
        results = self.run_dbthelper(["show_downstream", "d"])
        self.assertTrue(len(results) == 1)
        results = self.run_dbthelper(["show_upstream", "c"])
        self.assertTrue(len(results) == 4)
        results = self.run_dbthelper(["show_downstream", "c"])
        self.assertTrue(len(results) == 2)

    def test_compare(self):
        self.run_dbt(["run"])
        results = self.run_dbthelper(["compare"])
        self.assertTrue(len(results) == 0)
