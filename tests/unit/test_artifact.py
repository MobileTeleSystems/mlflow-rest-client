import logging

import pytest

from mlflow_client.artifact import Artifact

from .conftest import DEFAULT_TIMEOUT, rand_int, rand_str

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact():
    path = rand_str()

    artifact = Artifact(path)

    assert artifact.path == path


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_with_root():
    path = rand_str()
    root = rand_str()

    artifact = Artifact(path, root=root)

    assert artifact.root == root


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_without_root():
    path = rand_str()

    artifact = Artifact(path)

    assert artifact.root is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("is_dir", [(False), (True)])
def test_artifact_with_is_dir(is_dir):
    path = rand_str()

    artifact = Artifact(path, is_dir=is_dir)
    assert artifact.is_dir == is_dir


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_without_is_dir():
    path = rand_str()

    artifact = Artifact(path)

    assert not artifact.is_dir


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_with_file_size():
    path = rand_str()
    file_size = rand_int()

    artifact = Artifact(path, file_size=file_size)

    assert artifact.file_size == file_size


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_without_file_size():
    path = rand_str()

    artifact = Artifact(path)

    assert artifact.file_size == 0


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_make_str():
    path = rand_str()

    artifact = Artifact.make(path)

    assert artifact.path == path


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_make_tuple():
    root = rand_str()
    path = rand_str()

    artifact = Artifact.make((root, path))

    assert artifact.root == root
    assert artifact.path == path


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_make_dict():
    dct = {"path": rand_str()}

    artifact = Artifact.make(dct)

    assert artifact.path == dct["path"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_make_dict_with_root():
    dct = {"path": rand_str(), "root": rand_str()}

    artifact = Artifact.make(dct)

    assert artifact.root == dct["root"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_make_dict_with_root_kwargs():
    dct = {"path": rand_str()}
    root = rand_str()

    artifact = Artifact.make(dct, root=root)

    assert artifact.root == root


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("is_dir", [(False), (True)])
def test_artifact_make_dict_with_is_dir(is_dir):
    dct = {"path": rand_str(), "is_dir": is_dir}

    artifact = Artifact.make(dct)

    assert artifact.is_dir == dct["is_dir"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_make_dict_with_file_size():
    dct = {"path": rand_str(), "file_size": rand_int()}

    artifact = Artifact.make(dct)

    assert artifact.file_size == dct["file_size"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_full_path():
    path = rand_str()

    artifact = Artifact(path)

    assert artifact.full_path
    assert artifact.full_path == path


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_full_path_with_root():
    path = rand_str()
    root = rand_str()

    artifact = Artifact(path, root=root)

    assert artifact.full_path
    assert artifact.full_path == "{}/{}".format(root, path)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_str():
    path = rand_str()

    artifact = Artifact(path)

    assert str(artifact)
    assert str(artifact) == path


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_str_with_root():
    path = rand_str()
    root = rand_str()

    artifact = Artifact(path, root=root)

    assert str(artifact)
    assert str(artifact) == "{}/{}".format(root, path)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_eq():
    path1 = rand_str()
    path2 = rand_str()

    assert Artifact(path1) == Artifact(path1)
    assert Artifact(path1) != Artifact(path2)

    root1 = rand_str()
    root2 = rand_str()

    assert Artifact(path1, root=root1) == Artifact(path1, root=root1)
    assert Artifact(path1, root=root1) != Artifact(path1, root=root2)

    assert Artifact(path1, root=root1) != Artifact(path2, root=root1)
    assert Artifact(path1, root=root1) != Artifact(path2, root=root2)

    assert Artifact(path1, is_dir=False) == Artifact(path1, is_dir=False)
    assert Artifact(path1, is_dir=True) == Artifact(path1, is_dir=True)

    assert Artifact(path1, is_dir=False) != Artifact(path1, is_dir=True)
    assert Artifact(path1, is_dir=True) != Artifact(path1, is_dir=False)

    assert Artifact(path1, is_dir=False) != Artifact(path2, is_dir=False)
    assert Artifact(path1, is_dir=True) != Artifact(path2, is_dir=True)

    assert Artifact(path1, is_dir=False) != Artifact(path2, is_dir=True)
    assert Artifact(path1, is_dir=True) != Artifact(path2, is_dir=False)

    file_size1 = rand_int()
    file_size2 = rand_int()

    assert Artifact(path1, file_size=file_size1) == Artifact(path1, file_size=file_size1)
    assert Artifact(path1, file_size=file_size1) != Artifact(path1, file_size=file_size2)

    assert Artifact(path1, file_size=file_size1) != Artifact(path2, file_size=file_size1)
    assert Artifact(path1, file_size=file_size1) != Artifact(path2, file_size=file_size2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_eq_path():
    path1 = rand_str()
    path2 = rand_str()

    assert Artifact(path1) == path1
    assert Artifact(path1) != path2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_eq_path_with_root():
    path1 = rand_str()

    root1 = rand_str()
    root2 = rand_str()

    assert Artifact(path1, root=root1) == "{}/{}".format(root1, path1)
    assert Artifact(path1, root=root1) != path1
    assert Artifact(path1, root=root1) != "{}/{}".format(root2, path1)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_in():
    path1 = rand_str()
    path2 = rand_str()

    artifact1 = Artifact(path1)
    artifact2 = Artifact(path2)

    lst = Artifact.from_list([artifact1])

    assert artifact1 in lst
    assert artifact2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_in_by_path():
    path1 = rand_str()
    path2 = rand_str()

    artifact1 = Artifact(path1)

    lst = Artifact.from_list([artifact1])

    assert path1 in lst
    assert path2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_in_by_path_with_root():
    path1 = rand_str()
    path2 = rand_str()

    root1 = rand_str()
    root2 = rand_str()

    artifact1 = Artifact(path1, root=root1)

    lst = Artifact.from_list([artifact1])

    assert "{}/{}".format(root1, path1) in lst
    assert "{}/{}".format(root1, path2) not in lst
    assert "{}/{}".format(root2, path1) not in lst
    assert "{}/{}".format(root2, path2) not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_get_item_by_path():
    path1 = rand_str()
    path2 = rand_str()

    artifact1 = Artifact(path1)

    lst = Artifact.from_list([artifact1])

    assert lst[path1] == artifact1

    with pytest.raises(KeyError):
        lst[path2]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_artifact_get_item_by_path_with_root():
    path1 = rand_str()
    path2 = rand_str()

    root1 = rand_str()
    root2 = rand_str()

    artifact1 = Artifact(path1, root=root1)

    lst = Artifact.from_list([artifact1])

    assert lst["{}/{}".format(root1, path1)] == artifact1

    with pytest.raises(KeyError):
        lst["{}/{}".format(root1, path2)]

    with pytest.raises(KeyError):
        lst["{}/{}".format(root2, path1)]

    with pytest.raises(KeyError):
        lst["{}/{}".format(root2, path2)]
