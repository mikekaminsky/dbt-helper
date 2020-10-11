import argparse
import sys
import os

import core.bootstrap as bootstrap_task
import core.compare as compare_task
import core.show_dependencies as show_dependencies_task
import core.open as open_task
import core.find as find_task
import core.retry_failed as retry_failed_task

import utils.ui
from utils.logging import logger

from dbt.config import PROFILES_DIR
from dbt.version import get_installed_version


def get_nearest_project_dir():
    root_path = os.path.abspath(os.sep)
    cwd = os.getcwd()

    while cwd != root_path:
        project_file = os.path.join(cwd, "dbt_project.yml")
        if os.path.exists(project_file):
            return cwd
        cwd = os.path.dirname(cwd)

    return None


def test_dbt_version():
    # Test if the dbt version is compatible with this version of dbt-helper
    installed_version = get_installed_version()

    VERSION_INCOMPATIBILITY_MSG = """
        Installed dbt version: {}
        dbt-helper requires dbt version 0.17.X or higher.
        You can find upgrade instructions here:
        https://docs.getdbt.com/docs/installation
    """.format(
        installed_version.to_version_string(skip_matcher=True)
    )

    if int(get_installed_version().minor) < 17:
        print(VERSION_INCOMPATIBILITY_MSG)
        sys.exit(1)


def parse_args(args):

    p = argparse.ArgumentParser(
        prog="dbt-helper: additional tools for working with DBT",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Additional CLI tools for faster DBT development and database management",
        epilog="Select one of these sub-commands and you can find more help from there.",
    )

    base_subparser = argparse.ArgumentParser(add_help=False)
    base_subparser.add_argument(
        "--profiles-dir",
        default=PROFILES_DIR,
        type=str,
        help="""
        Which directory to look in for the profiles.yml file. Default = {}
        """.format(
            PROFILES_DIR
        ),
    )
    base_subparser.add_argument(
        "--project-dir",
        help="Project directory specification",
    )
    base_subparser.add_argument(
        "--profile",
        required=False,
        type=str,
        help="""
        Which profile to load. Overrides setting in dbt_project.yml.
        """,
    )
    base_subparser.add_argument(
        "--target",
        default=None,
        type=str,
        help="Which target to load for the given profile",
    )

    subs = p.add_subparsers(title="Available sub-commands", dest="command")

    compare_sub = subs.add_parser(
        "compare",
        parents=[base_subparser],
        help="Compare your dbt project specifications with what's in your database.",
    )
    compare_sub.set_defaults(cls=compare_task.CompareTask, which="compare")

    bootstrap_sub = subs.add_parser(
        "bootstrap",
        parents=[base_subparser],
        help="Bootstrap schema.yml files from database catalog",
    )
    bootstrap_sub.set_defaults(cls=bootstrap_task.BootstrapTask, which="bootsrap")

    bootstrap_sub.add_argument(
        "--schemas",
        required=True,
        nargs="+",
        help="""
        Required. Specify the schemas to inspect when bootstrapping
        schema.yml files.
        """,
    )
    bootstrap_sub.add_argument(
        "--single-file",
        action="store_true",
        dest="single_file",
        help="Store all of the schema information in a single schema.yml file",
    )
    bootstrap_sub.add_argument(
        "--write-files",
        action="store_true",
        dest="write_files",
        help="Create schema.yml files (will not over-write existing files).",
    )

    upstream_depencies_sub = subs.add_parser(
        "show-upstream",
        parents=[base_subparser],
        help="Show upstream dependencies for a model",
    )
    upstream_depencies_sub.set_defaults(
        cls=show_dependencies_task.ShowDependenciesTask, which="show-upstream"
    )
    upstream_depencies_sub.add_argument("model_name")

    downstream_depencies_sub = subs.add_parser(
        "show-downstream",
        aliases=["show_downstream"],
        parents=[base_subparser],
        help="Show downstream dependencies for a model",
    )
    downstream_depencies_sub.set_defaults(
        cls=show_dependencies_task.ShowDependenciesTask, which="show-downstream"
    )
    downstream_depencies_sub.add_argument("model_name")

    find_sub = subs.add_parser(
        "find",
        parents=[base_subparser],
        help="Find the source/compiled/run file for a model",
    )
    find_sub.set_defaults(cls=find_task.FindTask, which="find", code_type="compiled")

    open_sub = subs.add_parser(
        "open",
        parents=[base_subparser],
        help="Open the source/compiled/run file for a model",
    )
    open_sub.set_defaults(cls=open_task.OpenTask, which="open", code_type="compiled")

    for subparser in [find_sub, open_sub]:

        subparser.add_argument("model_name", help="The name of the model to open")

        code_type = subparser.add_mutually_exclusive_group()

        code_type.add_argument(
            "--source",
            "-s",
            action="store_const",
            const="source",
            dest="code_type",
            help="""
                Open the raw jinja-flavored SELECT statement, from the models/
                directory.""",
        )

        code_type.add_argument(
            "--compiled",
            "-c",
            action="store_const",
            const="compiled",
            dest="code_type",
            help="""
                Open the compiled SELECT statement, from the target/compiled
                directory. This is the default behavior.""",
        )
        code_type.add_argument(
            "--run",
            "-r",
            action="store_const",
            const="run",
            dest="code_type",
            help="""
                Open the compiled model wrapped in the appropriate DDL (i.e. CREATE
                statements), from the target/run directory.""",
        )

    retry_failed_sub = subs.add_parser(
        "retry-failed",
        parents=[base_subparser],
        help="""Rerun the models that failed or were skipped on the previous run.""",
    )

    retry_failed_sub.set_defaults(
        cls=retry_failed_task.RetryFailedTask, which="retry-failed"
    )

    if len(args) == 0:
        p.print_help()
        sys.exit(1)
        return

    parsed = p.parse_args(args)
    return parsed


def handle(args):

    nearest_project_dir = get_nearest_project_dir()
    if nearest_project_dir is None:
        raise Exception(
            "fatal: Not a dbt project (or any of the parent directories). "
            "Missing dbt_project.yml file"
        )

    os.chdir(nearest_project_dir)

    parsed = parse_args(args)
    results = None

    if parsed.command == "bootstrap":
        task = bootstrap_task.BootstrapTask(parsed)
        results = task.run()

    if parsed.command == "compare":
        task = compare_task.CompareTask(parsed)
        results = task.run()

    if parsed.command in ("show_upstream", "show_downstream"):
        logger.info(
            utils.ui.yellow(
                "Deprecation Warning: \n"
                "show_upstream and show_downstream will be deprecated in \n"
                "a future version of dbt-helper in favor of the more \n"
                "consistent show-upstream and show-downstream syntax."
            )
        )
        if parsed.command == "show_upstream":
            parsed.command = "show-upstream"
        else:
            parsed.command = "show-downstream"

    if parsed.command in ("show-upstream", "show-downstream"):
        task = show_dependencies_task.ShowDependenciesTask(parsed)
        results = task.run(parsed)

    if parsed.command == "find":
        task = find_task.FindTask(parsed)
        results = task.run()

    if parsed.command == "open":
        task = open_task.OpenTask(parsed)
        results = task.run()

    if parsed.command == "retry-failed":
        task = retry_failed_task.RetryFailedTask(parsed)
        results = task.run()

    return results


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    test_dbt_version()

    handle(args)
