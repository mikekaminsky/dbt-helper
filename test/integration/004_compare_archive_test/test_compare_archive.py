from test.integration.base import DBTIntegrationTest


class CompareTest(DBTIntegrationTest):
    @property
    def project_config(self):
        source_table = "seed"

        return {
            "archive": [
                {
                    "source_schema": self.test_schema_name,
                    "target_schema": self.test_schema_name,
                    "tables": [
                        {
                            "source_table": source_table,
                            "target_table": "archive_actual",
                            "updated_at": '"updated_at"',
                            "unique_key": '''"id" || '-' || "first_name"''',
                        }
                    ],
                }
            ]
        }

    def test_compare_archive(self):

        with open("test/integration/004_compare_archive_test/seed.sql", "r") as f:
            seed = f.read()

        self.run_sql("CREATE SCHEMA {}".format(self.test_schema_name))
        self.run_sql(seed.format(schema=self.test_schema_name))
        self.run_dbt(["archive"])
        results = self.run_dbthelper(["compare"])
        table_names = [x.table for x in results]
        self.assertFalse("archive_actual" in table_names)
