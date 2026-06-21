import pytest
from health_data_guard import HealthDataGuard, PolicyStatus

def test_load_policy():
    guard = HealthDataGuard()
    guard.load_policy('test_policy')
    assert 'test_policy' in guard.policies

def test_enforce_policy_loaded():
    guard = HealthDataGuard()
    guard.load_policy('test_policy')
    assert guard.enforce_policy('test_policy')

def test_enforce_policy_not_loaded():
    guard = HealthDataGuard()
    assert not guard.enforce_policy('test_policy')

def test_health_check_all_loaded():
    guard = HealthDataGuard()
    guard.load_policy('test_policy1')
    guard.load_policy('test_policy2')
    assert guard.health_check()

def test_health_check_not_all_loaded():
    guard = HealthDataGuard()
    guard.load_policy('test_policy1')
    guard.policies['test_policy1'].status = PolicyStatus.NOT_LOADED
    assert not guard.health_check()
