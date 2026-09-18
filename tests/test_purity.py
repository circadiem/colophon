"""I6: channels/ is pure. No I/O, no network, no model, no clock reads except an injected as_of.
Enforced by reading the source, so a future import cannot slip in unnoticed."""

import ast
import pathlib

import colophon.channels as channels

ALLOWED_MODULES = {"dataclasses", "datetime", "enum", "hashlib", "typing", "calendar", "__future__", "collections"}
FORBIDDEN_CALLS = {"today", "now", "utcnow", "open", "urlopen", "get", "post", "connect"}


def _sources():
    root = pathlib.Path(channels.__file__).parent
    return sorted(root.glob("*.py"))


def test_channels_imports_only_the_standard_library_subset():
    for path in _sources():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] in ALLOWED_MODULES, (path.name, alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level:  # relative import inside channels/
                    continue
                assert node.module.split(".")[0] in ALLOWED_MODULES, (path.name, node.module)


def test_channels_never_reads_the_clock_or_the_network():
    for path in _sources():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
                assert name not in FORBIDDEN_CALLS, (path.name, name, node.lineno)


def test_channels_has_no_notice_templating():
    """CLAUDE.md §2: no templating of §203 or §304 notices, not even as a preview."""
    for path in _sources():
        text = path.read_text().lower()
        for phrase in ("dear ", "notice of termination", "hereby", "template", "jinja", "docx"):
            assert phrase not in text, (path.name, phrase)
