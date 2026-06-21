import json
import csv
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

class UserRole(Enum):
    COMPLIANCE_OFFICER = 1
    ADMIN = 2

@dataclass
class AuditLog:
    timestamp: str
    policy_id: str
    data_source: str
    action_taken: str

class HealthDataGuard:
    def __init__(self):
        self.audit_logs = []
        self.user_roles = {}

    def add_audit_log(self, log: AuditLog):
        self.audit_logs.append(log)

    def add_user_role(self, user_id: str, role: UserRole):
        self.user_roles[user_id] = role

    def export_audit_logs(self, user_id: str, format: str) -> str:
        if self.user_roles.get(user_id) != UserRole.COMPLIANCE_OFFICER:
            raise PermissionError("User does not have permission to export audit logs")

        if format not in ["csv", "json"]:
            raise ValueError("Invalid format")

        logs = [log.__dict__ for log in self.audit_logs]

        if format == "csv":
            csv_data = "timestamp,policy_id,data_source,action_taken\n"
            for log in logs:
                csv_data += f"{log['timestamp']},{log['policy_id']},{log['data_source']},{log['action_taken']}\n"
            return csv_data
        elif format == "json":
            return json.dumps(logs, indent=4)

    def get_audit_logs(self, user_id: str) -> List[AuditLog]:
        if self.user_roles.get(user_id) != UserRole.COMPLIANCE_OFFICER:
            raise PermissionError("User does not have permission to view audit logs")
        return self.audit_logs
