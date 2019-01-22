from test.integration.base import DBTIntegrationTest
import os


class TestBootstrap(DBTIntegrationTest):

    def tearDown(self):
        files = os.listdir(self.models_path)
        for f in files:
            if f.endswith(".yml"):
                os.remove(self.model_file_path(f))

    def model_file_path(self, fname):
        return os.path.join(self.models_path,fname)

    def test_bootstrap_completeness(self):
        self.run_dbt(["run"])
        results = self.run_dbt(["bootstrap", '--schemas', self.test_schema_name])

        self.assertTrue(os.path.isfile(self.model_file_path('model_a.yml')))
        self.assertTrue(os.path.isfile(self.model_file_path('model_b.yml')))

    def test_late_binding_view(self):
        pass
