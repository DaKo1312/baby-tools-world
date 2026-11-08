# Testing

This project contains tests for the corresponding apps in the respective packages.
Tests in Django can either be located in a `tests.py` file within a django-app, or you could also have a module named `tests` (essentially a folder with an `__init__.py` file).
The django testrunner will by default discover tests by finding all python files that contain the word `test` in their name, e.g. `test.py`, `test_model.py`, or similar.

Example Structure:

```console
baby-tool-world/src/products
├───management
├───migrations
├───templates
└───tests <-- this is the module
      ├───__init__.py
      ├───test_category_model.py <-- this is a test file
      └───test_category_model.py <-- this is a test file too
```

## Important terms

| **Term**    | **Description** | **Example (products app)** |
|:---| :--- | :--- |
| Assertion | A statement in a test that checks if a condition is true; if not, the test fails. | `self.assertEqual(product.name, "Toy Car")` in `test_product_model.py` |
| Coverage | A metric indicating how much of the codebase is exercised by tests. | Using `coverage run manage.py test` to measure tests in `products/`. <br/>**NOTE:** the tests in a gitlab-ci pipeline run with coverage reporting enabled for MRs |
| Test | A single unit of code that checks a specific behavior or functionality. | `def test_product_str(self): ...` in `test_product_model.py` |
| TestCase | A class that groups related tests and provides setup/teardown logic. | `class ProductModelTestCase(TestCase): ...` in `test_product_model.py` |
| TestSuite | A collection of multiple test cases or tests that are run together. | Django automatically discovers and runs all tests in `products/tests/` as a suite. |


## Running tests

To run the tests with the `django testrunner` you can use the following command:

- `python manage.py test`, you need to run this in the folder where `manage.py` lives -> `src`

**Full command example**

This example assumes you have activated your virtual env and already have installed the project dependencies, see [here](#quickstart)

```bash
cd src
python manage.py test
```

### Run tests with coverage

```bash
cd src
coverage run manage.py test
# display the collected coverage information
coverage report -m --skip-covered --skip-empty
```

In order to prevent the runner from evaluating unnecessary files or files that do not contain tested code you can add the `--omit` option alongside with a pattern.

### Excluding files from coverage collection

The following example shows how to omit certain files from coverage discovery during the test execution.
This particular example omits the `manage.py` or and python file that contains the word `test`.

```bash
cd src
coverage run --omit=manage.py,test*.py manage.py test
# display the collected coverage information
coverage report -m --skip-covered --skip-empty
```
