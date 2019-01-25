# `dbt-helper`

`dbt-helper` is a command line tool that helps with developing [`dbt`](https://www.getdbt.com/) codebases and managing data warehouses. 

This repository is **not** formally associated with dbt and is not maintained by fishtown-analytics (the maintainers of dbt). If you have problems with one of these tools, please file an issue on this repository and do not bother the dbt maintainers about it.

## Usage

`dbt-helper` (currently) has two sub-commands:

* `compare`: Compare the relations in your warehouse with those that dbt is managing. This is useful for identifying `stale` relations that are no longer being updated by dbt (like if, for example, you converted the model from materialized to ephemeral).
* `bootstrap`: Create starter "`schema.yml`" files for your project. This function helpfully generates boilerplate dbt-model files for you so you don't have to go through the copy/paste when you're developing a new model.

As one might hope, you can view the command line options directly from the tool by using the help functionality:

```bash
dbt-helper --help
```

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
$ dbt-helper bootstrap --schemas dev_example --print-only

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


## Contributing

Install locally for development:

```
pip install . -e
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
