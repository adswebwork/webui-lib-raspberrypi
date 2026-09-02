"""Pruning old captures.

The kennel camera runs unattended and a full SD card stops the Pi writing
anything at all, so pruning is the thing standing between this node and a
silent failure. It had never been tested.
"""
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "projects", "dog-camera-monitor"))

from lib import capture  # noqa: E402


def _make_images(directory, count):
    """`count` .jpg files, oldest first by mtime."""
    paths = []
    for index in range(count):
        path = os.path.join(str(directory), "img-{:03d}.jpg".format(index))
        with open(path, "w") as handle:
            handle.write("x")
        os.utime(path, (index, index))          # deterministic age order
        paths.append(path)
    return paths


def test_keeps_the_newest_and_removes_the_rest(tmp_path):
    _make_images(tmp_path, 10)
    assert capture.prune(str(tmp_path), keep=4) == 6
    left = sorted(os.listdir(str(tmp_path)))
    assert left == ["img-006.jpg", "img-007.jpg", "img-008.jpg", "img-009.jpg"]


def test_nothing_to_do_when_under_the_limit(tmp_path):
    _make_images(tmp_path, 3)
    assert capture.prune(str(tmp_path), keep=500) == 0
    assert len(os.listdir(str(tmp_path))) == 3


def test_non_jpg_files_are_left_alone(tmp_path):
    _make_images(tmp_path, 5)
    keeper = os.path.join(str(tmp_path), "notes.txt")
    with open(keeper, "w") as handle:
        handle.write("not a capture")
    capture.prune(str(tmp_path), keep=1)
    assert os.path.exists(keeper)


def test_missing_directory_is_not_an_error(tmp_path):
    assert capture.prune(os.path.join(str(tmp_path), "nope"), keep=5) == 0


def test_none_disables_pruning(tmp_path):
    _make_images(tmp_path, 10)
    assert capture.prune(str(tmp_path), keep=None) == 0
    assert len(os.listdir(str(tmp_path))) == 10


@pytest.mark.parametrize("keep", [0, -1])
def test_zero_or_negative_is_rejected_not_guessed(tmp_path, keep):
    """0 reads as both "keep none" and "no limit". The old code silently chose
    neither - it pruned nothing, contradicting its own docstring."""
    _make_images(tmp_path, 5)
    with pytest.raises(ValueError, match="keep=None"):
        capture.prune(str(tmp_path), keep=keep)
    assert len(os.listdir(str(tmp_path))) == 5, "nothing deleted on a bad limit"
