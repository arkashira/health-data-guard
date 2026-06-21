import argparse
import json
from dataclasses import dataclass
from enum import Enum

class PolicyStatus(Enum):
    LOADED = 1
    NOT_LOADED = 2

@dataclass
class Policy:
    name: str
    status: PolicyStatus

class HealthDataGuard:
    def __init__(self):
        self.policies = {}

    def load_policy(self, name: str):
        self.policies[name] = Policy(name, PolicyStatus.LOADED)

    def enforce_policy(self, name: str):
        if name in self.policies:
            return self.policies[name].status == PolicyStatus.LOADED
        return False

    def health_check(self):
        return all(policy.status == PolicyStatus.LOADED for policy in self.policies.values())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load-policy', help='Load a policy')
    args = parser.parse_args()

    guard = HealthDataGuard()
    if args.load_policy:
        guard.load_policy(args.load_policy)

    if guard.health_check():
        print('OK')
    else:
        print('NOT OK')

if __name__ == '__main__':
    main()
