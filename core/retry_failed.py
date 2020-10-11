from dbt.config import RuntimeConfig

import os
import json
import subprocess

RUN_RESULTS_FILE = "run_results.json"


class RetryFailedTask:
    def __init__(self, args):
        self.args = args
        self.config = RuntimeConfig.from_args(args)
        self.target_path = self.config.target_path
        self.run_results = self._get_run_results()

    def _get_run_results(self):
        """
        This subcommand parses the results.json file
        """
        run_results_path = os.path.join(self.target_path, RUN_RESULTS_FILE)
        try:
            with open(run_results_path) as f:
                run_results = json.load(f)
            return run_results
        except IOError:
            raise Exception("Could not find {} file.".format(RUN_RESULTS_FILE))

    def get_models_to_retry(self):
        """Return a list of errored and skipped models"""
        models = []
        for result in self.run_results.get("results"):
            if result["status"] == "ERROR" or result["skip"]:
                models.append(result["node"]["name"])
        return models

    def get_run_flags(self):
        """This is a janky function that takes the args and puts them back
        into a list of strings."""
        flags = []
        if self.args.profiles_dir:
            flags.extend(["--profiles-dir", self.args.profiles_dir])
        if self.args.profile:
            flags.extend(["--profile", self.args.profile])
        if self.args.target:
            flags.extend(["--target", self.args.target])
        return flags

    def run(self):
        models_to_retry = self.get_models_to_retry()

        if models_to_retry == []:
            raise Exception("No models to rerun!")

        run_flags = self.get_run_flags()

        args = ["dbt run --models"]
        args.extend(models_to_retry)
        args.extend(run_flags)

        command = " ".join(args)

        print(command)
        subprocess.call(command, shell=True)

        return models_to_retry
