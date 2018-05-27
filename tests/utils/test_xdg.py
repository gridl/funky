"""Tests the localalias.utils.xdg utilities."""

import getpass
import os
import unittest.mock as mock

import pytest

import localalias.utils.xdg as xdg

pytestmark = pytest.mark.usefixtures("debug_mode")

user = getpass.getuser()


@pytest.mark.parametrize('key,expected', [
    ('config', '/home/{}/.config/localalias'.format(user)),
    ('data', '/home/{}/.local/share/localalias'.format(user)),
    ('runtime', '/run/user/1000/localalias'),
    ('cache', '/home/{}/.cache/localalias'.format(user))
])
def test_getdir(key,expected):
    """Tests that each user directory returned meets the XDG standard."""
    assert expected == xdg.getdir(key)


def test_getdir_failure():
    """Tests that xdg.getdir raises an exception for bad arguments."""
    with pytest.raises(ValueError):
        xdg.getdir('bad_key')
