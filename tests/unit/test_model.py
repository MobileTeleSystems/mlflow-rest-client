import logging
from datetime import timedelta

import pytest

from mlflow_client.model import (
    Model,
    ModelTag,
    ModelVersion,
    ModelVersionStage,
    ModelVersionState,
    ModelVersionStatus,
    ModelVersionTag,
)

from .conftest import DEFAULT_TIMEOUT, now, rand_int, rand_str

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.name == name
    assert model_version.version == version


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_with_creation_timestamp():
    name = rand_str()
    version = rand_int()
    created_time = now()

    model_version = ModelVersion(name, version, creation_timestamp=created_time)

    assert model_version.created_time == created_time


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_creation_timestamp():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.created_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_with_last_updated_timestamp():
    name = rand_str()
    version = rand_int()
    updated_time = now()

    model_version = ModelVersion(name, version, last_updated_timestamp=updated_time)

    assert model_version.updated_time == updated_time


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_last_updated_timestamp():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.updated_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "stage", [ModelVersionStage.unknown, ModelVersionStage.prod, ModelVersionStage.test, ModelVersionStage.archived]
)
def test_model_version_with_stage(stage):
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version, stage=stage)

    assert model_version.stage == stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_stage():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.stage == ModelVersionStage.unknown


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_with_description():
    name = rand_str()
    version = rand_int()

    description = rand_str()

    model_version = ModelVersion(name, version, description=description)

    assert model_version.description == description


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_description():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.description == ""


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_with_source():
    name = rand_str()
    version = rand_int()

    source = rand_str()

    model_version = ModelVersion(name, version, source=source)

    assert model_version.source == source


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_source():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.source == ""


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_with_run_id():
    name = rand_str()
    version = rand_int()

    run_id = rand_str()

    model_version = ModelVersion(name, version, run_id=run_id)

    assert model_version.run_id == run_id


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_run_id():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.run_id is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("state", [ModelVersionState.ready, ModelVersionState.pending, ModelVersionState.failed])
def test_model_version_with_state(state):
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version, state=state)

    assert model_version.status == ModelVersionStatus(state)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("state", [ModelVersionState.ready, ModelVersionState.pending, ModelVersionState.failed])
def test_model_version_with_state_message(state):
    name = rand_str()
    version = rand_int()

    state_message = rand_str()

    model_version = ModelVersion(name, version, state=state, state_message=state_message)

    assert model_version.status == ModelVersionStatus(state, state_message)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_state():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert model_version.status == ModelVersionStatus(ModelVersionState.pending)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_with_tags():
    name = rand_str()
    version = rand_int()

    key = rand_str()
    value = rand_str()
    tags = {key: value}

    model_version = ModelVersion(name, version, tags=tags)

    assert model_version.tags
    assert key in model_version.tags
    assert model_version.tags[key] == ModelVersionTag(key=key, value=value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_without_tags():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert not model_version.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_tuple():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion.make((name, version))

    assert model_version.name == name
    assert model_version.version == version


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_dict():
    dct = {
        "name": rand_str(),
        "version": rand_int(),
    }

    model_version = ModelVersion.make(dct)

    assert model_version.name == dct["name"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_dict_with_creation_timestamp():
    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "creation_timestamp": now(),
    }

    model_version = ModelVersion.make(dct)

    assert model_version.created_time == dct["creation_timestamp"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_dict_with_last_updated_timestamp():
    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "last_updated_timestamp": now(),
    }

    model_version = ModelVersion.make(dct)

    assert model_version.updated_time == dct["last_updated_timestamp"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "stage", [ModelVersionStage.unknown, ModelVersionStage.prod, ModelVersionStage.test, ModelVersionStage.archived]
)
def test_model_version_make_dict_with_stage(stage):
    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "current_stage": stage.value,
    }

    model_version = ModelVersion.make(dct)

    assert model_version.stage == stage

    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "stage": stage.value,
    }

    model_version = ModelVersion.make(dct)

    assert model_version.stage == stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_dict_with_description():
    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "description": rand_str(),
    }

    model_version = ModelVersion.make(dct)

    assert model_version.description == dct["description"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_dict_with_source():
    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "source": rand_str(),
    }

    model_version = ModelVersion.make(dct)

    assert model_version.source == dct["source"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_dict_with_run_id():
    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "run_id": rand_str(),
    }

    model_version = ModelVersion.make(dct)

    assert model_version.run_id == dct["run_id"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("state", [ModelVersionState.ready, ModelVersionState.pending, ModelVersionState.failed])
def test_model_version_make_dict_with_state(state):
    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "status": state,
    }

    model_version = ModelVersion.make(dct)

    assert model_version.status == ModelVersionStatus(state)

    dct = {
        "name": rand_str(),
        "version": rand_int(),
        "state": state,
    }

    model_version = ModelVersion.make(dct)

    assert model_version.status == ModelVersionStatus(state)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize("state", [ModelVersionState.ready, ModelVersionState.pending, ModelVersionState.failed])
def test_model_version_make_dict_with_state_message(state):
    dct = {"name": rand_str(), "version": rand_int(), "status": state, "status_message": rand_str()}

    model_version = ModelVersion.make(dct)

    assert model_version.status == ModelVersionStatus(state, dct["status_message"])

    dct = {"name": rand_str(), "version": rand_int(), "state": state, "state_message": rand_str()}

    model_version = ModelVersion.make(dct)

    assert model_version.status == ModelVersionStatus(state, dct["state_message"])


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_make_dict_with_tags():
    key = rand_str()
    value = rand_str()

    dct = {"id": rand_int(), "version": rand_int(), "name": rand_str(), "tags": {key: value}}

    model_version = ModelVersion.make(dct)

    assert model_version.tags
    assert key in model_version.tags
    assert model_version.tags[key] == ModelVersionTag(key=key, value=value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_str():
    name = rand_str()
    version = rand_int()

    model_version = ModelVersion(name, version)

    assert str(model_version)
    assert str(model_version) == "{name} v{version}".format(name=name, version=version)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_eq():
    name1 = rand_str()
    name2 = rand_str()

    version1 = rand_int()
    version2 = rand_int()

    assert ModelVersion(name1, version1) == ModelVersion(name1, version1)
    assert ModelVersion(name1, version1) != ModelVersion(name1, version2)
    assert ModelVersion(name1, version1) != ModelVersion(name2, version1)
    assert ModelVersion(name1, version1) != ModelVersion(name2, version2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_version_in():
    name1 = rand_str()
    name2 = rand_str()

    version1 = rand_int()
    version2 = rand_int()

    model1 = ModelVersion(name1, version1)
    model2 = ModelVersion(name2, version2)

    lst = ModelVersion.from_list([model1])

    assert model1 in lst
    assert model2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "stage", [ModelVersionStage.unknown, ModelVersionStage.prod, ModelVersionStage.test, ModelVersionStage.archived]
)
@pytest.mark.parametrize(
    "other_stage",
    [ModelVersionStage.unknown, ModelVersionStage.prod, ModelVersionStage.test, ModelVersionStage.archived],
)
def test_model_version_in_by_stage(stage, other_stage):
    name1 = rand_str()

    version1 = rand_int()

    model1 = ModelVersion(name1, version1, stage=stage)

    lst = ModelVersion.from_list([model1])

    assert stage in lst

    if other_stage != stage:
        assert other_stage not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    "stage", [ModelVersionStage.unknown, ModelVersionStage.prod, ModelVersionStage.test, ModelVersionStage.archived]
)
@pytest.mark.parametrize(
    "other_stage",
    [ModelVersionStage.unknown, ModelVersionStage.prod, ModelVersionStage.test, ModelVersionStage.archived],
)
def test_model_version_get_item_by_stage(stage, other_stage):
    name1 = rand_str()

    version1 = rand_int()

    model1 = ModelVersion(name1, version1, stage=stage)

    lst = ModelVersion.from_list([model1])

    assert lst[stage].version == version1
    assert lst[stage].stage == stage

    if other_stage != stage:
        assert other_stage not in lst

        with pytest.raises(KeyError):
            lst[other_stage]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model():
    name = rand_str()

    model = Model(name)

    assert model.name == name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_with_creation_timestamp():
    name = rand_str()
    created_time = now()

    model = Model(name, creation_timestamp=created_time)

    assert model.created_time == created_time


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_without_creation_timestamp():
    name = rand_str()

    model = Model(name)

    assert model.created_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_with_last_updated_timestamp():
    name = rand_str()
    updated_time = now()

    model = Model(name, last_updated_timestamp=updated_time)

    assert model.updated_time == updated_time


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_without_last_updated_timestamp():
    name = rand_str()

    model = Model(name)

    assert model.updated_time is None


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_with_description():
    name = rand_str()
    description = rand_str()

    model = Model(name, description=description)

    assert model.description == description


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_without_description():
    name = rand_str()

    model = Model(name)

    assert model.description == ""


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_with_versions():
    name = rand_str()

    version = ModelVersion(name=name, version=rand_int(), stage=ModelVersionStage.prod)

    model = Model(name, versions=[version])

    assert model.versions
    assert ModelVersionStage.prod in model.versions
    assert model.versions[ModelVersionStage.prod] == version


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_with_tags():
    name = rand_str()

    key = rand_str()
    value = rand_str()
    tags = {key: value}

    model = Model(name, tags=tags)

    assert model.tags
    assert key in model.tags
    assert model.tags[key] == ModelTag(key=key, value=value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_without_tags():
    name = rand_str()

    model = Model(name)

    assert not model.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_without_versions():
    name = rand_str()

    model = Model(name)

    assert not model.versions


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_make_str():
    name = rand_str()

    model = Model.make(name)

    assert model.name == name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_make_dict():
    dct = {"name": rand_str()}

    model = Model.make(dct)

    assert model.name == dct["name"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_make_dict_with_creation_timestamp():
    dct = {
        "name": rand_str(),
        "creation_timestamp": now(),
    }

    model = Model.make(dct)

    assert model.created_time == dct["creation_timestamp"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_make_dict_with_last_updated_timestamp():
    dct = {
        "name": rand_str(),
        "last_updated_timestamp": now(),
    }

    model = Model.make(dct)

    assert model.updated_time == dct["last_updated_timestamp"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_make_dict_with_description():
    dct = {
        "name": rand_str(),
        "description": rand_str(),
    }

    model = Model.make(dct)

    assert model.description == dct["description"]


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_make_dict_with_versions():
    name = rand_str()
    version = rand_int()
    dct = {"name": name, "latest_versions": [{"name": name, "version": version}]}

    model = Model.make(dct)

    assert model.versions
    assert ModelVersionStage.unknown in model.versions
    assert model.versions[ModelVersionStage.unknown]
    assert model.versions[ModelVersionStage.unknown].version == version


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_make_dict_with_tags():
    key = rand_str()
    value = rand_str()

    dct = {"id": rand_int(), "name": rand_str(), "tags": {key: value}}

    model = Model.make(dct)

    assert model.tags
    assert key in model.tags
    assert model.tags[key] == ModelTag(key=key, value=value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_str():
    name = rand_str()

    model = Model(name)

    assert str(model)
    assert str(model) == name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_eq():
    name1 = rand_str()
    name2 = rand_str()

    assert Model(name1) == Model(name1)
    assert Model(name1) != Model(name2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_eq_name():
    name1 = rand_str()
    name2 = rand_str()

    assert Model(name1) == name1
    assert Model(name1) != name2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_in():
    name1 = rand_str()
    name2 = rand_str()

    model1 = Model(name1)
    model2 = Model(name2)

    lst = Model.from_list([model1])

    assert model1 in lst
    assert model2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_in_by_name():
    name1 = rand_str()
    name2 = rand_str()

    model1 = Model(name1)

    lst = Model.from_list([model1])

    assert name1 in lst
    assert name2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_model_get_item_by_name():
    name1 = rand_str()
    name2 = rand_str()

    model1 = Model(name1)

    lst = Model.from_list([model1])

    assert lst[name1] == model1

    with pytest.raises(KeyError):
        lst[name2]
