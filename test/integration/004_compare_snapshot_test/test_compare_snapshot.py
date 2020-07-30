from test.integration.base import DBTIntegrationTest
import os


class CompareTest(DBTIntegrationTest):
    @property
    def project_config(self):
        return {
            "config-version": 2,
            "data-paths": [
                os.path.relpath(self.test_path + "/data", self.dbt_config_dir)
            ],
            "snapshot-paths": [
                os.path.relpath(self.test_path + "/snapshots", self.dbt_config_dir)
            ],
            "snapshots": {"+target_schema": self.test_schema_name},
        }

    def test_compare_archive(self):

        self.run_dbt(["seed"])
        self.run_dbt(["snapshot"])
        results = self.run_dbthelper(["compare"])
        table_names = [x.table for x in results]
        self.assertFalse("seed_snapshot" in table_names)
