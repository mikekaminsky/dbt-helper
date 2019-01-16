import argparse
import sys

import core.bootstrap as bootstrap_task
import core.compare as compare_task

from collections import namedtuple
from dbt.config import RuntimeConfig, PROFILES_DIR
from dbt.compilation import Compiler
import dbt.adapters.factory



def parse_args(args):

    p = argparse.ArgumentParser(
        prog="mkdbt: additional tools for wokring with DBT",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Additional CLI tools for faster DBT development and database management",
        epilog="Select one of these sub-commands and you can find more help from there.",
    )

    base_subparser = argparse.ArgumentParser(add_help=False)
    base_subparser.add_argument(
        '--profiles-dir',
        default=PROFILES_DIR,
        type=str,
        help="""
        Which directory to look in for the profiles.yml file. Default = {}
        """.format(PROFILES_DIR)
    )
    base_subparser.add_argument(
        '--profile',
        required=False,
        type=str,
        help="""
        Which profile to load. Overrides setting in dbt_project.yml.
        """
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
        "--print-only",
        action="store_true",
        dest="print_only",
        help="Print generated yml to console. Don't attempt to create schema.yml files.",
    )

    parsed = p.parse_args()
    return parsed

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parsed = parse_args(args)

    if parsed.command == 'bootstrap':
        task = bootstrap_task.BootstrapTask(parsed)
        task.run()

    if parsed.command == 'compare':
        task = compare_task.CompareTask(parsed)
        task.run()

    config = RuntimeConfig.from_args(parsed)
    compiler = Compiler(config)
    adapter = dbt.adapters.factory.get_adapter(config)
    print("Do something here!")

if __name__ == "__main__":
    main()
