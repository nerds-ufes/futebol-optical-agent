#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from wss_agent.skeleton import fib

__author__ = "Rafael S. Guimarães"
__copyright__ = "Rafael S. Guimarães"
__license__ = "apache"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
