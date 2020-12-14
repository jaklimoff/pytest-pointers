import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Set

import libcst as cst
from libcst.metadata import QualifiedNameProvider, ParentNodeProvider


class MethodQualNamesCollector(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (QualifiedNameProvider, ParentNodeProvider)

    def __init__(self):
        self.found = []
        super().__init__()

    def visit_FunctionDef(self, node: cst.FunctionDef):
        header = getattr(node.body, "header", None)
        excluded = (
            header is not None
            and header.comment
            and header.comment.value.find("notest:") > -1
        )

        if not excluded:
            # TODO: Find better way to remove locals
            qual_names = self.get_metadata(QualifiedNameProvider, node)
            for qn in qual_names:
                from_local = qn.name.find("<locals>") > -1
                if not from_local:
                    self.found.append(qn.name)


@dataclass
class FuncFinder:
    start_dir: Path

    @classmethod
    def get_methods_qual_names(cls, node: cst.Module):
        collector = MethodQualNamesCollector()
        cst.MetadataWrapper(node).visit(collector)
        for method_name in collector.found:
            yield method_name

    def get_py_files(self) -> Set[Path]:
        py_files = [p for p in self.start_dir.glob("**/*.py")]
        py_files = set(py_files)

        for pattern in [".venv/**/*.py", "venv/**/*.py", "tests/**/*.py"]:
            py_files = py_files - set(self.start_dir.rglob(pattern))

        return py_files

    def __iter__(self):
        source_paths = [Path(p) for p in sys.path]

        py_files = self.get_py_files()

        for p in py_files:
            with open(p, "r") as f:
                tree = cst.parse_module(f.read())

            source = min(set(p.parents) & set(source_paths))
            abs_import = p.parts[len(source.parts) : -1] + (p.stem,)

            for fun_name in self.get_methods_qual_names(tree):
                yield ".".join(abs_import + (fun_name,))
