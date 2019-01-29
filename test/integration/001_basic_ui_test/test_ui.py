import os
from test.integration.base import DBTIntegrationTest


class TestUi(DBTIntegrationTest):
    def test_works_from_any_subdirectory(self):
        os.chdir(self.models_path)
        results = self.run_dbthelper(["compare"])
        self.assertTrue(results is not None)
