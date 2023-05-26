## Pytest Plugin to Show Unit Coverage

**Code** coverage tools like
[coverage.py](https://coverage.readthedocs.io/en/7.0.1/) show you the
instrumented code coverage of your tests, however it won't tell you if you've
written specific unit tests for each of your code's **units** (here unit meaning
function).

This package implements a mechanism for measuring and reporting unit coverage.
Instead of instrumenting your code you will need to mark tests with a
**pointer** to the unit that it is covering.

For example if you have in your code this module `mypackage/widget.py`:

``` python
def foo(in):
    return in * 3
```

then in your test suite you would write a unit test for this function and mark it as relating to that unit, e.g. in `tests/test_widget.py`:

``` python

from mypackage.widget import foo

@pytest.mark.pointer(foo)
def test_foo():
    assert foo(3) == 9
```

This package works by collecting all of the pointed-to units during test
execution and persists these to the pytest cache (typically somewhere under
`.pytest_cache`). Then in subsequent runs you need only report the results.

### Invocation

This package adds a couple new options to the `pytest` CLI:

`--pointers-collect=STR` (default `src`)

This explicitly indicates to collect unit coverage results. If not specified,
but `--pointers-report` is given results will be collected using the default.

`--pointers-ignore=STR` (default ``)

Specify files via a comma separated list of glob pattern relative to the
`--pointers-collect` root directory to ignore. For example
`utils.py,no_unit/*.py`.

`--pointers-report` (default `False`)

When this flag is given a textual report will be given at the end of the test
run. Note that even if this is not given the coverage checks will still be run.

`--pointers-func-min-pass=INT` (default `2`)

This flag controls the number of unit test pointer marks are needed to get a
"passing" unit. In the report units with 0 pointers are shown as red, passing
numbers are green, and anything in between is blue.

`--pointers-fail-under=FLOAT` (default `0.0`)

This flag controls the percentage of passing units are needed for the entire
coverage check to pass. The percentage is always displayed even without
`--pointers-report`. If this test is failed then the test process exits with
code 1, which is useful for things like CI.


#### Example

Here is an example with source code under the `src` folder, requiring 1 pointer
test per collected unit in the code, for all functions.

```
pytest --pointers-report --pointers-collect=src --pointers-func-min-pass=1 --pointers-fail-under=100 tests
```

![](https://jaklimoff-misc.s3.eu-central-1.amazonaws.com/pytest-pointers/example_output.jpg)

### Installation

<<<<<<< HEAD
Just install from this git repository:

``` shell
pip install git+https://github.com/salotz/pytest-pointers.git
```

=======
``` shell
pip install pytest_pointers
```



>>>>>>> 453848dcc603cca982b2084292f0800cdcbd4125
