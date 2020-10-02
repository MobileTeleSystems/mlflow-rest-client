import logging
import pytest

from mlflow_client.experiment import Experiment, ExperimentStage, ExperimentTag
from .conftest import DEFAULT_TIMEOUT, rand_str, rand_int

log = logging.getLogger(__name__)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment():
    id = rand_int()
    name = rand_str()

    experiment = Experiment(id, name)

    assert experiment.id == id
    assert experiment.name == name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_with_artifact_location():
    id = rand_int()
    name = rand_str()
    artifact_location = rand_str()

    experiment = Experiment(id, name, artifact_location=artifact_location)

    assert experiment.artifact_location == artifact_location


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_without_artifact_location():
    id = rand_int()
    name = rand_str()

    experiment = Experiment(id, name)

    assert experiment.artifact_location == ''


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    'stage', [
        ExperimentStage.active,
        ExperimentStage.deleted
    ]
)
def test_experiment_with_stage(stage):
    id = rand_int()
    name = rand_str()

    experiment = Experiment(id, name, stage=stage.value)
    assert experiment.stage == stage

    experiment = Experiment(id, name, stage=stage)
    assert experiment.stage == stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_without_stage():
    id = rand_int()
    name = rand_str()

    experiment = Experiment(id, name)

    assert experiment.stage == ExperimentStage.active


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_with_tags():
    id = rand_int()
    name = rand_str()

    key = rand_str()
    value = rand_str()
    tags = {
        key: value
    }

    experiment = Experiment(id, name, tags=tags)

    assert experiment.tags
    assert key in experiment.tags
    assert experiment.tags[key] == ExperimentTag(key=key, value=value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_without_tags():
    id = rand_int()
    name = rand_str()

    experiment = Experiment(id, name)

    assert not experiment.tags


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_make_tuple():
    id = rand_int()
    name = rand_str()

    experiment = Experiment.make((id, name))

    assert experiment.id == id
    assert experiment.name == name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_make_dict():
    dct = {
        'id': rand_int(),
        'name': rand_str()
    }

    experiment = Experiment.make(dct)

    assert experiment.id == dct['id']
    assert experiment.name == dct['name']

    dct = {
        'experiment_id': rand_int(),
        'name': rand_str()
    }

    experiment = Experiment.make(dct)

    assert experiment.id == dct['experiment_id']
    assert experiment.name == dct['name']


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_make_dict_with_artifact_location():
    dct = {
        'id': rand_int(),
        'name': rand_str(),
        'artifact_location': rand_str(),
    }

    experiment = Experiment.make(dct)

    assert experiment.artifact_location == dct['artifact_location']


@pytest.mark.timeout(DEFAULT_TIMEOUT)
@pytest.mark.parametrize(
    'stage', [
        ExperimentStage.active,
        ExperimentStage.deleted
    ]
)
def test_experiment_make_dict_with_stage(stage):
    dct = {
        'id': rand_int(),
        'name': rand_str(),
        'lifecycle_stage': stage.value,
    }

    experiment = Experiment.make(dct)

    assert experiment.stage == stage

    dct = {
        'id': rand_int(),
        'name': rand_str(),
        'stage': stage.value,
    }

    experiment = Experiment.make(dct)

    assert experiment.stage == stage


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_make_dict_with_tags():
    key = rand_str()
    value = rand_str()

    dct = {
        'id': rand_int(),
        'name': rand_str(),
        'tags': {
            key: value
        }
    }

    experiment = Experiment.make(dct)

    assert experiment.tags
    assert key in experiment.tags
    assert experiment.tags[key] == ExperimentTag(key=key, value=value)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_str():
    id = rand_int()
    name = rand_str()

    experiment = Experiment(id, name)

    assert str(experiment)
    assert str(experiment) == name


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_int():
    id = rand_int()
    name = rand_str()

    experiment = Experiment(id, name)

    assert int(experiment)
    assert int(experiment) == id


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_eq():
    id1 = rand_int()
    id2 = rand_int()

    name1 = rand_str()
    name2 = rand_str()

    assert Experiment(id1, name1) == Experiment(id1, name1)
    assert Experiment(id1, name1) != Experiment(id1, name2)

    assert Experiment(id1, name1) != Experiment(id2, name2)
    assert Experiment(id1, name1) != Experiment(id2, name2)


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_eq_name():
    id1 = rand_int()

    name1 = rand_str()
    name2 = rand_str()

    assert Experiment(id1, name1) == name1
    assert Experiment(id1, name1) != name2


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_in():
    id1 = rand_int()
    id2 = rand_int()

    name1 = rand_str()
    name2 = rand_str()

    experiment1 = Experiment(id1, name1)
    experiment2 = Experiment(id2, name2)

    lst = Experiment.from_list([
        experiment1
    ])

    assert experiment1 in lst
    assert experiment2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_in_by_name():
    id1 = rand_int()

    name1 = rand_str()
    name2 = rand_str()

    experiment1 = Experiment(id1, name1)

    lst = Experiment.from_list([
        experiment1
    ])

    assert name1 in lst
    assert name2 not in lst


@pytest.mark.timeout(DEFAULT_TIMEOUT)
def test_experiment_get_item_by_name():
    id1 = rand_int()

    name1 = rand_str()
    name2 = rand_str()

    experiment1 = Experiment(id1, name1)

    lst = Experiment.from_list([
        experiment1
    ])

    assert lst[name1] == experiment1

    with pytest.raises(KeyError):
        lst[name2]
