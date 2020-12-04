import logging
import pytest

from mlflow_client.page import Page
from mlflow_client.model import Model
from mlflow_client.artifact import Artifact
from .conftest import DEFAULT_TIMEOUT, rand_str, rand_int

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page():
    items = [rand_str()]

    page = Page(items)

    assert page.items == items


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_with_next_page_token():
    items = [rand_str()]
    next_page_token = rand_str()

    page = Page(items, next_page_token=next_page_token)

    assert page.next_page_token == next_page_token
    assert page.has_next_page


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_without_next_page_token():
    items = [rand_str()]

    page = Page(items)

    assert page.next_page_token is None
    assert not page.has_next_page


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_make_dict():
    dct = {"items": [rand_str()]}

    page = Page.make(dct)

    assert page.items == dct["items"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_make_dict_with_next_page_token():
    dct = {"items": [rand_str()], "next_page_token": rand_str()}

    page = Page.make(dct)

    assert page.items == dct["items"]
    assert page.next_page_token == dct["next_page_token"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_make_dict_with_items_key():
    dct = {"runs": [rand_str()]}

    page = Page.make(dct, items_key="runs")

    assert page.items == dct["runs"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_make_item_class():
    dct = {
        "items": [rand_str()],
    }

    page = Page.make(dct, item_class=Model)

    assert page.items
    assert isinstance(page.items[0], Model)
    assert page.items[0].name == dct["items"][0]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_make_item_class_with_next_page_token():
    dct = {"items": [rand_str()], "next_page_token": rand_str()}

    page = Page.make(dct, item_class=Model)

    assert page.items
    assert isinstance(page.items[0], Model)
    assert page.items[0].name == dct["items"][0]
    assert page.next_page_token == dct["next_page_token"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_make_item_class_with_kwargs():
    dct = {
        "items": [{"path": rand_str(), "is_dir": True, "root": rand_str(), "file_size": rand_int()}],
    }
    root = rand_str()

    page = Page.make(dct, item_class=Artifact, root=root, is_dir=False)

    assert page.items
    assert isinstance(page.items[0], Artifact)
    assert page.items[0].path == dct["items"][0]["path"]
    assert not page.items[0].is_dir
    assert page.items[0].root == root
    assert page.items[0].file_size == dct["items"][0]["file_size"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_eq():
    items1 = [rand_str()]
    items2 = [rand_str(), rand_str()]

    assert Page(items1) == Page(items1)
    assert Page(items1) != Page(items2)

    next_page_token1 = rand_str()
    next_page_token2 = rand_str()

    assert Page(items1, next_page_token=next_page_token1) == Page(items1, next_page_token=next_page_token1)
    assert Page(items1, next_page_token=next_page_token1) != Page(items1)

    assert Page(items1, next_page_token=next_page_token1) != Page(items2, next_page_token=next_page_token1)
    assert Page(items1, next_page_token=next_page_token1) != Page(items2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_eq_list():
    items1 = [rand_str()]
    items2 = [rand_str()]

    assert Page(items1) == items1
    assert Page(items1) != items2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_in():
    item1 = rand_str()
    item2 = rand_str()

    items = [item1]

    page = Page(items)

    assert item1 in page
    assert item2 not in page


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_get_item():
    item1 = rand_str()
    item2 = rand_str()

    items = [item1]

    page = Page(items)

    assert page[0] == item1
    assert page[0] != item2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_add():
    item1 = rand_str()
    item2 = rand_str()

    items = [item1]

    page = Page(items)
    assert item2 not in page

    page += item2
    assert item2 in page


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_del():
    item1 = rand_str()
    item2 = rand_str()

    items = [item1, item2]

    page = Page(items)
    assert item2 in page

    del page[1]
    assert item2 not in page


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_len():
    item1 = rand_str()
    item2 = rand_str()

    assert len(Page([])) == 0
    assert len(Page([item1])) == 1
    assert len(Page([item1, item2])) == 2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_page_iterator():
    item1 = rand_str()
    item2 = rand_str()

    page = Page([item1, item2])

    found_item1 = False
    found_item2 = False
    for item in page:
        if item == item1:
            found_item1 = True
        if item == item2:
            found_item2 = True

    assert found_item1
    assert found_item2
