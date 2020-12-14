import json

import pytest

from pytest_pointers.plugin import _pointer_marker

pytestmark = [pytest.mark.unit]


@pytest.mark.pointer(target=_pointer_marker)
class TestPointerMarkerFixture:
    @staticmethod
    def get_params():
        content = """\
            import pytest

            class Some:
                def for_test(self):
                    return 1

            @pytest.mark.pointer(target=Some.for_test)
            def test_for_test():
                result = Some().for_test()
                assert result == 1
        """
        expect = {
            "test__regular_flow__pointers_collected.Some.for_test": [
                "test__regular_flow__pointers_collected.py::test_for_test"
            ]
        }
        yield pytest.param(content, expect, id="One test of method")

        # ----8<----------------------------------------------------------------------

        content = """\
            import pytest

            class Some:
                def for_test1(self):
                    return 1

                def for_test2(self):
                    return 1

            @pytest.mark.pointer(target=Some.for_test1)
            def test_for_test1():
                result = Some().for_test1()
                assert result == 1

            @pytest.mark.pointer(target=Some.for_test2)
            def test_for_test2():
                result = Some().for_test2()
                assert result == 1
        """
        expect = {
            "test__regular_flow__pointers_collected.Some.for_test1": [
                "test__regular_flow__pointers_collected.py::test_for_test1"
            ],
            "test__regular_flow__pointers_collected.Some.for_test2": [
                "test__regular_flow__pointers_collected.py::test_for_test2"
            ],
        }
        yield pytest.param(content, expect, id="Two tests for two methods")

        # ----8<----------------------------------------------------------------------

        content = """\
            import pytest

            class Some:
                def for_test(self):
                    return 1


            @pytest.mark.pointer(target=Some.for_test)
            class TestSome:
                def test_for_test1(self):
                    result = Some().for_test()
                    assert result == 1

                def test_for_test2(self):
                    result = Some().for_test()
                    assert result == 1
        """
        expect = {
            "test__regular_flow__pointers_collected.Some.for_test": [
                "test__regular_flow__pointers_collected.py::TestSome::test_for_test1",
                "test__regular_flow__pointers_collected.py::TestSome::test_for_test2",
            ]
        }
        yield pytest.param(content, expect, id="Two test for one method")

        # ----8<----------------------------------------------------------------------

        content = """\
            import pytest

            class Some:
                @property
                def for_test(self):
                    return 1


            @pytest.mark.pointer(Some, 'for_test')
            class TestSome:
                def test_for_test(self):
                    result = Some().for_test
                    assert result == 1
        """
        expect = {
            "test__regular_flow__pointers_collected.Some.for_test": [
                "test__regular_flow__pointers_collected.py::TestSome::test_for_test"
            ]
        }
        yield pytest.param(content, expect, id="Property as a target")

        # ----8<----------------------------------------------------------------------

        content = """\
            import pytest

            class Some:
                @classmethod
                def for_test(cls):
                    return 1
            
            
            @pytest.mark.pointer(target=Some.for_test)
            class TestSome:
                def test_for_test(self):
                    result = Some.for_test()
                    assert result == 1
        """
        expect = {
            "test__regular_flow__pointers_collected.Some.for_test": [
                "test__regular_flow__pointers_collected.py::TestSome::test_for_test"
            ]
        }
        yield pytest.param(content, expect, id="Classmethod as a target")

    @pytest.mark.parametrize(("content", "expect"), get_params.__func__())  # noqa
    def test__regular_flow__pointers_collected(self, testdir, content, expect):
        """
        Make sure that pointer marker is working properly
        """
        testdir.makepyfile(content)

        result = testdir.runpytest("--pointers-collect")
        assert result.ret == 0

        cache_file = testdir.tmpdir / ".pytest_cache" / "v" / "pointers" / "targets"
        assert cache_file.exists()
        with open(cache_file, "r") as f:
            targets = json.loads(f.read())

        assert targets == expect
