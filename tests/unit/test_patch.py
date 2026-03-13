"""Tests for patch functionality."""

import pytest
import tempfile
import os
from pathlib import Path
from agent_smith.patch import (
    parse_patch,
    apply_patch,
    derive_new_contents,
    generate_unified_diff,
    PatchType,
    ParseError,
    ComputeReplacementsError,
)


def test_parse_add_file():
    """Test parsing an add file patch."""
    patch = """*** Begin Patch
*** Add File: /tmp/test_file.py
+def hello():
+    print("Hello, World!")
*** End Patch"""

    hunks = parse_patch(patch)
    assert len(hunks) == 1
    assert hunks[0].type == PatchType.ADD
    assert hunks[0].path == "/tmp/test_file.py"
    assert "def hello():" in hunks[0].contents


def test_parse_delete_file():
    """Test parsing a delete file patch."""
    patch = """*** Begin Patch
*** Delete File: /tmp/test_file.py
*** End Patch"""

    hunks = parse_patch(patch)
    assert len(hunks) == 1
    assert hunks[0].type == PatchType.DELETE
    assert hunks[0].path == "/tmp/test_file.py"


def test_parse_update_file():
    """Test parsing an update file patch."""
    patch = """*** Begin Patch
*** Update File: /tmp/test_file.py
@@ old_function
-def old_function():
-    pass
+def new_function():
+    return True
*** End Patch"""

    hunks = parse_patch(patch)
    assert len(hunks) == 1
    assert hunks[0].type == PatchType.UPDATE
    assert hunks[0].path == "/tmp/test_file.py"
    assert hunks[0].chunks[0].old_lines == ["def old_function():", "    pass"]
    assert hunks[0].chunks[0].new_lines == ["def new_function():", "    return True"]


def test_parse_invalid_patch():
    """Test parsing an invalid patch raises error."""
    with pytest.raises(ParseError):
        parse_patch("invalid patch content")


def test_parse_patch_missing_markers():
    """Test parsing patch without markers raises error."""
    with pytest.raises(ParseError):
        parse_patch("*** Add File: test.txt\n+content")


def test_derive_new_contents():
    """Test deriving new contents from chunks."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("line 1\nline 2\nline 3\n")
        temp_path = f.name

    try:
        from agent_smith.patch import UpdateFileChunk

        chunks = [
            UpdateFileChunk(
                old_lines=["line 2"],
                new_lines=["modified line 2"],
                change_context="line 1",
                is_end_of_file=False,
            )
        ]

        diff, content = derive_new_contents(temp_path, chunks)
        assert "modified line 2" in content
    finally:
        os.unlink(temp_path)


def test_generate_unified_diff():
    """Test generating unified diff."""
    old = "line 1\nline 2\nline 3\n"
    new = "line 1\nmodified line 2\nline 3\n"

    diff = generate_unified_diff(old, new)
    assert "-line 2" in diff
    assert "+modified line 2" in diff


@pytest.mark.asyncio
async def test_apply_patch_add():
    """Test applying an add file patch."""
    import asyncio

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "new_file.py")
        patch = f"""*** Begin Patch
*** Add File: {test_file}
+def hello():
+    print("Hello")
*** End Patch"""

        result = await apply_patch(patch)
        assert test_file in result.added
        assert os.path.exists(test_file)
        content = Path(test_file).read_text()
        assert "def hello():" in content


@pytest.mark.asyncio
async def test_apply_patch_update():
    """Test applying an update file patch."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def old():\n    pass\n")
        temp_path = f.name

    try:
        patch = f"""*** Begin Patch
*** Update File: {temp_path}
@@
-def old():
-    pass
+def new():
+    return True
*** End Patch"""

        result = await apply_patch(patch)
        assert temp_path in result.modified
        content = Path(temp_path).read_text()
        assert "def new():" in content
        assert "return True" in content
    finally:
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_apply_patch_delete():
    """Test applying a delete file patch."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("content\n")
        temp_path = f.name

    patch = f"""*** Begin Patch
*** Delete File: {temp_path}
*** End Patch"""

    result = await apply_patch(patch)
    assert temp_path in result.deleted
    assert not os.path.exists(temp_path)


def test_strip_heredoc():
    """Test stripping heredoc syntax."""
    from agent_smith.patch import strip_heredoc

    input_text = """cat <<'EOF'
content here
more content
EOF"""

    result = strip_heredoc(input_text)
    assert result == "content here\nmore content"


def test_parse_with_move():
    """Test parsing patch with move directive."""
    patch = """*** Begin Patch
*** Update File: /tmp/old.py
*** Move to: /tmp/new.py
@@ main
-old code
+new code
*** End Patch"""

    hunks = parse_patch(patch)
    assert len(hunks) == 1
    assert hunks[0].move_path == "/tmp/new.py"
