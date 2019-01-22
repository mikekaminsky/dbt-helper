import os
from test.integration.base import DBTIntegrationTest
from core.main import handle


class TestBootstrap(DBTIntegrationTest):

    def tearDown(self):
        for path, subdirs, files in os.walk(self.models_path):
            for name in files:
                if name.endswith(".yml"):
                    os.remove(os.path.join(path, name))

    def model_file_path(self, *args):
        return os.path.join(self.models_path, *args)

    def test_bootstrap_completeness(self):
        self.run_dbt(["run"])
        results = handle(["bootstrap", '--schemas', self.test_schema_name])

        self.assertTrue(os.path.isfile(self.model_file_path(self.test_schema_name, 'downstream.yml')))
        self.assertTrue(os.path.isfile(self.model_file_path(self.test_schema_name, 'test_view.yml')))

    def test_late_binding_view(self):
        pass
