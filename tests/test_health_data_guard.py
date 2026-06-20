import json
from health_data_guard import HealthDataGuard, EncryptedData

def test_encrypt_data():
    health_data_guard = HealthDataGuard()
    data = "sensitive_data"
    key = "secret_key"
    encrypted_data = health_data_guard.encrypt_data(data, key)
    assert encrypted_data.data == json.dumps({"data": data, "key": key})
    assert encrypted_data.key == key

def test_verify_compliance():
    health_data_guard = HealthDataGuard()
    state = "state1"
    assert health_data_guard.verify_compliance(state) == True
    state = "unknown_state"
    assert health_data_guard.verify_compliance(state) == False

def test_decrypt_data():
    health_data_guard = HealthDataGuard()
    data = "sensitive_data"
    key = "secret_key"
    encrypted_data = health_data_guard.encrypt_data(data, key)
    decrypted_data = health_data_guard.decrypt_data(encrypted_data)
    assert decrypted_data == data

def test_decrypt_data_invalid_json():
    health_data_guard = HealthDataGuard()
    encrypted_data = EncryptedData("invalid_json", "key")
    try:
        health_data_guard.decrypt_data(encrypted_data)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
