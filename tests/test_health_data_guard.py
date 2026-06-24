import pytest
from src.health_data_guard import HealthDataGuard, Policy, PolicyStatus

@pytest.fixture
def health_data_guard():
    return HealthDataGuard()

def test_enforce_policy_loaded(health_data_guard):
    policy = Policy(1, "Test Policy", PolicyStatus.LOADED)
    health_data_guard.load_policies([policy])
    assert health_data_guard.enforce_policy(1)

def test_enforce_policy_not_loaded(health_data_guard):
    policy = Policy(1, "Test Policy", PolicyStatus.NOT_LOADED)
    health_data_guard.load_policies([policy])
    assert not health_data_guard.enforce_policy(1)

def test_enforce_policy_not_found(health_data_guard):
    assert not health_data_guard.enforce_policy(1)

def test_health_check_all_loaded(health_data_guard):
    policy1 = Policy(1, "Test Policy 1", PolicyStatus.LOADED)
    policy2 = Policy(2, "Test Policy 2", PolicyStatus.LOADED)
    health_data_guard.load_policies([policy1, policy2])
    assert health_data_guard.health_check()

def test_health_check_not_all_loaded(health_data_guard):
    policy1 = Policy(1, "Test Policy 1", PolicyStatus.LOADED)
    policy2 = Policy(2, "Test Policy 2", PolicyStatus.NOT_LOADED)
    health_data_guard.load_policies([policy1, policy2])
    assert not health_data_guard.health_check()

def test_get_policies(health_data_guard):
    policy1 = Policy(1, "Test Policy 1", PolicyStatus.LOADED)
    policy2 = Policy(2, "Test Policy 2", PolicyStatus.NOT_LOADED)
    health_data_guard.load_policies([policy1, policy2])
    assert len(health_data_guard.get_policies()) == 2
