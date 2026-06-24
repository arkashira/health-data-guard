import json
from dataclasses import dataclass
from enum import Enum
from typing import List

class PolicyStatus(Enum):
    LOADED = 1
    NOT_LOADED = 2

@dataclass
class Policy:
    id: int
    name: str
    status: PolicyStatus

class HealthDataGuard:
    def __init__(self):
        self.policies = []

    def load_policies(self, policies: List[Policy]):
        self.policies = policies

    def enforce_policy(self, policy_id: int):
        for policy in self.policies:
            if policy.id == policy_id:
                return policy.status == PolicyStatus.LOADED
        return False

    def health_check(self):
        return all(policy.status == PolicyStatus.LOADED for policy in self.policies)

    def get_policies(self):
        return self.policies
