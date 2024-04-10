import pytest
from src.utils import read_json


@pytest.fixture
def base_path():
    return "tests/files"


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("test.json", {"system": "test"}),
    ],
)
def test_read_valid_json(base_path, file_name, expected):
    expected = {"System": {"Name": "Test", "Version": "1.0.0"}}
    path = f"{base_path}/{file_name}"
    assert read_json(path) == expected


def test_read_invalid_file_format(base_path):
    path = f"{base_path}/test.txt"
    assert read_json(path) is None


def test_read_invalid_json(base_path):
    path = f"{base_path}/invalid.json"
    assert read_json(path) is None
