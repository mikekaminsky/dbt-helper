import os
from test.integration.base import DBTIntegrationTest


class TestBootstrap(DBTIntegrationTest):
    def tearDown(self):
        for path, subdirs, files in os.walk(self.models_path):
            for name in files:
                if name.endswith(".yml"):
                    os.remove(os.path.join(path, name))

        super(TestBootstrap, self).tearDown()

    def model_file_path(self, *args):
        return os.path.join(self.models_path, *args)

    def test_bootstrap_doesnt_write(self):
        self.run_dbt(["run"])
        self.run_dbthelper(["bootstrap", "--schemas", self.test_schema_name])

        self.assertFalse(
            os.path.isfile(
                self.model_file_path(self.test_schema_name, "downstream.yml")
            )
        )
        self.assertFalse(
            os.path.isfile(self.model_file_path(self.test_schema_name, "test_view.yml"))
        )

    def test_bootstrap_write(self):
        self.run_dbt(["run"])
        self.run_dbthelper(
            ["bootstrap", "--schemas", self.test_schema_name, "--write-files"]
        )

        self.assertTrue(
            os.path.isfile(
                self.model_file_path(self.test_schema_name, "downstream.yml")
            )
        )
        self.assertTrue(
            os.path.isfile(self.model_file_path(self.test_schema_name, "test_view.yml"))
        )

    def test_late_binding_view(self):
        pass
