import pytest
from health_data_guard import HealthDataGuard, AuditLog, UserRole

def test_export_audit_logs_csv():
    guard = HealthDataGuard()
    guard.add_user_role("user1", UserRole.COMPLIANCE_OFFICER)
    guard.add_audit_log(AuditLog("2022-01-01 12:00:00", "policy1", "data_source1", "action_taken1"))
    csv_data = guard.export_audit_logs("user1", "csv")
    assert csv_data == "timestamp,policy_id,data_source,action_taken\n2022-01-01 12:00:00,policy1,data_source1,action_taken1\n"

def test_export_audit_logs_json():
    guard = HealthDataGuard()
    guard.add_user_role("user1", UserRole.COMPLIANCE_OFFICER)
    guard.add_audit_log(AuditLog("2022-01-01 12:00:00", "policy1", "data_source1", "action_taken1"))
    json_data = guard.export_audit_logs("user1", "json")
    assert json_data == '[\n    {\n        "timestamp": "2022-01-01 12:00:00",\n        "policy_id": "policy1",\n        "data_source": "data_source1",\n        "action_taken": "action_taken1"\n    }\n]'

def test_export_audit_logs_invalid_format():
    guard = HealthDataGuard()
    guard.add_user_role("user1", UserRole.COMPLIANCE_OFFICER)
    with pytest.raises(ValueError):
        guard.export_audit_logs("user1", "invalid_format")

def test_export_audit_logs_permission_denied():
    guard = HealthDataGuard()
    guard.add_user_role("user1", UserRole.ADMIN)
    with pytest.raises(PermissionError):
        guard.export_audit_logs("user1", "csv")

def test_get_audit_logs_permission_denied():
    guard = HealthDataGuard()
    guard.add_user_role("user1", UserRole.ADMIN)
    with pytest.raises(PermissionError):
        guard.get_audit_logs("user1")
