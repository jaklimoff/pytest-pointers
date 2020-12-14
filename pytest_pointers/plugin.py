from pathlib import Path
from textwrap import dedent
from typing import Union

import pytest
from rich.console import Console
from rich.padding import Padding

from pytest_pointers.utils import FuncFinder

CACHE_TARGETS = "pointers/targets"
CACHE_ALL_FUNC = "pointers/funcs"


def pytest_addoption(parser):
    group = parser.getgroup("pointers")
    group.addoption(
        "--pointers-report",
        action="store_true",
        dest="pointers_report",
        default=False,
        help="Show report in console",
    )
    group.addoption(
        "--pointers-collect",
        action="store_true",
        dest="pointers_collect",
        default=False,
        help="Gather targets and tests for them",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "pointer(element): Define a tested element.")


def pytest_sessionstart(session: pytest.Session):
    if session.config.option.pointers_collect or session.config.option.pointers_report:
        session.config.cache.set(CACHE_TARGETS, {})


@pytest.fixture(scope="function", autouse=True)
def _pointer_marker(request):
    if (
        not request.config.option.pointers_collect
        and not request.config.option.pointers_report
    ):
        return

    pointers = request.config.cache.get(CACHE_TARGETS, {})
    marker = request.node.get_closest_marker("pointer")
    if marker:
        target_full_name = None
        if "target" in marker.kwargs:
            # support for regular pointers
            # @pytest.mark.pointer(target=Some.for_test)
            target = marker.kwargs.get("target", None)
            target_full_name = f"{target.__module__}.{target.__qualname__}"
        elif len(marker.args) == 2:
            # support for property pointers
            # @pytest.mark.pointer(Some, 'for_test')
            target_parent, target_member = marker.args
            target_full_name = f"{target_parent.__module__}.{target_parent.__qualname__}.{target_member}"

        if target_full_name not in pointers:
            pointers[target_full_name] = []

        pointers[target_full_name].append(request.node.nodeid)
        request.config.cache.set(CACHE_TARGETS, pointers)


def pytest_sessionfinish(
    session: pytest.Session, exitstatus: Union[int, pytest.ExitCode]
):
    if session.config.option.pointers_report:
        console = Console()
        console.print("")

        pointers = session.config.cache.get(CACHE_TARGETS, {})

        start_dir = Path(session.startdir)  # noqa
        funcs = FuncFinder(start_dir)

        def report_line(f):
            test_count = len(pointers.get(f, []))

            if test_count > 1:
                color = "green"
            elif test_count == 1:
                color = "blue"
            else:
                color = "red"

            test_count_str = f"{test_count: <2}"
            return f"[{color}]{test_count_str:·<5}[/{color}] {f}"

        report_lines = "\n".join([report_line(f) for f in funcs])
        report = dedent(
            f"""
        [bold]List of functions in project and the number of tests for them[/bold]

        \n{report_lines}
        """
        )

        test = Padding(report, (2, 4), expand=False)
        console.print(test)
