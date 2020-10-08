# `dbt-helper` (beta)

NOTE: `dbt-helper` currently only works with dbt version >= 0.17.1. This is still in extremely-limited beta release. We'd love your help, testing it though! Until we're out of beta, please don't build this into anything production-touching as it will surely get broken sooner rather than later

`dbt-helper` is a command line tool that helps with developing [`dbt`](https://www.getdbt.com/) projects and managing data warehouses.

This repository is **not** formally associated with dbt and is not maintained by fishtown-analytics (the maintainers of dbt). If you have problems with one of these (`dbt-helper`) tools, please file an issue on _this_ repository and do not bother the dbt maintainers about it.

## Installation

```bash
pip install dbt-helper
```

NOTE: dbt-helper may not work with dbt when dbt is installed via homebrew. We are currently investigating options for fixes, but if you experience issues that might be the culprit.

## Usage

`dbt-helper` (currently) has seven sub-commands:

* `compare`: Compare the relations in your warehouse with those that dbt is managing. This is useful for identifying "stale" relations that are no longer being updated by dbt (like if, for example, you converted the model from materialized to ephemeral).
  * Note: `dbt-helper compare` will compare all schemas that are impacted by models in the `models/` directory. There is (currently) no way to specify a single schema to compare.
* `bootstrap`: Create starter "`schema.yml`" files for your project. This function helpfully generates boilerplate dbt-model files for you so you don't have to go through the copy/paste when you're developing a new model.
  * Note: this command will not over-write existing `schema.yml` files. It will default to printing templates to the console, but you can create new files by using the `--write-files` flag.
* `show-upstream`: Inspect the dbt graph and show the relations that are "upstream" from (i.e., the "parents" of) the selected relation. Print to the terminal.
* `show-downstream`: The same as `show-upstream` but in the other direction -- show dependents 'downstream' from (i.e., the "children" of) the selected relation
* `find`: Find the compiled `.sql` file for a model by providing the model name only. You can also find the source or run `.sql` files for a model by using the appropriate flag. Useful when working in large dbt projects and you want to find files quickly wihout having to navigate a file tree.
* `open`: Open the compiled `.sql` file for a model by providing the model name only. Works the same as find, but directly opens the file in your text editor.
* `retry-failed`: Rerun models that errored or were skipped on your previous dbt run.

As one might hope, you can view the command line options directly from the tool by using the help functionality:

```bash
dbt-helper --help
```

### Usage Details:

#### `compare`

```bash
$ dbt-helper compare

Comparing local models to the database catalog. Checking schemas:
- dev_downstream
- dev_example
Warning: The following relations do not match any models found in this project:
TABLE "dev_example"."b"
VIEW "dev_downstream"."d"
```

#### `bootstrap`

```bash
$ dbt-helper bootstrap --schemas dev_example

Bootstrapping the following schemas:
- dev_example
--------------------
Design for relation: dev_example.my_first_dbt_model
--------------------
version: 2
models:
  name: my_first_dbt_model
- columns:
  - name: id
  description: 'TODO: Replace me'

--------------------
Design for relation: dev_example.b
--------------------
version: 2
models:
  name: b
- columns:
  - name: city
  - name: count
  description: 'TODO: Replace me'
```

#### `show-upstream`
```bash
$ dbt-helper show-upstream d

--------------------------------------------------------------------------------
                                  downstream.d
--------------------------------------------------------------------------------
                                   example.b
--------------------------------------------------------------------------------
```

#### `show-downstream`
_see `show-upstream`_

#### `find`

```bash
# Find the compiled version of model
$ dbt-helper find my_model

# Same as above
$ dbt-helper find my_model --compiled

# Find the run version of the model
$ dbt-helper find my_model --run

# Find the source version of the model
$ dbt-helper find my_model --source
```

**Understanding the flags:**

* The `--compiled` flag will find the relevant `.sql` file in the
`target/compiled` directory. This file contains the compiled `SELECT` query.
* The `--run` flag will find the relevant `.sql` file in the `target/run`
directory. The `run` version of the model contains the compiled query wrapped
in the DDL (i.e. `CREATE`) statements to materialize it in the warehouse.
* The `--source` flag will find the relevant jinja-flavored `.sql` file in the
`models/` directory.

Without a flag, dbt-helper will find the `compiled` model.

#### `open`

```bash
# Open the compiled version of model
$ dbt-helper open my_model

# Same as above
$ dbt-helper open my_model --compiled

# Open the run version of the model
$ dbt-helper open my_model --run

# Open the source version of the model
$ dbt-helper open my_model --source

# Print model to STDOUT rather than opening in a text editor
$ dbt-helper open my_model --print

```

These flags work exactly the same was `find` above, so check there for more detail on these.

**If dbt-helper is opening your file in the wrong text editor**, update your
`$EDITOR` environment variable to be the command you normally use to open a file
in your text editor, e.g. `vim`, `emacs`, `atom`, `code`, or `subl`. If you
would prefer to not update your `$EDITOR` env var, you can instead create a
`$DBT_HELPER_EDITOR` environment variable for your command.

dbt-helper will try to use one of the following commands to open the file (in
order of precedence):
* `$DBT_HELPER_EDITOR`. If this is not set, then it will use:
* `$EDITOR`: A standard environment variable used across a number of
applications (e.g. git prompts launch in the editor specified here). If this is
not set, then use:
* `"Open"`: Generic command that will open a file in the default application for
the associated file type.


#### `retry-failed`
```bash
$ dbt-helper retry-failed
dbt run --models my_failed_model my_skipped_model
Running with dbt=0.13.0
Found 8 models, 20 tests, 0 archives, 0 analyses, 113 macros, 0 operations, 3 seed files, 0 sources

17:40:11 | Concurrency: 1 threads (target='dev')
17:40:11 |
17:40:11 | 1 of 2 START view model dev_example.my_failed_model.................. [RUN]
17:40:12 | 1 of 2 OK created view model dev_example.my_failed_model............. [CREATE VIEW in 0.65s]
17:40:12 | 2 of 2 START table model dev_example.my_skipped_model................ [RUN]
17:40:29 | 2 of 2 OK created table model dev_example.my_skipped_model........... [SELECT in 16.86s]
17:41:31 |
17:41:31 | Finished running 1 view models, 1 table models in 80.96s.
```

## Contributing

Install locally for development:

```
pip install -e .
```

### Conventions

We follow a few conventions in this repository.

#### Git stuff

Please name your branch names with a prefix denoting the type of change you're making. For example:

```bash
feature/my-descriptive-feature-name
fix/describe-the-fix
docs/whats-changing
```

Please also follow generally accepted git best practices by using descriptive commit messages and squashing your commits (where possible) before submitting your PR (or after making any required changes).

#### Python formatting

We use [`black`](https://github.com/ambv/black) to format python code in this project. Please use it! (And consider using it for all of your other python projects while you're at it.)

### Running the tests

Run the tests using your local environment:

```
tox -e dev -- --nocapture
```

Run the tests locally using docker:

```
docker-compose run test tox -- --nocapture
```

If you want to specify a particular test to run, you can pass in a path to an integration test to either of the above commands, e.g.:

```
tox -e dev -- --nocapture test/integration/001_compare_test/
```

## Giving Thanks

* Thanks to [Claire Carroll](https://github.com/clrcrl) for the `open` and `retry-failed` functions
* Thanks to [Drew Banin](https://github.com/drewbanin) for invaluable discussion and code-review on early `dbt-helper` features.
* Thanks to [John Lynch](https://github.com/jplynch77) for early beta-testing and feedback.
* Thanks to [Leon Tchikindas](https://github.com/ltchikindas) for the [blog post](https://www.periscopedata.com/blog/automated-identification-and-graphing-of-sql-dependencies) (and code) inspiring this command-line graph builder.
