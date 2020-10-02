import logging
import pytest

from mlflow_client.tag import Tag
from .conftest import DEFAULT_TIMEOUT, rand_str

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag():
    key = rand_str()
    value = rand_str()

    tag = Tag(key, value)

    assert tag.key == key
    assert tag.value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_without_value():
    key = rand_str()

    tag = Tag(key)

    assert tag.key == key
    assert tag.value == ''


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_make_str():
    key = rand_str()

    tag = Tag.make(key)

    assert tag.key == key
    assert tag.value == ''


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_make_tuple():
    key = rand_str()
    value = rand_str()

    tag = Tag.make((key, value))

    assert tag.key == key
    assert tag.value == value


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_make_dict():
    dct = {
        'key': rand_str(),
        'value': rand_str(),
    }

    tag = Tag.make(dct)

    assert tag.key == dct['key']
    assert tag.value == dct['value']


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_make_dict_without_value():
    dct = {
        'key': rand_str(),
    }

    tag = Tag.make(dct)

    assert tag.key == dct['key']
    assert tag.value == ''


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_str():
    key = rand_str()
    value = rand_str()

    tag = Tag(key, value)

    assert str(tag)
    assert str(tag) == key


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_eq():
    key1 = rand_str()
    key2 = rand_str()

    value1 = rand_str()
    value2 = rand_str()

    assert Tag(key1, value1) == Tag(key1, value1)
    assert Tag(key1, value1) != Tag(key1, value2)

    assert Tag(key1, value1) != Tag(key2, value1)
    assert Tag(key1, value1) != Tag(key2, value2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_eq_str():
    key1 = rand_str()
    key2 = rand_str()

    value1 = rand_str()

    assert Tag(key1, value1) == key1
    assert Tag(key1, value1) != key2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_list_in_by_key():
    key1 = rand_str()
    key2 = rand_str()

    value1 = rand_str()

    tag1 = Tag(key1, value1)

    lst = Tag.from_list([
        tag1
    ])

    assert key1 in lst
    assert key2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_tag_list_get_item_by_key():
    key1 = rand_str()
    key2 = rand_str()

    value1 = rand_str()

    tag1 = Tag(key1, value1)

    lst = Tag.from_list([
        tag1
    ])

    assert lst[key1] == tag1

    with pytest.raises(KeyError):
        lst[key2]
