import ast
import sys
from _ast import ClassDef, AST
from _ast import FunctionDef, AsyncFunctionDef
from dataclasses import dataclass
from pathlib import Path
from typing import Set


@dataclass
class FuncFinder:
    start_dir: Path

    @classmethod
    def get_methods(cls, node: AST):
        for child in node.body:
            if isinstance(child, ClassDef):
                for m in cls.get_methods(child):
                    m.parent = child
                    yield m
            if isinstance(child, FunctionDef) or isinstance(child, AsyncFunctionDef):
                yield child

    @classmethod
    def get_node_qual_name(cls, node: AST) -> str:
        def get_name(n: AST):
            if hasattr(n, 'parent'):
                return get_name(n.parent) + [n.name]
            else:
                return [n.name]

        return ".".join(get_name(node))

    def get_py_files(self) -> Set[Path]:
        py_files = [p for p in self.start_dir.glob('**/*.py')]
        py_files = set(py_files)

        for pattern in [".venv/**/*.py", "venv/**/*.py", "tests/**/*.py"]:
            py_files = py_files - set(self.start_dir.rglob(pattern))

        return py_files

    def __iter__(self):
        source_paths = [Path(p) for p in sys.path]

        py_files = self.get_py_files()

        for p in py_files:
            with open(p, 'r') as f:
                tree = ast.parse(f.read())

            source = min(set(p.parents) & set(source_paths))
            abs_import = p.parts[len(source.parts):-1] + (p.stem,)

            for func in self.get_methods(tree):
                name = FuncFinder.get_node_qual_name(func)
                yield ".".join(abs_import + (name,))
