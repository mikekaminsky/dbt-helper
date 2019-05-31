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

        if args[0] == "my_model":
            c_location = "test/"
        elif args[0] == "my_package_model":
            c_location = "local_dep/"

        path = "target/compiled/" + c_location

        if len(args) > 1:
            if args[1] in ("--run", "-r"):
                path = "target/run/" + c_location
            if args[1] in ("--source", "-s"):
                path = self.models + "/"

        correct_path = path + args[0] + ".sql"

        return result == correct_path

    def test_open(self):
        self.run_dbt(["deps"])
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_opened(["my_model"]))
        self.assertTrue(self.check_model_file_opened(["my_model", "--compiled"]))
        self.assertTrue(self.check_model_file_opened(["my_model", "--run"]))
        self.assertTrue(self.check_model_file_opened(["my_model", "--source"]))
        self.assertTrue(self.check_model_file_opened(["my_model", "--print"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model", "-c"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model", "-r"]))
        self.assertTrue(self.check_model_file_opened(["my_package_model", "-p"]))
        # self.assertTrue(self.check_model_file_opened(["my_package_model", "-s"]))
