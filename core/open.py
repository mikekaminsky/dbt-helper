import os
import subprocess

from core.find import FindTask

COMPILED_DIR = "compiled"
RUN_DIR = "run"
MANIFEST_FILE = "manifest.json"
DEFAULT_OPEN_COMMAND = "open"
COMPILATION_MESSAGE = "You may need to run dbt compile first."


class OpenTask(FindTask):
    def __init__(self, args):
        FindTask.__init__(self, args)
        self.open_command = self._get_open_command()

    def _get_open_command(self):
        open_command = os.environ.get(
            "DBT_HELPER_EDITOR", os.environ.get("EDITOR", DEFAULT_OPEN_COMMAND)
        )
        return open_command

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

        result = subprocess.call(
            " ".join([self.open_command, file_to_open]), shell=True
        )
        if result == 0:
            print("Opened " + file_to_open)
        else:
            raise Exception(
                "Unsuccessfully tried to open a file using the '{}' command. "
                "You may need to update your $DBT_HELPER_EDITOR or $EDITOR "
                "environment variable.".format(self.open_command)
            )

        return file_to_open
