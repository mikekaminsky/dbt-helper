import os
import json

from dbt.config import RuntimeConfig

COMPILED_DIR = "compiled"
RUN_DIR = "run"
MANIFEST_FILE = "manifest.json"
DEFAULT_OPEN_COMMAND = "open"
COMPILATION_MESSAGE = "You may need to run dbt compile first."


class FindTask:
    def __init__(self, args):
        self.args = args
        self.config = RuntimeConfig.from_args(args)
        self.model_path = self.config.source_paths[0]
        self.target_path = self.config.target_path
        self.manifest = self._get_manifest()

    def _get_manifest(self):
        """
        This subcommand uses the manifest file, whereas other subcommands import
        the manifest object from dbt (which requires the project to be parsed).
        Using the manifest file is significantly faster, so is preferred in this
        case.
        """
        manifest_path = os.path.join(self.target_path, MANIFEST_FILE)
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            return manifest
        except IOError:
            raise Exception(
                "Could not find {} file. {}".format(MANIFEST_FILE, COMPILATION_MESSAGE)
            )

    def _get_model_files(self):
        """ Return a dictionary of the form:
        {
            'source': 'models/path/to/model',
            'compiled': 'target/compiled/path/to/model',
            'run': 'target/run/path/to/model'
        }
        """

        file_names = {}
        for node in self.manifest["nodes"].values():
            if (
                node["resource_type"] == "model"
                and node["name"] == self.args.model_name
            ):
                root_path = node["root_path"]
                original_file_path = node["original_file_path"]
                package_name = node["package_name"]

                file_names["source"] = os.path.join(root_path, original_file_path)

                file_names["compiled"] = os.path.join(
                    self.target_path, COMPILED_DIR, package_name, original_file_path
                )

                file_names["run"] = os.path.join(
                    self.target_path, RUN_DIR, package_name, original_file_path
                )

        return file_names

    def run(self):

        model_files = self._get_model_files()

        if model_files == {}:
            raise Exception(
                "Could not find a model '{}'. {}".format(
                    self.args.model_name, COMPILATION_MESSAGE
                )
            )

        file_to_open = model_files.get(self.args.code_type)
        if not os.path.isfile(file_to_open):
            raise Exception(
                "Could not find a file '{}'. {}".format(
                    file_to_open, COMPILATION_MESSAGE
                )
            )

        print(file_to_open)

        return file_to_open
