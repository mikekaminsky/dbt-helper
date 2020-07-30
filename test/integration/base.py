import unittest
from dbt.adapters.factory import get_adapter, register_adapter
from dbt.config import RuntimeConfig
from dbt.main import handle_and_check
from dbt.logger import log_manager
import sys
import os
import yaml
from core.main import handle
import shutil

IS_DOCKER = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)


class TestArgs(object):
    def __init__(self, kwargs):
        self.which = "run"
        self.single_threaded = False
        self.profiles_dir = os.getcwd()
        self.project_dir = None
        self.__dict__.update(kwargs)


class DBTIntegrationTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DBTIntegrationTest, self).__init__(*args, **kwargs)

        self.run_dir = os.getcwd()

        self.test_schema_name = "my_test_schema"
        if IS_DOCKER:
            dbt_config_dir = os.path.abspath(
                os.path.expanduser(
                    os.environ.get("DBT_CONFIG_DIR", "/home/dbt_test_user/.dbt")
                )
            )
        else:
            dbt_config_dir = self.run_dir

        self.dbt_config_dir = dbt_config_dir
        self.dbt_profile = os.path.join(self.dbt_config_dir, "profiles.yml")

    def setUp(self):
        self.use_profile()
        self.use_default_project()
        self.set_packages()
        self.load_config()

    def tearDown(self):

        self.load_config()  # Re-set the connection
        self.run_sql('DROP SCHEMA IF EXISTS "{}" CASCADE'.format(self.test_schema_name))

        if os.path.exists("dbt_project.yml"):
            os.remove("dbt_project.yml")
        if os.path.exists("packages.yml"):
            os.remove("packages.yml")
        if os.path.exists("profiles.yml"):
            os.remove("profiles.yml")
        if os.path.exists("dbt_modules"):
            shutil.rmtree("dbt_modules")

    @property
    def project_config(self):
        return {
            "config-version": 2,
        }

    @property
    def packages_config(self):
        return None

    @property
    def test_path(self):
        path = sys.modules[self.__module__].__file__
        path = os.path.split(path)[0]
        return path

    @property
    def models_path(self, dirname="models"):
        return os.path.join(self.test_path, dirname)

    @property
    def rel_models_path(self):
        return os.path.relpath(self.models_path, self.run_dir)

    def postgres_profile(self):

        if IS_DOCKER:
            hostname = "database"
        else:
            hostname = "localhost"

        return {
            "config": {"send_anonymous_usage_stats": False},
            "test": {
                "outputs": {
                    "default2": {
                        "type": "postgres",
                        "threads": 4,
                        "host": "{}".format(hostname),
                        "port": 5432,
                        "user": "root",
                        "pass": "password",
                        "dbname": "dbt",
                        "schema": "{}".format(self.test_schema_name),
                    },
                    "noaccess": {
                        "type": "postgres",
                        "threads": 4,
                        "host": "{}".format(hostname),
                        "port": 5432,
                        "user": "noaccess",
                        "pass": "password",
                        "dbname": "dbt",
                        "schema": "{}".format(self.test_schema_name),
                    },
                },
                "target": "default2",
            },
        }

    def use_profile(self):
        if not os.path.exists(self.dbt_config_dir):
            os.makedirs(self.dbt_config_dir)

        profile_config = {}
        default_profile_config = self.postgres_profile()

        profile_config.update(default_profile_config)

        with open(self.dbt_profile, "w") as f:
            yaml.safe_dump(profile_config, f, default_flow_style=True)

        self._profile_config = profile_config

    def set_packages(self):
        if self.packages_config is not None:
            with open("packages.yml", "w") as f:
                yaml.safe_dump(self.packages_config, f, default_flow_style=True)

    def load_config(self):
        # we've written our profile and project. Now we want to instantiate a
        # fresh adapter for the tests.
        # it's important to use a different connection handle here so
        # we don't look into an incomplete transaction
        kwargs = {"profile": None, "profiles_dir": self.dbt_config_dir, "target": None}

        config = RuntimeConfig.from_args(TestArgs(kwargs))

        register_adapter(config)
        adapter = get_adapter(config)
        self.adapter_type = adapter.type()
        adapter.cleanup_connections()
        self.connection = adapter.acquire_connection("__test")
        self.adapter_type = self.connection.type
        self.adapter = adapter
        self.config = config

    def run_sql(self, sql, fetch="None"):

        if sql.strip() == "":
            return

        self.load_config()
        conn = self.connection
        with conn.handle.cursor() as cursor:
            try:
                cursor.execute(sql)
                conn.handle.commit()
                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "all":
                    return cursor.fetchall()
                else:
                    return
            except BaseException as e:
                conn.handle.rollback()
                print(sql)
                print(e)
                raise e

    def use_default_project(self, overrides=None):
        # create a dbt_project.yml
        base_project_config = {
            "name": "test",
            "version": "1.0",
            "test-paths": [],
            "source-paths": [self.rel_models_path],
            "profile": "test",
        }

        project_config = {}
        project_config.update(base_project_config)
        project_config.update(self.project_config)
        project_config.update(overrides or {})

        with open("dbt_project.yml", "w") as f:
            yaml.safe_dump(project_config, f, default_flow_style=True)

    def run_dbthelper(self, args):

        if args is None:
            args = []

        args.extend(["--profiles-dir", self.dbt_config_dir])
        results = handle(args)
        return results

    def run_dbt(self, args):
        if args is None:
            args = ["run"]

        log_manager.reset_handlers()

        args.extend(["--profiles-dir", self.dbt_config_dir])

        res, success = handle_and_check(args)

        return res, success
