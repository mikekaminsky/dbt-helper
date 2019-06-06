from test.integration.base import DBTIntegrationTest
import os
from core.main import get_nearest_project_dir


class OpenFindTest(DBTIntegrationTest):
    """
    Test that open and find work for each file type, and for installed packages
    """

    @property
    def models(self):
        return "test/integration/007_open_find_test/models"

    @property
    def packages_config(self):
        return {
            "packages": [
                {"local": "test/integration/007_open_find_test/local_dependency"},
                {
                    "git": "https://github.com/fishtown-analytics/dbt-integration-project",
                    "revision": "master",
                },
            ]
        }

    def check_model_file_path(self, command, args):

        # Change directory to make sure relative paths still work
        os.chdir("test/integration/007_open_find_test")
        result = self.run_dbthelper([command] + args)

        model_name = args[0]
        if len(args) > 1:
            code_type = args[1]
        else:
            code_type = "NA"

        if model_name == "my_model":
            c_location = "test/"
        elif model_name == "my_package_model":
            c_location = "local_dep/"
        elif model_name == "incremental":
            c_location = "dbt_integration_project/"

        path = "target/compiled/" + c_location

        if code_type in ("--run", "-r"):
            path = "target/run/" + c_location
        if code_type in ("--source", "-s"):
            path = get_nearest_project_dir() + "/" + self.models + "/"

        correct_path = path + model_name + ".sql"

        # Have to special-case these
        if model_name == "my_package_model" and code_type in ("-s", "--source"):
            correct_path = (
                get_nearest_project_dir()
                + "/"
                + "dbt_modules/local_dep/models/my_package_model.sql"
            )
        if model_name == "incremental" and code_type in ("-s", "--source"):
            correct_path = (
                get_nearest_project_dir()
                + "/"
                + "dbt_modules/dbt_integration_project/models/incremental.sql"
            )

        return result == correct_path

    def test_open_compiled(self):
        self.run_dbt(["deps"])
        # This will cause errors that we can ignore from the integration package
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_path("open", ["my_model"]))
        self.assertTrue(self.check_model_file_path("open", ["my_model", "--compiled"]))
        self.assertTrue(self.check_model_file_path("open", ["my_package_model"]))
        self.assertTrue(self.check_model_file_path("open", ["my_package_model", "-c"]))
        self.assertTrue(self.check_model_file_path("open", ["incremental"]))
        self.assertTrue(self.check_model_file_path("open", ["incremental", "-c"]))

    def test_open_run(self):
        self.run_dbt(["deps"])
        # This will cause errors that we can ignore from the integration package
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_path("open", ["my_model", "--run"]))
        self.assertTrue(self.check_model_file_path("open", ["my_package_model", "-r"]))
        self.assertTrue(self.check_model_file_path("open", ["incremental", "-r"]))

    def test_open_source(self):
        self.run_dbt(["deps"])
        # This will cause errors that we can ignore from the integration package
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_path("open", ["my_model", "--source"]))
        self.assertTrue(self.check_model_file_path("open", ["my_package_model", "-s"]))
        self.assertTrue(self.check_model_file_path("open", ["incremental", "-s"]))

    def test_find_compiled(self):
        self.run_dbt(["deps"])
        # This will cause errors that we can ignore from the integration package
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_path("find", ["my_model"]))
        self.assertTrue(self.check_model_file_path("find", ["my_model", "--compiled"]))
        self.assertTrue(self.check_model_file_path("find", ["my_package_model"]))
        self.assertTrue(self.check_model_file_path("find", ["my_package_model", "-c"]))
        self.assertTrue(self.check_model_file_path("find", ["incremental"]))
        self.assertTrue(self.check_model_file_path("find", ["incremental", "-c"]))

    def test_find_run(self):
        self.run_dbt(["deps"])
        # This will cause errors that we can ignore from the integration package
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_path("find", ["my_model", "--run"]))
        self.assertTrue(self.check_model_file_path("find", ["my_package_model", "-r"]))
        self.assertTrue(self.check_model_file_path("find", ["incremental", "-r"]))

    def test_find_source(self):
        self.run_dbt(["deps"])
        # This will cause errors that we can ignore from the integration package
        self.run_dbt(["run"])

        self.assertTrue(self.check_model_file_path("find", ["my_model", "--source"]))
        self.assertTrue(self.check_model_file_path("find", ["my_package_model", "-s"]))
        self.assertTrue(self.check_model_file_path("find", ["incremental", "-s"]))
