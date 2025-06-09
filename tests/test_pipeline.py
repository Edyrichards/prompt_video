import os
import tempfile
from pathlib import Path
import pytest # Ensure pytest is imported if specific features are used, though not strictly needed for basic tests

# Adjust the import path based on your project structure
# This assumes 'src' is in PYTHONPATH or tests are run from project root.
from prompt_video.pipeline import _safe_unlink

def test_safe_unlink_file_exists():
    """Test that _safe_unlink removes a file that exists."""
    # Create a temporary file
    # Use mkstemp to avoid potential issues with NamedTemporaryFile on some OSes regarding re-opening/deleting
    fd, temp_file_name = tempfile.mkstemp()
    os.close(fd) # Close the file descriptor
    temp_file_path = Path(temp_file_name)

    assert temp_file_path.exists(), "Temporary file was not created"

    _safe_unlink(temp_file_path)

    assert not temp_file_path.exists(), "_safe_unlink did not remove the existing file"

def test_safe_unlink_file_does_not_exist():
    """Test that _safe_unlink does not raise an error for a non-existent file."""
    non_existent_path = Path("surely_this_file_does_not_exist_12345.tmp")

    # Ensure it doesn't exist before the test, just in case
    if non_existent_path.exists():
        non_existent_path.unlink()

    try:
        _safe_unlink(non_existent_path)
    except Exception as e:
        pytest.fail(f"_safe_unlink raised an exception for a non-existent file: {e}")

def test_safe_unlink_with_string_path():
    """Test that _safe_unlink works with a string path."""
    fd, temp_file_name_str = tempfile.mkstemp()
    os.close(fd)
    temp_file_path = Path(temp_file_name_str) # Keep Path object for assertion

    assert temp_file_path.exists(), "Temporary file was not created (string path)"

    _safe_unlink(temp_file_name_str) # Pass string path to function

    assert not temp_file_path.exists(), "_safe_unlink did not remove the existing file (string path)"
