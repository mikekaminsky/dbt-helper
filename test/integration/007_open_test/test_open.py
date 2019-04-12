from test.integration.base import DBTIntegrationTest


class OpenTest(DBTIntegrationTest):
    """
    Want to test that this works for each file type, and for installed packages
    """

    @property
    def models(self):
        return "test/integration/007_open_test/models"

    @property
    def packages_config(self):
        return {
            "packages": [{"local": "test/integration/007_open_test/local_dependency"}]
        }

    def check_model_file_opened(self, args):
        result = self.run_dbthelper(["open"] + args)
        return result == 0

    def test_open(self):
        self.run_dbt(["deps"])
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_opened(["my_model"]))
        self.assertTrue(self.check_model_file_opened(["my_model", "--compiled"]))
        self.assertTrue(self.check_model_file_opened(["my_model", "--run"]))
        self.assertTrue(self.check_model_file_opened(["my_model", "--source"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model", "-c"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model", "-r"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model", "-s"]))
