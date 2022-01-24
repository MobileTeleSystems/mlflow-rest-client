from __future__ import annotations

import logging

import pytest

from mlflow_client.tag import Tag

from .conftest import DEFAULT_TIMEOUT, rand_str

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag():
    key = rand_str()
    value = rand_str()

    tag = Tag(key=key, value=value)

    assert tag.key == key
    assert tag.value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_without_value():
    key = rand_str()

    tag = Tag(key=key)

    assert tag.key == key
    assert tag.value == ""


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_str():
    key = rand_str()
    value = rand_str()

    tag = Tag(key=key, value=value)

    assert str(tag)
    assert str(tag) == key


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_eq():
    key1 = rand_str()
    key2 = rand_str()

    value1 = rand_str()
    value2 = rand_str()

    assert Tag(key=key1, value=value1) == Tag(key=key1, value=value1)
    assert Tag(key=key1, value=value1) != Tag(key=key1, value=value2)

    assert Tag(key=key1, value=value1) != Tag(key=key2, value=value1)
    assert Tag(key=key1, value=value1) != Tag(key=key2, value=value2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_eq_str():
    key1 = rand_str()
    key2 = rand_str()

    value1 = rand_str()

    assert Tag(key=key1, value=value1).key == key1
    assert Tag(key=key1, value=value1).key != key2
