
import uuid
import pytest
import unittest

from mlflow_client import MLflowApiClient

api_url="http://localhost:5001"
client = MLflowApiClient(api_url)

def create_exp_name():
    return "pyTestExp_"+ uuid.uuid4().hex

class ApiTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_experiment(self):
        exp_name = create_exp_name()
        exp_id = client.create_experiment(exp_name)

        rsp = client.get_experiment(exp_id)
        print("Experiment:",rsp)
        exp = rsp['experiment']
        assert exp['experiment_id'] == exp_id
        assert exp['name'] == exp_name


    def test_get_or_create_experiment_id(self):
        exp_name = create_exp_name()
        exp_id = client.get_or_create_experiment_id(exp_name)
        exp_id2 = client.get_or_create_experiment_id(exp_name)
        assert exp_id == exp_id2
