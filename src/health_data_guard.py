import json
from dataclasses import dataclass
from typing import Dict

@dataclass
class EncryptedData:
    data: str
    key: str

class HealthDataGuard:
    def __init__(self):
        self.compliance_regulations = {
            "state1": "regulation1",
            "state2": "regulation2"
        }

    def encrypt_data(self, data: str, key: str) -> EncryptedData:
        encrypted_data = json.dumps({"data": data, "key": key})
        return EncryptedData(encrypted_data, key)

    def verify_compliance(self, state: str) -> bool:
        return state in self.compliance_regulations

    def decrypt_data(self, encrypted_data: EncryptedData) -> str:
        try:
            decrypted_data = json.loads(encrypted_data.data)
            return decrypted_data["data"]
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON")
