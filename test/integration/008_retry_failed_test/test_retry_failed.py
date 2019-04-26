from test.integration.base import DBTIntegrationTest


class RetryFailedTest(DBTIntegrationTest):
    @property
    def models(self):
        return "test/integration/008_retry_failed_test/models"

    def tests_retry_failed(self):
        try:
            self.run_dbt(["run"])
        except InvocationError:
            pass
        self.assertEqual(self.run_dbthelper(["retry-failed"]), ["my_failing_model", "my_skipped_model"])
